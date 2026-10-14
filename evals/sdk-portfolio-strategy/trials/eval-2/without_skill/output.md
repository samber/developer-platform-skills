# Building the five Northwind Freight client libraries

**Recommendation:** generate the transport and model layer from a repaired OpenAPI spec using self-hosted tools. Hand-write the public surface customers touch. Fix spec drift before anything else.

I haven't seen your spec, API code, or customer usage data, so treat the estimates and tool notes below as starting points to check.

## 1. Where I disagree with "official means hand-written"

Customers don't object to generation. They object to code that is unidiomatic or hard to use: `ApiClientDefaultApi.getShipmentsUsingGET`, nested `Optional` wrappers, opaque errors, no pagination helper. Template choices cause most of that, not generation as such.

With four engineers and five languages, pure hand-writing has these costs:

- **Cost:** every API change lands five times, in five idioms, by the same four people.
- **Drift:** hand-written clients drift from the API just as your spec did. Nothing mechanical keeps them correct.
- **Maintenance:** with 1,200 customers, you will be maintaining five libraries for years.

The hybrid splits the work like this:

| Layer | How | Why |
|---|---|---|
| Models, endpoint methods, serialization | Generated, internal package, custom templates | Mechanical and high-volume, so drift is what you most need to prevent |
| Public facade | Hand-written, thin, per language | This is what customers read and what "feels official" |
| Auth, retries with backoff, idempotency keys, timeouts, pagination iterators, typed errors, user-agent | Hand-written once per language, following one shared design spec | Behavior is identical across languages even when the idioms differ |

Customers import the facade, and the generated layer stays an implementation detail. Regeneration then never breaks the public API.

You can settle the disagreement with evidence. Build the pilot (section 4), show it unlabeled to 5 to 10 friendly customers next to a hand-written endpoint or two, and ask which is which. If they can tell, change course for that language.

## 2. Fix the spec first (blocking)

Any generator works from the spec. Generating from a spec that is six months stale just produces wrong clients faster.

1. **Measure the drift.** Run contract tests against staging, for example Schemathesis or Dredd, driven by the current spec. The failure list is your drift backlog.
2. **Pick a source of truth.** Preferably generate the spec from the API code or its route and schema definitions. If that isn't possible, keep it hand-maintained but enforced by a CI contract test.
3. **Add a CI gate.** Make the build fail when the API and spec disagree. Without this gate the spec will drift again.
4. **Add a breaking-change diff.** A tool such as oasdiff in CI catches accidental breaking changes between spec versions.
5. **Add examples and descriptions.** They become the generated docstrings, and thin docs make the SDKs feel thin.

Rough estimate: 2 to 4 weeks for one or two engineers, depending on how much drifted. Don't start on SDKs until the contract tests pass.

## 3. The security rule: two things to check with your security org

You described the rule as "nothing in our build pipeline may call out to an external SaaS." That rules out some popular options and raises two questions.

**Tooling.** Several commercial SDK generators run their generation in the vendor's cloud. Treat those as excluded unless the vendor offers a verified fully offline mode. Candidates that run entirely inside your network:

- **OpenAPI Generator.** It supports all five languages with customizable templates. OpenAPI 3.1 support is partial, so test it against your spec.
- **Kiota.** It is Microsoft's tool and covers Python, TypeScript, Java, Go, and PHP with a consistent design. Its fluent, path-builder style is opinionated, so check that you like it.
- **Per-language generators.** Examples are oapi-codegen or ogen (Go) and openapi-python-client (Python). They often produce more idiomatic output but multiply the tools you maintain.

Pin the generator version in a container image in your internal registry.

**Dependencies and publishing.** Both of these are outbound calls to registries, and registries are arguably external services:

- **Pulling dependencies.** Builds need PyPI, npm, Maven Central, Go proxy, and Packagist mirrors. Use an internal proxy such as Artifactory or Nexus.
- **Publishing.** Public SDKs have to land on PyPI, npm, Maven Central, Packagist, and a public Git repo for Go modules. Ask security whether publishing counts as a build-pipeline call. If it does, you need an approved egress path or a separate release stage outside the build pipeline. A promotion step from an internal artifact repository, run by a human or an approved gateway, usually satisfies this.

Get the answers in writing before you design the release pipeline. Otherwise you may build the whole pipeline and fail review at the last step.

## 4. Build order

1. **Write one SDK design spec**, language-agnostic: naming rules, error taxonomy, retry and timeout defaults, idempotency, pagination, auth, versioning, and the user-agent format. Each facade implements it in its own idiom.
2. **Pilot one language**, the one with the most customers by your API logs, not by guesswork. Go through generator selection, custom templates, facade, docs, and the CI loop: spec change, regenerate, test, publish candidate.
3. **Run the blind comparison** from section 1 on the pilot's output.
4. **Fan out the rest.** Do the next two languages from the same template and pipeline, then the final two. Expect each to be much faster than the pilot, though Java and PHP generator output often needs the most template work.
5. **Automate regeneration.** A spec change opens a PR in each SDK repo. The facade tests and a contract test against staging gate the merge.

## 5. Team split (four engineers)

- **Engineer 1:** spec and contract tests (section 2), then owns the spec pipeline permanently.
- **Engineer 2:** generator, templates, and the CI/release pipeline, including the security work.
- **Engineers 3 and 4:** facades, docs, and the examples. Split by language pair once the pilot is done.

Have the same person own a language's facade end to end, so each SDK has one accountable maintainer.

## 6. When hand-writing is still right

Hand-write if either of these holds:

- You can't get the spec to a trustworthy state.
- No offline generator produces acceptable output for a given language, even after template work.

Even then, keep the design spec and the contract tests, which are what keep five hand-written clients honest.

## 7. Questions that would change this plan

1. Can security answer the registry and publishing question (section 3)? This is the biggest schedule risk.
2. Do you have API-log data on which languages your 1,200 customers actually use? It sets the pilot choice and the order.
3. Can the spec be generated from the API code, or must it be hand-maintained?
4. Is there a support or breaking-change policy for existing integrations? It sets the versioning rules in the design spec.