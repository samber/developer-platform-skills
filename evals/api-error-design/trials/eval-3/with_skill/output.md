# Localized error design for the Craftpoint API

I read the skill and its four references. I made the calls below from your brief, so please check the items under "Open questions" before shipping.

## Verdict on the product ask

- **Translate:** `title`, `detail`, and each `errors[].message`.
- **Never translate:** `code`, `errors[].code`, `type`, field names, and the numbers in `constraints`.
- **Reject `INVALID_SKU` → `REFERENCE_INVALIDE`.** The skill lists "a translated or repurposed `code` value" as an audit failure mode, and it breaks the stability contract.
- **What breaks:**
  - Client code branches on `code`, so a French account's `switch` would never match.
  - A German integrator's logs and tickets would carry codes we can't search in one catalog.
  - A locale change on an account would silently change behaviour.
- **What the product ask really wants:** French and German integrators can read the error without an English dictionary. Translated prose covers that. Identifiers only need to be stable and documented.
- **What to tell Product:** every identifier is a stable English token, and every sentence is localized.

## Taxonomy choice

Retrofit, third-party integrators, REST-only (assumed). That gives the **code/subcode catalog**: a top-level `code` pinned to one HTTP status, with specific reasons in `errors[].code`.

## Localization spec

1. **Locale resolution, in order:**
   1. `Accept-Language` request header, matched against the supported set `en`, `fr`, `de`.
   2. The account's default locale setting.
   3. `en`.
2. **Response headers:** always send `Content-Language: <resolved>` and `Vary: Accept-Language`. Otherwise caches and proxies serve French text to German callers.
3. **Localized members:**
   - `title`
   - `detail`
   - `errors[].message`
4. **Locale-invariant members:**
   - `type`
   - `status`
   - `code`
   - `errors[].code`
   - `errors[].field`
   - `constraints`
   - `value_provided`
   - `retryable`
   - `request_id`

   `field` is the request parameter name (`quantity`), not UI copy.
5. **Stability statement for the catalog:** "`code` and `errors[].code` are stable and safe to branch on. `title`, `detail`, and `message` are localized, not contractual, and may be reworded at any time."
6. **Message templates:**
   - Each catalog code owns one template per locale, keyed by `errors[].code`.
   - Parameters are `field`, `value_provided`, and `constraints.*`.
   - Use ICU MessageFormat so plurals work in all three languages.
   - Emit numbers as JSON numbers. Don't format them inside prose with locale separators, which avoids `1,5` vs `1.5` ambiguity.
7. **Fallback:** if a template is missing for the locale, return the English text and `Content-Language: en`. Never return an empty or mixed-language message.
8. **Docs link:** `documentation_url` points at the English code's anchor, for example `https://docs.craftpoint.example/errors#MIN_QTY_RULE_VIOLATED`. The anchor is the stable code. The page may be locale-prefixed.
9. **Gate (CI):**
   - Every catalog code and subcode must have an `en`, `fr`, and `de` template.
   - Every template must use only the parameters its code declares.
   - A response containing an uncatalogued code fails the build.
10. **Support:** French and German tickets are traceable through `request_id` and the English `code`, so support doesn't need to read the prose.

## Retrofit: mapping from the current surface

Today the body is just `MIN_QTY_RULE_VIOLATED`. Hyrum's Law applies, so I treat that string as contract. I never rename or drop it.

| Shipped identity | New home | Rule |
|---|---|---|
| `MIN_QTY_RULE_VIOLATED` | `errors[].code` (kept verbatim) | Never renamed. |
| `INVALID_SKU` | stays `INVALID_SKU` in `en`, `fr`, and `de` | Identifier never localized. |
| (new) | `code: VALIDATION_ERROR` | Added category, pinned to the HTTP status. |

## Example rewrite: `POST /v1/stock-moves` with `quantity=0` (minimum 1)

**Request**

```http
POST /v1/stock-moves
Accept-Language: fr
Content-Type: application/json

{ "sku": "BOLT-M8-50", "quantity": 0 }
```

