Run `npx @stoplight/spectral-cli lint openapi.yaml` now. Spend the three hours making your OpenAPI file exactly true.

**Why this one**

Every missing item (SDKs, sandbox mock, Postman collection, docs accuracy) is generated from that file. "Mostly current" means your docs site tells 40 integrators things that are false, and any SDK built later would copy those errors. This is the only change that improves what integrators already use and also unblocks everything else.

**Steps (about 3h)**

1. **Lint, 20 min.** Run Spectral with the `spectral:oas` ruleset. Fix every error. Skip warnings for now.
2. **Find drift, 45 min.** Run Schemathesis against staging, never prod, with read-only calls first: `uvx schemathesis run openapi.yaml --url <staging-url> --method GET --checks all`. Every failure is a place where the spec and the API disagree.
3. **Decide which side is wrong, 60 min.** For each mismatch, fix the spec if the API behavior is what integrators rely on. Fix the API only if it is a plain bug. After two years, assume integrators depend on current behavior.
4. **Add examples, 40 min.** Give every endpoint one realistic request and one response example, error responses included. Do the 10 most-used endpoints first. Take that list from your access logs.
5. **Gate it in CI, 15 min.** Add the Spectral lint as a required check. Run Schemathesis nightly against staging. This keeps the spec accurate after today.
6. **Regenerate and publish the docs site, 10 min.**

**Done when**

- Spectral reports 0 errors.
- Schemathesis GET run on staging reports 0 failures.
- The top 10 endpoints have examples.
- CI blocks a spec that fails lint.

**Cut if time runs short:** step 4 beyond the top 5 endpoints. Never cut step 5, because without it the spec drifts again within months.

**If an integrator is blocked on something specific right now,** fix that first. Otherwise this is the best use of the three hours.

Next: run the Spectral command and count the errors. That count sets your pace for the rest.