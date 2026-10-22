**Next step:** split your security section into a pointer and a separate page, and publish the video ranking penalty in the rulebook. Both changes are small (about 20 minutes of editing). The two sections below are paste-ready.

Your interview answers (Q1–Q10) aren't in your message, so I assumed Quillrock has a ranked search and a review process. Say so if either is wrong.

## 1. OAuth scope audit and re-review triggers: don't put the mechanics in the listing rulebook

The skill lists this as a named failure mode, "scope creep into security review". The rulebook starts encoding permission audits and re-review triggers that belong to the review process. The two documents then drift apart and contradict each other. Content triggers (a blurry screenshot, keyword spam) must fire independently of safety.

Concrete risks if you merge the mechanics:
- Security changes its re-review triggers and the listing doc goes stale.
- The two sets of rules need different notice runways.
- A reviewer can't tell whether a rejection is a content or a safety decision, and partners dispute both.

Security's real goal is one page for partners to read. You can meet it without merging the rules:

1. Keep one partner-facing entry page with two sections.
2. Put scope audit and re-review triggers in the review process doc (`samber/developer-platform-skills@app-marketplace-review` owns that).
3. Keep only the content-side rule in the rulebook: the listing must match the app. HubSpot does this by requiring its Shared-data table to match the app's actual OAuth scopes.

Paste-ready section for the rulebook:

> **Permissions and data disclosure**
> Your listing must state which data your app reads and writes, and this must match the OAuth scopes the app actually requests. A mismatch is rejected as misrepresentation.
> How scopes are audited, and which app updates trigger a security re-review, are defined in [Security and Review Requirements](link). Content decisions and security decisions are made independently. Passing one does not satisfy the other.

If security insists on literally one document, accept it only with these conditions:
- Two separately owned parts.
- A separate changelog for each part.
- A notice runway per part.
- A rule that the review part overrides the listing part on safety.

## 2. Silent ranking penalty for no demo video: publish it

Your goal and your plan conflict. A hint nobody can read is not a hint. Vendors can't respond to a penalty they don't know exists. They only see "we rank lower" and read it as arbitrary.

- **The skill says the same.** "Undisclosed ranking penalties… reads as arbitrary when discovered. Fix: if you rank-penalize, publish it."
- **The skill's own benchmark discloses it.** The one operator that does this (Chrome Web Store, for a promo tile) states it: "items without it are ranked below items that have one."
- **Disclosure doesn't weaken the lever.** Vendors who want the rank will add the video. That is the behavior you want.
- **Discovery is the real risk.** A hidden penalty that gets noticed damages partner trust, which is the thing the standard exists to build.

The penalty itself is a fine choice, because you already have ranked search. The skill calls it a starved option that only works when ranking exists, and it exists. Keep the video optional so the listing publishes without it and ranks below listings that have one.

Paste-ready section:

> **Demo video (optional, affects ranking)**
> A demo video is optional. Listings without one are published, but rank below otherwise comparable listings that have one in Quillrock marketplace search. [State the mechanism here, e.g. "a tie-breaker among results of similar relevance" or "a fixed ranking adjustment". Say which.]
> A video counts if it:
> - is a public link,
> - runs [N] seconds or less,
> - has captions on,
> - shows the app's actual UI, and
> - contains no marketing footage [adjust to match your answer to Q4].
>
> This applies to new listings from [date] and to existing listings from [date + notice runway].

Fill in these before you publish:
- **N (the video length cap).** Set it from who evaluates a listing before install. The benchmarked ceilings run from 30 seconds (diligence buyers) to 2–3 minutes (self-serve). Don't average them.
- **Mechanism wording.** I can't say what your ranker actually does, so I left a placeholder.
- **Notice runway.** The skill requires one for any new requirement applied to already-listed apps.

## Gate check against the skill's five rulebook gates

- **Gate 1 (objective reject criteria per field):** the video criteria above are self-checkable.
- **Gate 5 (badge display and currency rules):** not touched by this change.
- **Gates 2–4 (one geometry per asset, taxonomy cap, decay trigger):** can't verify without the rest of your draft.

## Open questions

1. Is the video evaluated by self-serve installers or by an admin doing diligence? This sets N.
2. Do you want it **optional with ranking penalty**, as above, or **required**? Required gives a hard guarantee, but costs submitter friction and rejections.

Answer 1 and I'll fill in N and the tone rule.