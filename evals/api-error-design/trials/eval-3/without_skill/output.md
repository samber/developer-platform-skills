# Localized error design for the Craftpoint API

## Recommendation: translate the text, never the code

Do not translate `INVALID_SKU` into `REFERENCE_INVALIDE`. I'd push back on that part of the product ask. Integrators branch on the identifier, so it is part of the API contract:

- **Code breaks per locale.** A `switch (err.code)` written against `INVALID_SKU` would stop working the moment the account locale changes to `fr`. Each locale would need its own enum.
- **Shared tooling breaks.** Logs, alerts, retry rules, SDK enums and support macros all key on the code. A French and a German integrator at the same customer could no longer compare notes.
- **Every new locale multiplies the contract.** Each added language means one more set of identifiers to freeze, document and never rename.
- **Existing clients break.** Everything integrated today matches on `MIN_QTY_RULE_VIOLATED`.

What product probably wants is that a French developer reads a French error without needing a dictionary. The design below delivers that:

| Field | Localized? | Purpose |
|---|---|---|
| `code` | No, frozen | Machine branching, logs, support |
| `type` | No, frozen URI | Stable link to docs. The docs page itself is served in the reader's locale |
| `title` | Yes | Short human label |
| `detail` / `errors[].detail` | Yes | Full sentence for the failure |
| `errors[].params` | No | Raw machine values (`min`, `actual`) so clients can render their own text |

If product still insists on a translated identifier, add an optional, purely informational `code_label` (`"Référence invalide"`). It would never be used for branching and would be documented that way.

## Response shape

Adopt RFC 9457 `application/problem+json` and keep the existing code as an extension member. Today's bare string carries no field, no values and no request ID.

| Member | Type | Notes |
|---|---|---|
| `type` | URI | Stable per code |
| `title` | string | Localized |
| `status` | int | HTTP status |
| `code` | string | Existing identifier, unchanged |
| `detail` | string | Localized summary |
| `locale` | string | Locale actually used, after fallback |
| `request_id` | string | For support |
| `errors[]` | array | One entry per violation |
| `errors[].code` | string | Stable |
| `errors[].pointer` | string | JSON Pointer to the offending field, e.g. `/quantity` |
| `errors[].detail` | string | Localized |
| `errors[].params` | object | Raw, unlocalized values |

Always send the `Content-Language` header and `Vary: Accept-Language`.

## Locale resolution

1. An explicit `Accept-Language` header on the request, if it matches a supported locale. This matters for server-to-server calls made with a shared service account.
2. Otherwise, the account locale.
3. Otherwise, `en`.

Regional variants fall back to their base language (`fr-CA` → `fr`), then to `en`. Supported at launch: `en`, `fr`, `de`. Product should confirm precedence 1 over 2. The ask only mentions the account locale.

## Message catalog

- Key messages by `code`, written in ICU MessageFormat, with `en` as the source of truth.
- Pass `params` unlocalized in the JSON, but format numbers inside `detail` for the locale (`1.000` in `de`, `1 000` in `fr`).
- Keep product terms such as "SKU" untranslated unless the glossary says otherwise.
- CI gates:
  - Every `code` has a message in every supported locale.
  - Placeholders match across locales.
  - A contract test asserts `code`, `type`, `status` and `params` are byte-identical across all locales for the same failing request.
- A missing translation falls back to `en` and sets `locale: "en"` honestly, rather than failing.

## Rewritten example

Request:

```http
POST /v1/stock-moves
Accept-Language: fr
Content-Type: application/json

{ "sku": "CP-10442", "quantity": 0 }
```

(`sku` and any other fields are illustrative. Only `quantity=0` came from your case.)

**Before** (today, locale-blind):

```http
HTTP/1.1 422
MIN_QTY_RULE_VIOLATED
```

**After**, French account:

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json
Content-Language: fr
Vary: Accept-Language

{
  "type": "https://docs.craftpoint.com/errors/min-qty-rule-violated",
  "title": "Quantité minimale non respectée",
  "status": 422,
  "code": "MIN_QTY_RULE_VIOLATED",
  "detail": "Le mouvement de stock contient 1 erreur. Corrigez le champ indiqué et renvoyez la requête.",
  "locale": "fr",
  "request_id": "req_8f3a1c2e",
  "errors": [
    {
      "code": "MIN_QTY_RULE_VIOLATED",
      "pointer": "/quantity",
      "detail": "La quantité doit être d'au moins 1. Valeur reçue : 0.",
      "params": { "min": 1, "actual": 0 }
    }
  ]
}
```

**After**, German account. Only the text changes:

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json
Content-Language: de
Vary: Accept-Language

{
  "type": "https://docs.craftpoint.com/errors/min-qty-rule-violated",
  "title": "Mindestmenge unterschritten",
  "status": 422,
  "code": "MIN_QTY_RULE_VIOLATED",
  "detail": "Die Lagerbewegung enthält 1 Fehler. Korrigieren Sie das angegebene Feld und senden Sie die Anfrage erneut.",
  "locale": "de",
  "request_id": "req_8f3a1c2e",
  "errors": [
    {
      "code": "MIN_QTY_RULE_VIOLATED",
      "pointer": "/quantity",
      "detail": "Die Menge muss mindestens 1 betragen. Empfangener Wert: 0.",
      "params": { "min": 1, "actual": 0 }
    }
  ]
}
```

The same pattern covers the other example: `INVALID_SKU` stays `INVALID_SKU`, with `title: "Référence invalide"` for `fr` and `"Ungültige Artikelnummer"` for `de`.

## Migration

- Existing clients that read only `code` keep working, because `code` is unchanged.
- Document `message`-style free text as unstable and not for parsing. Localization makes that explicit.
- Ship the docs error pages in `fr` and `de`, reachable from the same `type` URI via `Accept-Language`.

## Open questions

1. Does product accept codes staying English? If not, `code_label` is the fallback.
2. Is 422 right for validation failures here, or does the API return 400 today? Match the current status unless there is a reason to change it.
3. Is `Accept-Language` overriding the account locale acceptable?