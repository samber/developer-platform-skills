# Sample archive rules: Marrowline

Status: ⚠️ unapproved - assumed. This covers step 6 of the sample-app-strategy workflow. Steps 1 to 5 haven't run, and I haven't seen the 38-repo inventory, so the VP's list of 16 is unverified.

## Don't ship the VP's rule as written

- **Age is not evidence.** A repo with no commits in 18 months can be green and on the adoption path. A repo with recent bot commits can be red. The skill triggers on CI state, not activity.
- **Stars are vanity.** The skill says to report them and never decide on them. Under 10 stars says nothing about leaks, EOL or partner links.
- **Delete is wrong.** Forks, inbound links and coding agents keep reaching the repo. Several of the 16 have hundreds of forks, so deleting them breaks real copies and leaves a 404 with no redirect. Archive with a banner and a redirect instead.
- **Age and stars miss real risks.** Your four named cases show it. `deploy-button` (the leaked key) may escape both filters, and `storefront-legacy` is unmarked, so no filter flags it.

I kept the VP's intent. Inactivity opens a review but never archives by itself (rule 3).

## Assumptions (change any that are wrong)

- Standing policy, run every quarter.
- The VP Eng signs off on archives.
- Samples run against a sandbox with test keys.
- Usage is not measured, so it is never read as zero.
- The leaked key is each deployer's own storefront key, printed in the deployer's build logs.

## Archive rules

**Triggers.** Any one is enough, checked in this order.

1. 🔴 **Leaked credential or known-vulnerable dependency.** Fix or archive this week. This overrides every other verdict.
2. **SDK major or API version reached end of life.** Archive with redirect on the EOL date. Announce the retirement in the README beforehand.
3. **Red past the SLA with no fix scheduled.**
4. **Superseded by a merged or newer artifact.**
5. **No named owner for one review cycle**, outside the adoption path. One review cycle is 30 days during this cleanup, then one quarter.
6. **Low usage and red together.** Retire these first.

**Not triggers.** Age alone, stars, forks, and commit recency.

**Inactivity review.** 18 months without commits opens an issue on the owner, or on the portfolio owner if there is none. It runs 30 days. Only a green sandbox CI run clears it. Closing the issue does not reset the clock, which is the weakness in Microsoft's bot.

**Protections.**

- Quickstart, auth, first-call and top-ticket samples are fixed in place or rebuilt. Never archive them for lack of an owner. Escalate to the VP Eng. After one review cycle the portfolio owner owns the repo.
- Before archiving anything linked from a sales deck or partner material, notify the link's owner and swap the link.
- If the VP vetoes an archive, relabel the repo community-maintained. A red repo's banner says "Currently failing CI". Never move it back to kept.

**SLA (all numbers self-set).**

- Owner ticket on the first red run, same day, automated.
- 14 days red forces a fix-or-deprecate decision.
- 30 days deprecated, then archive.
- If the owner is absent, the portfolio owner decides. If they are absent too, the VP Eng decides.

**Archive sequence.** Follow `references/archive-and-redirect-playbook.md`.

1. Confirm the trigger and the successor, or record "none".
2. Final commit: README banner, successor link, deploy buttons and template flag removed.
3. Move the repo from "current" to `deprecated` and `aliases` in the canonical index.
4. Remove it from docs, gallery, CLI list and agent index, pointing each at the successor.
5. Stop Renovate and scheduled CI, then run a last secret scan.
6. **Archive the repo read-only** (`gh repo archive`). Never delete.
7. Announce in the changelog if it was on the adoption path.

Banner:

```markdown
> **Archived <YYYY-MM-DD>. This sample is no longer maintained or tested.**
> Reason: <superseded | SDK v2 end of life | merged into <repo> | no longer supported>.
> Use instead: <successor link>. Migration notes: <link or "none needed">.
> The code stays readable and forkable; it may not work against the current API.
```

## Your four named repos

| Repo | Rule | Action |
| --- | --- | --- |
| `deploy-shopfront` | 1 | **This week.** Remove the deploy button and template flag first, so nothing new deploys. Rotate the exposed keys and notify the ~200 deployers. The archive banner must say deployed copies keep running on their own keys, and owners must rotate any key the template ever printed. Archiving doesn't fix the leak. Check git history for the key. Involve security on disclosure. Successor: "none", unless someone owns and CI-tests a rebuilt template. |
| `cart-sdk-v2-examples` | 2, timed | Put a retirement banner up now. Archive on the v2 EOL date, only after a v3 successor and migration notes exist. If no v3 sample exists, that is a gap to build, with an owner and CI. |
| `checkout-react` | 3 and the partner-link protection | Hold. It is probably on the adoption path, so fix in place. If it is archived anyway, the partner owner swaps the deck link first. It is out of the auto-archive set. |
| `storefront-legacy` | 4 | Archive with a "superseded" banner. Add `[ARCHIVED]` to the repo description. List it under `deprecated` in the index and in the agent guide. Archiving is what fixes the assistants, since coding agents ingest unmarked repos as current. Name a successor. |

## Replacing "16 of 38, done"

1. Build the register for all 38 (step 1). Run the secret and dependency scans first.
2. Apply the triage rules in order (step 4).
3. Report the count per verdict. Expect some of the 16 to be merged, fixed or kept, and some repos outside the 16 to be archived.

## Decisions I need from you

- Who owns the portfolio and signs off on archives? Is it the VP Eng?
- What is the exact v2 EOL date, and does a v3 sample exist?
- What are the successors for `storefront-legacy` and `deploy-shopfront`?
- Is the leaked key per-deployer, and can you identify the ~200 deployers from API logs?
- Does a sandbox exist for CI?
- May I replace the VP's rule with this one? That is your call to take to the VP.