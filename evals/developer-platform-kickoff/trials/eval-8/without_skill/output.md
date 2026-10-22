# Tern Robotics: client libraries, API pricing, first-run tutorial

I haven't seen your product, API, tutorial page or analytics, so everything below rests on stated assumptions. The tutorial section is a template and a diagnosis plan, not a rewrite of your page. Paste the current page and I'll write the real one.

## Order to hand me

1. **Tutorial (first).** It's a leak at the top of your funnel, and you can fix it this week with little engineering.
2. **Client libraries (second).** They have a ship date and a hard checklist, and the tutorial should end up using them.
3. **Pricing (third).** Finance needs usage data you don't have yet. Start metering now, and decide after about 4 weeks of data.

The one platform engineer is your constraint. Do the tutorial rewrite with curl so it doesn't wait on the SDKs. Swap in SDK snippets after release.

---

## 1. Publishing the Python and Go clients

### Python (PyPI)

**Package name and layout**
- Check the name on PyPI now, and reserve it with a `0.0.1` pre-release if it's free. Match the brand, for example `tern-robotics`, and import as `tern`.
- Use a `src/` layout with `pyproject.toml` and the `hatchling` or `setuptools` backend.
- Ship `py.typed` so type checkers see your inline annotations.
- Ship both sync and async clients if your users run async. Say which is primary in the README.

**`pyproject.toml` essentials**
```toml
[project]
name = "tern-robotics"
version = "0.1.0"
description = "Official Python client for the Tern Robotics API"
readme = "README.md"
requires-python = ">=3.9"
license = "Apache-2.0"   # SPDX expression (PEP 639)
license-files = ["LICENSE"]
authors = [{ name = "Tern Robotics", email = "devrel@<your-domain>" }]
keywords = ["robotics", "api-client", "sdk"]
classifiers = [
  "Development Status :: 4 - Beta",          # move to 5 - Production/Stable at 1.0
  "Intended Audience :: Developers",
  "Operating System :: OS Independent",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Programming Language :: Python :: 3 :: Only",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "Topic :: Scientific/Engineering",
  "Typing :: Typed",
]

[project.urls]
Homepage = "https://<your-domain>"
Documentation = "https://docs.<your-domain>"
Source = "https://github.com/<org>/tern-python"
Issues = "https://github.com/<org>/tern-python/issues"
Changelog = "https://github.com/<org>/tern-python/blob/main/CHANGELOG.md"
```
- Don't add a `License ::` classifier if you use the SPDX `license` field. Combining them is deprecated or rejected, depending on tooling version.
- List only Python versions you test in CI.
- Check the classifier list against `trove-classifiers` before upload, because PyPI rejects unknown ones.

**PyPI page**
- The README becomes the project page. Put install, a 10-line quickstart and a link to the tutorial at the top.
- Use absolute URLs for images and links, since relative ones break on PyPI.

### Go

Go has no registry. `pkg.go.dev` indexes your tagged module automatically.
- Use a public repo with a module path that matches the URL, `github.com/<org>/tern-go`, and `go 1.22` or whichever minimum you actually test.
- Use a standard OSI license file at the root, or pkg.go.dev won't render docs for it.
- Tag releases `v0.1.0`. Semver rules for Go:
  - From v2 on, the module path needs a `/v2` suffix.
  - Staying on `v0.x` until the API is stable avoids that churn.
- Write a package comment in `doc.go` and runnable `ExampleXxx` functions. pkg.go.dev shows them and `go test` verifies them.
- Keep dependencies near zero. A client library with a heavy dep tree loses trust fast.
- After tagging, request indexing by running `GOPROXY=proxy.golang.org go list -m github.com/<org>/tern-go@v0.1.0`.

### Docker Hub