**Before (every locale)**

```
MIN_QTY_RULE_VIOLATED
```

It has no field, no value, no constraint, no status guidance, and no request ID.

**After, French account**

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json
Content-Language: fr
Vary: Accept-Language
X-Request-ID: req_4f1a9c27

{
  "type": "https://api.craftpoint.example/errors/validation-error",
  "title": "Erreur de validation",
  "status": 422,
  "detail": "Un champ de la requête ne respecte pas une règle de validation.",
  "instance": "/v1/stock-moves",
  "code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "quantity",
      "code": "MIN_QTY_RULE_VIOLATED",
      "message": "quantity doit être supérieur ou égal à 1 ; reçu : 0. Indiquez un nombre entier supérieur ou égal à 1.",
      "value_provided": 0,
      "constraints": { "min": 1 }
    }
  ],
  "retryable": false,
  "documentation_url": "https://docs.craftpoint.example/errors#MIN_QTY_RULE_VIOLATED",
  "request_id": "req_4f1a9c27"
}
```

**After, German account (only the localized members differ)**

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json
Content-Language: de
Vary: Accept-Language
X-Request-ID: req_4f1a9c28

{
  "type": "https://api.craftpoint.example/errors/validation-error",
  "title": "Validierungsfehler",
  "status": 422,
  "detail": "Ein Feld der Anfrage verletzt eine Validierungsregel.",
  "instance": "/v1/stock-moves",
  "code": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "quantity",
      "code": "MIN_QTY_RULE_VIOLATED",
      "message": "quantity muss mindestens 1 betragen; erhalten: 0. Geben Sie eine ganze Zahl ab 1 an.",
      "value_provided": 0,
      "constraints": { "min": 1 }
    }
  ],
  "retryable": false,
  "documentation_url": "https://docs.craftpoint.example/errors#MIN_QTY_RULE_VIOLATED",
  "request_id": "req_4f1a9c28"
}
```

The `en` variant is identical, with `title: "Validation Error"` and `message: "quantity must be at least 1; received 0. Send a whole number of 1 or more."`.

Why this is right:
- **Status:** 422, because the JSON is well-formed and the value violates a business minimum. 400 is for malformed requests.
- **Actionable:** each message names the field, the received value, and the constraint, in neutral corrective wording ("Indiquez…", "Geben Sie… an").
- **Retry:** `retryable: false`, because repeating the request unchanged fails identically.
- **Machine path:** a client branches on `errors[].code == "MIN_QTY_RULE_VIOLATED"` and reads `constraints.min`. It never parses prose.
- **Support path:** `request_id` is in both the header and the body.

## Catalog entry (published page)

```markdown
## MIN_QTY_RULE_VIOLATED (HTTP 422, under VALIDATION_ERROR) {#MIN_QTY_RULE_VIOLATED}

A quantity is below the minimum allowed for the operation. `errors[].constraints.min`
holds the minimum. Not retryable: send a quantity at or above the minimum.
Message safe to show end users: yes. Localized: en, fr, de.
```

## OpenAPI

Under `POST /v1/stock-moves` → `"422"`, add a named example `min_qty_rule_violated` using the `en` payload above. Document `Content-Language` and `Vary` as response headers. Generate the catalog page and examples from the spec so they can't drift.

## Open questions (please answer)

1. **Status today:** what status does the bare `MIN_QTY_RULE_VIOLATED` response return now? If it's 400 and clients branch on it, keep 400 until a version boundary instead of moving to 422.
2. **Top-level `code`:** do any clients read `MIN_QTY_RULE_VIOLATED` from the top level? If yes, also emit it there during a deprecation window (via `api-versioning-policy`) while `VALIDATION_ERROR` takes over.
3. **Locale source:** is "customer's locale" an account setting, or should the header always win? I assumed header first, account second.
4. **Other surfaces:** is the API REST-only? A gRPC or GraphQL surface changes the taxonomy rung and the envelope.
5. **Translation ownership:** who reviews the `fr` and `de` templates? The CI gate checks coverage, not translation quality.