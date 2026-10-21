# Artifact types, coverage matrices and vendor cases

Load this file during step 3, when assigning an artifact type per developer job and sizing language coverage.

## Contents

- Artifact taxonomy
- Named taxonomies to cite
- Language and framework coverage cases
- Intake gating

## Artifact taxonomy

| Artifact                        | Developer job                          | Typical owner             | Example                                                    |
| ------------------------------- | -------------------------------------- | ------------------------- | ---------------------------------------------------------- |
| Snippet in docs                 | Learn one method                       | Docs or SDK team          | AWS "Single action" (out of scope here: snippet policy)    |
| Scenario sample                 | Integrate one workflow                 | Docs, SDK or DevRel       | AWS "Scenario", Expo `with-<library>` examples             |
| Tiny quickstart                 | First call with least code             | DevRel                    | Plaid Tiny Quickstart: one backend, one endpoint           |
| Flagship multi-language quickstart | Evaluate plus first end-to-end success | DevRel or DX            | Plaid Quickstart, Stripe Samples, Auth0 quickstart repos   |
| Reference app                   | Production pattern                     | Solutions or docs team    | AWS "Cross-service" apps, Stripe Apps "SuperTodo"          |
| Starter template / deploy button | Evaluate by owning a running copy     | Platform or partner       | Vercel Deploy Button, Twilio Function templates            |
| Hosted explorer or collection   | Zero-install first call                | DevRel                    | Postman public workspaces (Stripe, Twitter)                |
| Embedded playground             | Try in the browser                     | DevRel plus platform      | CodeSandbox or StackBlitz embeds (no vendor governance published) |
| Agent context                   | Let a coding agent integrate correctly | DevRel or docs            | Plaid "vibe coding guides", aws-samples SKILL.md skills    |

## Named taxonomies to cite

- **AWS SDK Code Examples**: "Single action" (one service function), "Scenario" (multiple functions in one service), "Cross-service" (sample applications across services). The cleanest published split; it maps onto first call, integrate, production pattern.
- **Stripe Apps**: "Complete sample app" versus "Minimal samples" that "demonstrate specific techniques" and "might need additional features to be useful".
- **Plaid**: the main Quickstart "is designed to show as many products and configurations as possible"; the Tiny Quickstart serves the minimal first call. Two artifacts for two jobs.
- **Google Cloud Samples Style Guide**: snippets aim at copy-paste-runnable, teach through code, idiomatic. Principles in priority order: clarity, idiomaticity, consistency, simplicity, portability, maintainability.

## Language and framework coverage cases

| Platform        | Full-app coverage                                   | Framework rule                                        | Long tail                                               |
| --------------- | --------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------- |
| Stripe          | Starter and accept-a-payment: 7 server languages each (.NET, Go, Java, Node, PHP, Python, Ruby) | "the most minimal framework to convey the key Stripe calls" | CLI picks server and client language per sample     |
| Plaid           | 5 backends: Node, Python, Ruby, Go, Java; one React frontend | Shared frontend across backends              | .NET port "not created, reviewed, or supported by Plaid"; new product quickstarts Node only |
| Google Cloud Run | Hello World in 8 languages                         | Idiomatic per language over cross-language uniformity | Pub/Sub in 4 languages, Cloud SQL in 3, VPC testing in Python only |
| AWS SDK examples | 11 SDK languages, folder per SDK major            | Per-language standards wiki                           | Deprecated SDK majors archived in place                 |
| Auth0           | One repo per framework, about 106 repos            | Framework-specific SDK quickstarts                    | Sister brand Okta moved its PHP samples to security-patch-only, then archived |

Pattern: full parity only for the flagship quickstart; coverage thins as scenarios specialize; new products launch in one language.

Matrix shape for the register: rows are scenarios (one stable ID each, shared across languages like Google's region tags), columns are tier-1 languages, cells are `tested`, `present-untested`, `missing`, `community`. Parity coverage = tested cells ÷ (scenarios × tier-1 languages), computed for the flagship row and reported separately for the rest.

## Intake gating

- AWS triages sample requests on clarity, relevance and feasibility, asks two months' lead time for larger examples, and states that bug fixes and security issues take priority over new examples.
- A Google samples README states "Entirely new samples are not accepted".
- Twilio's community intake requires a permissive license, no known vulnerabilities, automated tests, and a pledge that the sample "will be kept up-to-date", backed by a signed agreement.

Growth gated by owners keeps the capacity cap honest: a request queue with a maintenance-first rule turns "please add a sample" into a trade against upkeep hours.