Client libraries don't ship on Docker Hub. Only publish an image if you also ship a CLI, a local simulator or a gateway. If you do:
- **Short description (100 chars):** one line, for example "Tern Robotics CLI: manage fleets and call the Tern API from your terminal."
- **Overview (README):**
  1. What it is.
  2. A `docker run` quickstart that works with zero config.
  3. Tag policy (`latest`, `1.2`, `1.2.3`).
  4. Supported architectures (`linux/amd64` and `linux/arm64`, which matters for robotics).
  5. Env vars.
  6. Link to source and to the security policy.
- **Trust:**
  - Apply for Docker Official or Verified Publisher status if eligible.
  - Run as non-root, keep the image minimal, sign it with cosign, attach an SBOM and provenance (`docker buildx --sbom=true --provenance=true`), and scan with Trivy or Grype in CI.

### Trust signals (both languages)

**Release integrity**
- Python: use PyPI **Trusted Publishing** (OIDC from GitHub Actions). That removes long-lived API tokens, and attestations are generated automatically by `pypa/gh-action-pypi-publish`.
- Protect the release workflow with a GitHub environment that requires approval.
- Enable 2FA on the PyPI organization account.
- Go: use signed tags, and let the Go checksum database (`sum.golang.org`) record the module.
- Publish only from CI.

**Repo hygiene**
- `LICENSE`, `SECURITY.md` (a private disclosure address and a response time), `CHANGELOG.md`, `CONTRIBUTING.md` and a `CODE_OF_CONDUCT.md`.
- A CI badge on the README, with a test matrix across supported language versions.
- Dependabot or Renovate.
- `govulncheck` for Go and `pip-audit` for Python in CI.
- OpenSSF Scorecard, which gives you a public score you can badge once you've fixed the basics.
- Branch protection on `main`.

