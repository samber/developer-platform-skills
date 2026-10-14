# Verdict: not ready to ship

Sections 2 and 3 together recreate the update channel that every major 2024-2026 marketplace incident used. Ferrule auto-installs updates into customer tenants overnight. The summary gives that channel no objective gate, no hold, and weak publisher authentication. Section 5 isn't a policy section at all.

I reviewed your five-section summary, not the full doc. The skill starts with a 10-question interview, which I couldn't run here. So I flagged where my assumptions change the answer (see the end).

**Fix order:** Section 3, then Section 2, then Section 4. Section 1 comes after that, and Section 5 comes out of the doc. Harden the channel that ships code before you deepen initial review.

## Section 3, Publish: blocker

The summary says developers push builds with username, password and an SMS code, and builds go live to tenants that night.

- **SMS is not phishing-resistant 2FA.** The 2025 npm maintainer phish reset the victim's 2FA and published malicious releases of about 18 packages, including chalk and debug. npm's operator then moved to FIDO-based 2FA. SMS is weaker than the TOTP that failed there, because SIM swap and relay phishing both beat it. That last point is my inference, not a sourced claim.
- **No propagation hold.** "Live to tenants that night" means a stolen publisher login compromises all of your installed tenants within hours. With auto-propagation, a 24-48 hour hold between a cleared update and propagation is mandatory. It needs an operator kill switch inside the window and an expedite path for security fixes.
- **No credential lifetime control.** There is no mention of short-lived or scoped publish tokens, or of CI publishing. npm shipped a 7-day default and 90-day maximum token lifetime after its worm.

Chrome's Cyberhaven incident (December 2024) shows the failure mode. A phished publisher account pushed the same injected code to at least 35 extensions with roughly 2.6M users, through an update channel with no hold. Your channel has no hold either.

**Minimum to write into the doc:**
1. FIDO/WebAuthn required on publisher accounts. SMS is removed, and the account-recovery path is hardened too.
2. Short-lived, scoped publish tokens.
3. A 24-48h propagation hold, a kill switch, and an expedite path.
4. Later, as publisher count grows: OIDC trusted publishing from CI.
5. Signed artifacts enforced at install only if tenants execute auto-updated code. That is the highest-effort control, so it can wait.

## Section 2, Updates: blocker

"Minor publishes without re-review" is undefined. If "minor" is the developer's own version label, an attacker's malicious build is simply labeled 1.4.1.

- **Define minor by objective criteria a developer can self-assess.** Full re-review fires on any of: new OAuth scopes, new external endpoints, changed data handling, payment-model change, new app type. Anything else takes the fast path. This is Atlassian's published trigger list.
- **Scan every release.** The fast path stays safe only if automated scanning runs on every version, plus periodic scans for apps that never ship an update. Without it, the fast path is the gap.
- **Add an annual re-review floor** for the tier that holds purchase-order data. It catches drift in apps that never update.
- **Don't use "substantial changes" wording.** Slack's version of it is subjective, and it decays into never-resubmitted.

The fast path is the right default for 210 apps, since reviewing every update would swamp reviewers. But a fast path with no objective definition, plus auto-install and no hold, is the shape the skill deletes outright.

## Section 4, Enforcement: incomplete

"May hide, suspend or remove any app that violates our policies" is a permission, not a ladder. A rule with no rung behind it is a preference. The ladder needs:

1. **Six rungs.** They are finding raised, remediation SLA by severity, listing hidden, new installs suspended, tokens revoked or kill switch, and delisting with customer notification.
2. **For each rung:** an owner, a developer notice period, and the evidence that fires it.
3. **Discovery channels.** These are a required security contact per partner, an incident-reporting channel, and vulnerability discovery via internal scanning and a disclosure program. A bug bounty can come later.
4. **Publisher-level enforcement.** A bad-faith or non-responsive publisher is a different problem from one bad app.
5. **A notice runway for new requirements** on already-listed apps. Atlassian commits to at least six months.
6. **An appeal path.** The summary has none. The default is a human-reviewed appeal, by someone who didn't make the original decision, with a stated turnaround. It must be explicitly distinct from resubmission, and every rejection must cite the violated policy. If you serve EU business users, platform-to-business rules (P2B) give them mediation rights over listing decisions, so the appeal path is not optional.

## Section 1, Admission: needs work

- **"Enhanced review at the reviewer's discretion" fails the first gate.** A tier trigger must be objective so developers can self-assess before submitting. Write it as: any app that reads or writes purchase-order data, or requests write access to customer data, moves up one review tier.
- **A questionnaire is self-attestation, not security testing.** Atlassian pairs its questionnaire with automated scanning that hard-blocks on any critical or high finding. Add scanning and a named scope-minimization rule: an app requests only the scopes it uses, and high-risk scopes need demonstrated necessity.
- **Data-access review is missing.** It should cover where data goes after consent (external endpoints, subprocessors, retention) and state the secrets-handling prohibitions.
- **Mark each check as automated or human.** For example, auto-ticket only critical and high findings, and route only secret-scan hits to humans.
- **Give developers your pre-check tool before submission,** so they can self-screen.
- **Single hard gate is the right default for now.** Purchase-order data is business records at minimum, and 210 apps is small enough for reviewer capacity. Revisit when update volume makes reviewer cost the constraint.

## Section 5, Curation: remove it from this doc

Open versus curated is a strategy decision, and this process enforces that decision. It doesn't make it. Sections 1-4 already describe a gated marketplace, so the doc contradicts itself if Section 5 leaves "open" on the table. A no-review registry is also incompatible with having a review policy at all. If you still need the decision, make it first with `connector-marketplace-strategy`, then cite the result here. If it lands on hybrid with a certified tier, Section 1 changes shape.

## The skill's four design-document gates

| Gate | Status |
|---|---|
| Every tier has an objective, self-assessable escalation trigger | ❌ "reviewer's discretion" |
| "Minor update" defined by objective criteria | ❌ undefined |
| Every enforcement rung has an owner, notice period and evidence | ❌ no rungs |
| Publish channel has the default control rung, plus a propagation hold if updates auto-propagate | ❌ neither |

All four fail. The doc also has no KPIs. Add first-pass approval rate, time-to-decision against an SLA, share of updates clearing the fast path, appeal overturn rate, post-approval findings with time-to-remediation, and scan false-positive rate.

## What I assumed, and what would change it

- **Auto-propagation:** confirmed by your description. It is what makes Section 3 the top priority.
- **Maximum data grant:** I assumed purchase-order data means read or write on business records. If any app touches regulated financial data, the hard gate stays regardless of volume.
- **Unknown, and they'd move the answer:**
  1. Does Ferrule serve EU business users? That moves the appeal rung up.
  2. How many reviewers and what tooling exist today? No SAST or secret scanning means the pre-screen automation has to be built first.
  3. Is there a hard ship date? A hard date promotes the controls that ship as policy text, such as FIDO, the hold, the objective triggers and the ladder. Everything that needs engineering follows.

Send me those three answers and I'll turn this into the full review-process design doc, section by section. The skill has me validate each section with you before the next.