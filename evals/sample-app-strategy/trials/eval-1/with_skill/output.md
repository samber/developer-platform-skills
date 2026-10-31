**Do first: revoke the `bp_live_` key in `checkout-node` today.** Removing the commit does not undo the exposure. Treat the key as public, pull its API activity since the 2024 commit, and bring in security. If the key belongs to a customer, notify them.

I ran nothing. This triage comes from your list alone, and no repo was scanned. Every section below is **unapproved - assumed**, because the answers came in one batch.

## Assumptions

- Brackenpay is a payments API, and the shape is a standing quarterly policy.
- There is no mobile SDK.
- You are the portfolio owner.
- "Green" means CI passes. I don't know whether it calls the sandbox.
- The SDK major and API version each repo pins are `unknown` for all 15.
- v1 was already sunset last January.

## Triage

15 repos, run through the 8 rules in order. Every verdict assumes the secret scan comes back clean.

| Repo | Rule | Verdict | After |
|---|---|---|---|
| checkout-node | 1 (leaked key) | Revoke key, fix CI, then merge into `checkout-quickstart` | supported |
| checkout-python, -java, -go | 8, plus step 3 (one flagship repo) | Merge into `checkout-quickstart` | supported |
| checkout-elixir | 2 | Community label, with Marek as maintainer | community |
| checkout-dotnet | 2, then 4 | Archive. Dana's veto turns it into a community label with a "currently failing CI" banner | community, or archived |
| auth-quickstart | 3 | Fix in place (rebuild if the fix costs more), then merge into `scenarios` | supported |
| webhooks-node | 3 | Fix, then merge into `scenarios` | supported |
| payouts-node, payouts-python | 6 | Merge into `scenarios` (scenario ID `payouts`) | supported |
| deploy-starter | 8 | Keep (own repo, deploy template) | supported |
| api-v1-samples | 2 | Archive, redirect to `checkout-quickstart` and the v1-to-v2 migration guide | archived |
| subscriptions-ruby | 2 | Archive, successor "none" | archived |
| marketplace-reference-app | 4 | Archive, redirect to the payouts scenarios. Swap Sales' slide link first | archived |
| hackathon-demo-2025 | 4 | Archive, successor "none" | archived |

Counts:
- Fix then merge: 3
- Merge: 5
- Community label: 2
- Archive: 4 (5 if Dana accepts the .NET archive)
- Keep: 1

You go from 15 repos to 3 supported repos (`checkout-quickstart`, `scenarios`, `deploy-starter`) plus 2 community repos.

Details on specific rows:
- **checkout-node:** 11 docs pages link to it, so swap all 11. Build `checkout-quickstart` with a fresh history. Archive the old repo only after the key is dead.
- **checkout-elixir:** Marek must accept in writing. Give him write access to that repo only. Keep sandbox CI secrets away from him.
- **checkout-dotnet:** it is red, has no owner, and isn't tier 1, so rule 2 says archive. Dana's veto only changes the label. Ask her what the two prospects actually ran, since the repo has been red for 5 months.
- **auth-quickstart:** you sign off on the escalation, and after one review cycle you own it by default. Never archive it. The flow has only a Node version, so check what Python, Java and Go readers do at page two.
- **webhooks-node:** read the 14 tickets first (1 hour). Decide fix or rebuild from what they say. Add a second language only if tickets or API traffic name one.
- **marketplace-reference-app:** this is the one real reversal risk. If Sales shows marketplace flows drive active deals, rebuild one reference app after launch. The ~16 hours a quarter it needs only fits if you cut flagship languages first.
- **Usage data:** GitHub traffic keeps only 14 days, so treat usage as `not measured`, never zero. Start weekly snapshots now.

## 1. Inventory and baseline

- 15 artifacts: 7 quickstarts, 4 scenarios, 1 reference app, 1 deploy template, 2 legacy or demo.
- 7 red, 7 green, 1 `unknown` CI (`api-v1-samples`).
- 0 confirmed owners.
- 1 known secret hit.
- Pins are `unknown` everywhere.

## 2. Portfolio shape

**Recommend lean golden path.**
- It keeps one flagship at parity across tier 1, scenario samples in a shared repo, and the one deploy template you already have.
- Reference-app anchored is the other option. It doesn't fit the capacity sum and has no deal evidence yet.
- Gallery-led needs telemetry you don't have.

## 3. Artifact types and coverage

| Job | Artifact | Status |
|---|---|---|
| First call | `checkout-quickstart`: Node, Python, Java, Go | served |
| Integrate one workflow | `scenarios`: webhooks/node, payouts/node, payouts/python, auth/node | served |
| Start a project | `deploy-starter` | served |
| Evaluate without installing | hosted collection | not served. Add it next quarter, since it costs about 1 hour or less |
| Production pattern | docs page plus scenarios | not served. A reference app is added only if marketplace deal evidence shows up |
| Mobile | none | not served. Add it if a mobile SDK reaches tier 1 |
| Coding agent | the index in §7 | served, with no separate guide yet |

Languages:
- **Supported:** Node, Python, Java, Go.
- **Community:** Elixir, and .NET if Dana vetoes.
- **Absent:** Ruby.