**Product-level trust**
- A stated versioning and deprecation policy (for example: semver, at least 6 months' notice before removing anything).
- A compatibility table mapping SDK versions to API versions.
- A status page link.
- Typed models, clear error classes with retry guidance, and a user-agent string like `tern-python/0.1.0`. The user-agent lets you see SDK adoption in your API logs.
- Named maintainers, and an issue response target you can actually meet. With one platform engineer, promise "triaged within 3 business days" at most.

**Launch day**
- Mention both libraries on the docs home page, the tutorial, the changelog and a short announcement post.
- Add them to `awesome-*` lists only after 1.0.

---

## 2. Usage-based API pricing

### Recommendation

Use **a small platform fee with included usage, plus per-call overage**, metered on a well-chosen billable unit. Don't use per-seat, and treat credits as packaging for later, not a starting point.

### Why not per seat
- API consumers are mostly robots, services and CI jobs, so seat count doesn't track the value or the cost you deliver.
- Customers also game seats by sharing a key.
- Seats only make sense for a dashboard or console product, and you can add that as a separate line item.

### Per call vs credits

| | Per call | Credits |
|---|---|---|
| Customer clarity | High: one number | Lower: they convert credits into calls |
| Weighting heavy and light endpoints | Needs multiple prices | Easy: cheap calls cost 1, heavy calls cost 20 |
| Engineering cost | Metering plus invoicing | Metering plus a ledger, expiry and top-up |
| Revenue shape | Variable, billed in arrears | Prepaid, with breakage and better cash flow |
| Price changes | Visible to everyone | Absorbed by changing credit costs |

For a team of 30 with one platform engineer, per-call is the first version. Move to credits only when endpoint costs differ by more than about 10x or you want prepaid commits.

### Pick the billable unit before the price

The unit should track value and your cost. For a robotics API, the candidates are:
- Successful requests.
- Robot-hours or active devices per month.
- Compute-heavy operations (planning, inference, simulation minutes).

Rules:
- Never bill failed or retried calls.
- Make the unit easy to explain in one sentence.
- If a few endpoints dominate your cost, price those separately instead of building a credit system.

### Structure
- **Free tier:** sized so a real prototype fits (not just a "hello world"). It carries the tutorial users.
- **Usage tier:** pay as you go with a card, with a monthly platform fee that includes a usage allowance.
- **Committed tier:** annual commit with volume discounts, invoiced, with a negotiated SLA.
- Use hard spend caps and usage alerts, so a runaway robot loop doesn't produce a surprise invoice. This is the biggest trust issue with usage billing.

### What it costs to build
- Use **Stripe Billing meters** or an equivalent (Lago, Orb, Metronome), not a homemade biller. For one engineer, building invoicing is the wrong use of their time.
- Emit one usage event per billable call from your gateway, keyed to an account and an idempotency ID.
- Show customers their usage in the dashboard, or they'll file support tickets.

### Questions for finance, before setting any numbers
1. What's the marginal cost per call, by endpoint?
2. What does a typical customer do per month? Pull the distribution (median, p90, p99), not the average.
3. Is revenue predictability or growth the priority?
4. Do the biggest customers want commits?
5. What's the competitor price point?

Prices set without answers to 1 and 2 are guesses. Start emitting meter events now, even before you charge, so you have the distribution in about 4 weeks.

---

## 3. First-run tutorial rewrite

### Step 1: find where the drop-off happens (about a day)

I can't tell why people leave without data. Instrument these events, then look at the funnel:

1. Landed on tutorial.
2. Created an account or key.
3. Ran the first request.
4. Got a successful response.
5. Reached the final step.

The step with the biggest drop decides the rewrite. Typical causes:
- **Before step 2:** signup friction or an unclear promise.
- **Between 2 and 3:** key handling, environment setup or install problems.
- **Between 3 and 4:** errors, auth failures, or needing hardware or a sandbox they don't have.
- **After 4:** the tutorial is too long, or it doesn't show a reason to continue.

Also watch 5 sessions of new users (screen recordings or a live call). It finds more problems than any dashboard.

### Step 2: rewrite rules

- **One goal, one path.** "Make your first successful API call in 5 minutes". Cut every option that isn't on the happy path.
- **No hardware required.** Offer a sandbox or simulator, so someone without a robot at their desk still succeeds.
- **Pre-filled key.** When the user is logged in, show their real sandbox key in the code blocks. Otherwise they have to leave the page and come back.
- **Copy-paste commands that run.** Each block is complete, with no `<placeholders>` except one.
- **Show expected output** after every command, so users can tell it worked.
- **Success within 3 steps.** Everything after the first real response is "next steps", not the tutorial.
- **Put the failure cases inline:** invalid key, wrong region, rate limit. Show the exact error text and the fix.
- **Test it.** Run the tutorial in CI against the sandbox, so it can't silently rot.

### Template

```
# Make your first Tern API call (about 5 minutes)

You'll end with: <the concrete result, e.g. "a robot pose returned from the sandbox">.
You need: a free account. No hardware.

1. Get your sandbox key            (pre-filled if logged in)
2. Make the call                   (curl; tabs for Python and Go once released)
   Expected response: <exact JSON>
3. Change one thing                (e.g. a parameter) and see the result change
   → You've now used the API end to end.

If it didn't work
- 401 Unauthorized: <cause and fix>
- 429 Too Many Requests: <cause and fix>
- Anything else: <link to support>

Next
- Build <the most common real use case> (link)
- Install the Python / Go client (link)
- See pricing and limits (link)
```

### After the rewrite
- Compare the funnel before and after for 2 weeks.
- Track **time to first successful call** as the headline metric. A realistic first target is under 5 minutes for most users.
- Once the SDKs ship, add Python and Go tabs next to the curl block. Leave curl in place as the default.

---

## What I need from you

1. The current tutorial text and any funnel numbers, to write the actual rewrite.
2. Your API's main use case and whether a sandbox exists, to finalize the tutorial and the free-tier sizing.
3. Your license choice for the libraries (Apache-2.0 or MIT are the safe defaults), and the PyPI and GitHub org names.
4. Finance's cost-per-call figures, to turn the pricing structure into numbers.