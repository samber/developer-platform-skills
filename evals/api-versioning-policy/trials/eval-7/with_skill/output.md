**Do this first:** pull v1 traffic per account for all 31 accounts, today. Sort by request volume and by revenue. About half a day. Both fronts depend on that sheet.

I skipped the one-question-at-a-time interview and worked from assumptions, listed at the end. The date check below also needs your answer. Each answer can change the recommendation.

## Front 2: the v1 sunset (urgent)

**Keep March 1 as the public date. Don't flip the switch blind.** The skill's rule is that a version is removable when telemetry shows zero traffic, or a residue you have consciously accepted. A date passing proves nothing about who migrated. 14% of traffic across 31 accounts is not zero, and for a fintech a failed call can mean failed money movement.

**"We honored the window" only holds if it holds.**
- A fully public API needs at least 12 months. You gave exactly 12.
- Mobile-app or enterprise consumers need at least 24 months. If any of the 31 are enterprise or mobile, you are under the floor. Slow change management is on their side, but the floor is yours.
- Check that the 12 months started at the announcement. State the clock start in the policy next time.

**Steps, with T = March 1:**
1. **T-6w, 1 day:** check v1 responses. They need `Deprecation` (RFC 9745), `Sunset` (RFC 8594) and `Link: rel="successor-version"`. Add any that are missing. About 2h. Confirm new signups default to v2. A version that is both deprecated and still the default is a named failure mode.
2. **T-6w to T-5w:** contact all 31 accounts directly. Use a named owner per account, a migration guide, and an offer of a call. Add a dashboard banner. Add an in-response warning on v1 calls. Headers alone reach nobody. 31 reachable accounts is a small, doable outreach job.
3. **T-4w:** re-measure v1 share. If it is flat after the outreach, the channel failed. Escalate to calls and executive contacts.
4. **T-2w, go/no-go:** apply the rule below.
5. **March 1:** hard cutoff. v1 returns `410 Gone` with a described error, a migration link, and the successor version. No fall-forward to v2. Silent behavior drift on financial calls is worse than a loud failure.

**Go/no-go rule at T-2w:**
- Cut v1 for every account that has migrated.
- Also cut v1 for any account that got at least 3 contacts over 2 channels and never replied. That account had notice.
- For an account that engaged but can't finish, grant a private written extension. Give it a hard end date, 30 to 60 days. Put it in writing, like a partner SLA. Enforce it with a per-account allowlist at the gateway.
- Never move the public date. Twilio extended one end-of-life three times, and integrators learned to ignore its dates. Per-account extensions keep the public date intact.

**What to tell Ops:** the date stays. The kill happens per account against a measured rule, not blind. Cost of a 6-week migration push: about 1 engineer plus 1 person on communication.

## Front 1: the governance council

**Do not build a Google-style program before shipping.** Ship stage 1 now, in about 1.5 days, and don't block other work.

The skill gives three governance stages. Grow into them. Google's own paper says manual review alone "did not scale well", and Google has far more than one API and 12 engineers.

**Stage 1 for Ostrafin:**
1. **CI check:** add an OpenAPI diff (`oasdiff`) or Spectral to CI. It flags breaking changes mechanically. About half a day.
2. **Named approver:** one named senior engineer plus one backup approves anything flagged. No rotation. With 12 people and one API, a rotation is overhead.
3. **One-page policy, about half a day:** the skill's template sections in a short form.
   - Scheme: URI major version (`/v1`, `/v2`). It is the default for a hard-deadline team with no versioning machinery.
   - Breaking and non-breaking lists, with what is explicitly not contractual: message text, ordering, timing.
   - Windows: at least 12 months, 24 if mobile or enterprise. Define when the clock starts.
   - Communication: headers plus at least one human channel.
   - Enforcement: hard cutoff, then `410 Gone`.
   - Cap of 2 to 3 live versions.
   - Written security escape hatch.
4. **Rule:** no breaking change ships without approval. This rule matters most when the motive is business, not technical.

**Stage 2 trigger, written into the policy:** move to a chartered review board when the API surface outgrows one reviewer, or when breaking changes exceed about 2 per year. Stage 3 is not for you.

**Pitch to the VP Eng:** "We are standing up governance at stage 1 now. The v1 sunset is the live test of it. The charter grows when measured triggers fire." The VP's instinct is right that you need governance. The size is wrong.

**Sequencing:** draft the policy during the sunset, not before. This sunset teaches you the clock start, the window floor and the enforcement style. Write them into the policy while they are fresh.

## Assumptions

REST, fully public, 12 engineers, and one live API with v1 and v2 both serving. I assumed no per-account gateway config exists. Answers that change my advice:
- Are any of the 31 accounts mobile or enterprise? If yes, the extension rule gets more lenient.
- Are the headers already live on v1?
- Is the 14% flat or falling over the past 3 months? If flat, the earlier channels failed.
- What revenue share do the 31 accounts hold?
- Is v2 already the default for new signups?

**Date check:** my environment clock says 2026-10-03, which doesn't match "six weeks before March 1". I used the T-minus timeline above, so no calendar dates are baked in.

**Next:** build the per-account v1 sheet (the first action above), then paste the top 5 accounts by volume here. I will draft the outreach email and the `410` body for those.