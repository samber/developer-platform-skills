# Recommendation: build warehouse export first, as an API-first resource. Ship the CLI and Terraform provider right behind it.

## The three signals measure different things

| Signal | What it actually measures | Decision weight |
|---|---|---|
| 400+ reactions | Demand intensity from a self-selected, vocal group. It doesn't tell you whether they pay, have budget, or would churn without it. | Strong for *what to build second*. Weak as the sole tiebreaker. |
| 2 stalled renewals | Concrete revenue at risk with a deadline, tied to a named gap. | Highest. This is the only signal with a clock and a dollar figure. |
| 61% Python user-agent | Where existing traffic comes from. It is not a request. | Low for prioritization. It shapes *how* you build, not *what*. |

Leadership's rule, "pick by what the community wants", conflates "loudest" with "most representative". Your customers are also your community. Two of them have said, in effect, "we can't renew without this."

## What to build

**1. Warehouse export (first)**
- Scope the minimum that unblocks the renewals: scheduled batch export to object storage (S3/GCS, Parquet), then a Snowflake/BigQuery connector. Skip a generic pipeline platform.
- Treat the two stalled customers as design partners. Ask them for their warehouse, volume, and latency needs before you scope anything.
- Design it as a **public API resource** (`exports`: destination, schema, schedule, status) with an OpenAPI spec. This is the key move. Every export is then configurable from code, which is exactly what the community asked for.

**2. CLI (second, weeks after the export API lands)**
- A thin wrapper over the same API: `quorrel export create/list/status`, plus the existing core operations.
- Cheap once the API is clean, and it's the most-requested surface.

**3. Terraform provider (third)**
- Generate or scaffold it from the OpenAPI spec. Exports, and then your other resources, become Terraform resources.
- Terraform buyers are typically platform teams at larger companies, so this overlaps heavily with your enterprise accounts. It is not a separate audience.

**4. Python library**
- Don't let 61% drive a roadmap slot. Use it as a design rule: any new surface gets a first-class Python helper (`client.exports.create(...)`) on day one.
- Keep maintaining the library. Don't treat it as a build-next item.

## How to present it to leadership

The pitch isn't "enterprise beats community". It's this:

- "The community asked for infrastructure-as-code control of Quorrel. Export is the first resource we can only expose well if we build the API surface properly. The CLI and Terraform provider follow from it, and the same work saves two renewals."
- **Close the loop publicly.** Reply on the 400-reaction issue with a dated plan: export API now, CLI next, Terraform after. Months of silence on a loud issue damages the brand more than a transparent sequence does.
- **Invite community input on the export design.** Post the RFC in Discord and GitHub. This makes the build community-shaped.
- If leadership still insists on community-first, offer the CLI first only if export can be delivered in parallel by a separate team. Never trade the renewals for it.

## Facts to check before committing (about a day of work)

1. **ARR of the two renewals, and their dates.** If the combined value is small relative to the build cost, or the renewals are already lost, the case weakens.
2. **Were they really blocked on export?** Check the call notes and ask sales for the exact words. "Warehouse export" is sometimes a proxy for a security, compliance, or procurement objection.
3. **Who are the 400 reactors?** Cross-reference GitHub handles and Discord members against paying accounts and trials. If a large share are paying teams, Terraform and the CLI move up.
4. **Export effort estimate.** If it's more than about two quarters, the renewals may close before it ships. In that case ask sales whether an interim manual or bulk export (a one-off S3 dump, say) can bridge them.
5. **Overlap in the demand.** Do the enterprise accounts also ask for Terraform or a CLI? If yes, the sequence is even easier to defend.

## When I'd flip this

- Renewals are small, or customers confirm the real blocker is something else: go CLI first, then Terraform.
- Export can't ship before the renewal dates and can't be bridged: take the interim route and keep the sequence.
- Most of the 400 reactors are paying accounts: build the CLI and export in parallel.

## What I'm assuming

I haven't seen your ARR, effort estimates, or the reactor breakdown. The recommendation rests on the signals as you described them, so check the five items above before you commit.