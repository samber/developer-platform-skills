# Ledgerwell client libraries: what to build and in what order

## Recommendation

Build **Java and .NET first**, then Python and TypeScript, then Ruby and Go. Ship six supported libraries by year end, not nine. If your VP needs the number nine, add three generated, clearly labeled "preview" SDKs. They are not a nine-language support commitment.

## Why not the TIOBE and Stack Overflow order

- **Those indexes measure how many people write a language.** They don't measure what your buyers write. Your 40 integrated customers are all Java or .NET, plus a couple of Ruby shops. That is your real data, and it beats any public survey.
- **Python tops TIOBE largely because of education and ML.** JavaScript tops the survey because of front-end work. Neither tells you what a bank's integration team uses to call a payments API.
- **C++ should not be on the list.** I can't think of a mid-market bank or finance team that integrates a reconciliation API from C++. If someone has asked for it, treat that as a one-off.
- **Building Python first would mean none of your current customers benefit at launch.** Their curl examples would still be their only option for months.

## Build order

| # | Language | Why | Target |
|---|---|---|---|
| 1 | **Java** | Most of your customers. Banks live here. | Java 8 baseline, so no customer is locked out |
| 2 | **.NET (C#)** | The other half of your customers. | .NET Standard 2.0, which covers both Framework 4.8 and modern .NET |
| 3 | **Python** | Finance and data teams reconcile in notebooks and scripts. It is also the likeliest first language for prospects. | Python 3.9+ |
| 4 | **TypeScript** | Covers JavaScript too, so you build one library, not two. Fintech startups and internal tooling teams use it. | Node 18+, with types shipped |
| 5 | **Ruby** | Existing customers, so it is a retention task. | Generated, with light polish |
| 6 | **Go** | Common in newer fintech backends. Lower priority until sales asks for it. | Go modules |

**Skip separate libraries for these:**
- **Kotlin and Scala:** the Java SDK works from both. Write one doc page on JVM interop instead.
- **JavaScript:** TypeScript covers it.
- **C++:** no demand.

## If the VP insists on nine

Slots 7 to 9 should be **PHP, Kotlin (idiomatic wrapper over the Java SDK), and one more** chosen from sales pipeline data. Make them generated from your OpenAPI spec and label them "preview, best-effort support".

Don't count them as supported. Each language you support costs ongoing work: releases, security patches, runtime upgrades, and support tickets. Six well-maintained libraries are worth more to a bank's procurement review than nine uneven ones.

## Suggested timeline

I'm assuming about 11 weeks until year end, so adjust if your team is small.

1. **Weeks 1–2: prerequisites.**
   - Make the OpenAPI spec the single source of truth, and fix any drift between the spec and the live API.
   - Pick a generator, such as Stainless, Fern, or OpenAPI Generator, and a shared test suite that every SDK must pass against a sandbox.
2. **Weeks 3–6: Java and .NET.** Hand-polish these two. They are the ones your customers will judge you on.
3. **Weeks 6–9: Python and TypeScript.**
4. **Weeks 9–11: Ruby** as generated and lightly polished. Add any preview SDKs the VP wants.
5. **Q1: Go**, unless sales demand pulls it forward.

## What every SDK must do (payments-specific)

- **Money as exact decimals:** `BigDecimal`, `decimal`, `Decimal`, or strings. Never floats.
- **Idempotency keys:** automatic on writes, with safe retries.
- **Retries with backoff:** also honor `429` and `Retry-After`.
- **Webhook signature verification:** a one-call helper in every language.
- **Pagination iterators:** so users don't hand-roll cursors.
- **Typed errors:** include request IDs.
- **Corporate environment support:** proxy settings, custom TLS and mTLS, and configurable timeouts. Bank environments need these.
- **Semantic versioning** and a changelog from the first release.
- **Quickstarts and a migration page from the curl examples** in each language.

## Two checks before you commit

1. **Ask sales and customer success for the stack of every open deal** and the language each prospect asked about. Forty customers is a small sample, and this reorders slots 3 to 6 cheaply.
2. **Ask your Java and .NET customers which runtime versions they run.** Banks lag, and a Java 17-only or .NET 8-only SDK could exclude several of them.

## Message for the VP

"Nine languages is a count. Coverage of the customers we have and the ones we're selling to is the goal. Java and .NET cover our whole installed base. Six supported libraries by year end cover the realistic prospect base. Extra languages beyond that are cheap to generate but expensive to support, so we'll offer them as previews and promote them only when demand shows up."