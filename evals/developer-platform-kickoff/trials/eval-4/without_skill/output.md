**Verdict: it's breaking, so don't ship it as a straight rename.** I haven't reviewed your API. It isn't in this repo and I wasn't given the spec. The verdict comes from the definition of a breaking change, not from your code. The "just a rename" camp is wrong, and a document would settle it (see step 1).

## Why it's breaking

A change is breaking if a correct, existing client can fail or behave differently after it. Renaming or removing a field does that.

- **Requests:** an integrator sending `customer_ref` gets a 400. Worse, if your server ignores unknown fields, the value is dropped silently and the write succeeds without a counterparty. In a ledger API, that failure is the worst outcome.
- **Responses:** clients reading `customer_ref` get null or undefined. Strictly typed or generated clients can fail to deserialize at all.
- **The two dropped fields:** "nobody should be reading them" doesn't mean nobody is. After three years and about 400 integrators, assume someone does. You can't see response-field reads in your logs, so you can't prove otherwise.
- **Industry convention:** Google's API design guide (AIP-180), Stripe's versioning policy and SemVer-style API guidance all class field removal and renaming as breaking. Adding an optional field is the usual non-breaking change.

## What to do

1. **Write the policy first.** This is the document that ends the argument. Define "breaking" as removing or renaming a field, changing a type, tightening validation, changing enum values or changing semantics. Add a minimum deprecation window and the notice channels. Check whether your published docs or terms already promise something. If they say clients must ignore unknown fields, adding `counterparty_id` is safe. If they don't, even adding it carries some risk.
2. **Expand, then contract, for the rename.**
   - **Now:** accept both names in requests and return both in responses. Return a 400 if both are sent with different values.
   - **Announce:** mark `customer_ref` deprecated in the OpenAPI spec and docs. Add `Deprecation` and `Sunset` headers on the eight endpoints. Publish a changelog entry and email integrators directly.
   - **Measure:** count requests per API key that still send `customer_ref`. Contact the stragglers individually.
   - **Remove:** only after the sunset date and near-zero usage. For a financial API, 6 to 12 months is a defensible window. That's my judgment, not a standard.
3. **Treat the two dropped fields as higher risk, because you can't measure reads.**
   - Deprecate them in the docs and set a long sunset.
   - Don't replace them with `null`, because a type change is also breaking.
   - Ideally gate the removal behind a new API version or a per-key version pin. New keys get the slim response. Existing keys keep the old one until they opt in.
   - Ask your largest integrators directly.
4. **Add a CI gate so this argument doesn't recur.** Run a spec diff such as `oasdiff breaking` on the OpenAPI file for every PR. Failing the build on breaking changes makes the policy enforceable instead of a matter of opinion.

## Before committing

- **Versioning:** is there any mechanism today (URL, header, date pin)? If not, building one is probably the real prerequisite.
- **Specs and SDKs:** are the eight endpoints fully described in an OpenAPI spec? Do you ship SDKs that hard-code these field names?
- **Contracts:** do any enterprise integrators have SLAs or contract language about change notice?
- **Traffic data:** can you pull per-key request logs for the eight endpoints? That's how you'll find who's affected.

If you send me the OpenAPI spec for those eight endpoints, I can list the exact breaking surface and draft the deprecation notice and policy text.