Publish this table in the README of each repo and in docs.

**Capacity (self-set estimates):**

| Item | Hours/quarter |
|---|---|
| Flagship, 4 languages × 4h | 16 |
| 4 scenarios × 1h | 4 |
| deploy-starter | 2 |
| CI harness | 3 |
| Index, quarterly review, measurement | 6 |
| **Total** | **31 of 40** |

The remaining 9 hours are headroom. Ingrid carries about 16, Tomasz about 9, and you about 6. These assignments are proposals until each person accepts. "DevRel" can do labor but never fills the owner column.

**One-off 60 hours, in sequence:**

| Week | Work | Hours |
|---|---|---|
| W1 (Nov 2) | Key revocation and log review: 3. Full-history secret and vulnerability scan on all 15 repos: 3. Ticket read, traffic snapshot and API traffic share by SDK: 3. Send Dana and yourself the approval packet | 9 |
| W2 | Archive the 3 clear rows, after the veto window | 3 |
| W2–3 | Fix auth: 7. Fix webhooks: 5. Fix checkout-node CI: 4 | 16 |
| W3–4 | Flagship repo and moves: 6. `scenarios` repo and moves: 5. CI harness, Renovate and scoped secrets: 5. Index and docs link swaps: 4. Archive 8 merged sources: 3. Marketplace and Sales swap: 2. Elixir and .NET labels: 2 | 27 |
| W5 (ends Dec 4) | Reserve | 5 |

If the fixes miss by the end of W3, rebuild or demote them before launch. Decide that at the W3 gate. If hours run short, defer the three green checkout merges first.

**Dates:** the veto window closes Fri Nov 13, and your sign-off lands Mon Nov 16. Fixes on the adoption path start now, since they need no sign-off.

## 5. Freshness contract

All numbers are self-set.

- **CI:** weekly against the sandbox, plus a run on every SDK release and API version change. The v3 launch is the first trigger.
- **Credentials:** sandbox keys only, in CI secrets, never exposed to fork PRs. Rotate each quarter, clean up test fixtures, and stay under the sandbox rate limits.
- **Dependencies:** grouped Renovate, minor monthly and patch quarterly, automerge only behind green sandbox CI, alerts at any time.
- **Red-build SLA:**
  1. Owner ticket the same day, automated.
  2. Fix-or-deprecate decision forced after 14 days red.
  3. Archive after 30 days deprecated.
  4. If the owner is absent, you decide.
- **Pins:** record the SDK major, runtime and API version in the index. Check them each quarter.
- **Sandbox gaps:** I don't know which flows the sandbox skips. I'd guess webhook delivery and payout settlement. Label those "compiled, not run" until confirmed.
- **Secret scanning:** turn it on org-wide, with a custom pattern for `bp_live_`.

## 6. Archive rules

Archive on evidence, not age. Triggers:
- Red past the SLA with no fix scheduled.
- No owner for one review cycle, outside the adoption path.
- Superseded or merged.
- SDK or API end of life.
- Red and low usage together, which go first.

Sequence for each archive:
1. Confirm the trigger and the successor.
2. Add the README banner, a successor link, and remove deploy buttons.
3. Move the repo from the index's current list to its redirect registry.
4. Swap the links in docs, decks and the gallery.
5. Stop bots and CI.
6. Run a last secret scan.
7. Archive read-only. Never delete.

Veto path: a vetoed archive becomes a community label, never a return to kept. A red repo with that label shows "currently failing CI". A community repo that stays red past the SLA with a silent maintainer gets archived.

## 7. Discoverability

- Create a `samples-index` repo holding `index.json`. You own it.
- Per-sample fields: ID, type, job, languages, status, successor, owner, pins.
- The registry also has `aliases` and `deprecated` blocks.
- Drive docs links, GitHub topics, any scaffold CLI you have, and the agent index from it.
- Agents ingest stale repos as readily as current ones, so the index has to say which are current.

## 8. Measurement

- **Tag traffic:** put the sample ID in the SDK's app-info or User-Agent field.
- **Per-artifact signals:**
  1. Tagged invocations.
  2. Time to first sandbox call.
  3. Tickets naming the sample.
  4. CI pass rate for the quarter.
- **Reporting:** report stars but never decide on them. Q1 is the baseline.
- **Review:** a quarterly review (about 3 hours) refreshes the register, applies the triggers, and recalibrates hours from what the owners logged.

**Pass gate: not met.**
- No owner has accepted a row yet.
- Nothing is approved.
- Freshness contracts aren't signed.

## Open questions (5)

1. Does v3 bump the SDK majors or the API version? If so, the hours may be tight.
2. Is the v1 sunset already past? I assumed January 2026. If it is January 2027, v1 stays live and the migration notes matter more.
3. Which flows does the sandbox not simulate?
4. Do Ingrid, Tomasz and Marek accept the rows above?
5. Whose key leaked, one of yours or a customer's?

**Next, in 2 minutes:** message Ingrid and Tomasz with their proposed rows and ask for a yes or no by Wednesday.