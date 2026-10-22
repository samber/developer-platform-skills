# Pellworth public API GA: can we ship Thursday with all 9 review items open?

**No, not all 9. You can ship with 5 open, but not with the 4 style-guide violations open.** Each of those four has to be fixed before Thursday or carry a recorded deviation signed by the VP.

I worked from your description only. I haven't seen the review, the spec, or the style guide.

## Why the 9 split into two groups

The review method I followed has two buckets, and only one blocks a launch.

- **Must-change** is a violation of a written rule, here your internal style guide. A public GA is a blocking review, and the ship gate is zero Must-change items open. The only alternative to fixing one is a documented deviation with a recorded rationale.
- **Improvement** has no rule behind it. Improvements may ship open, always.

| # | Item | Bucket | Thursday |
|---|---|---|---|
| 1 | Casing inconsistency (1 of 2) | Must-change | Fix, or sign a deviation |
| 2 | Casing inconsistency (2 of 2) | Must-change | Fix, or sign a deviation |
| 3 | Verb in URI | Must-change | Fix, or sign a deviation |
| 4 | 200 with an error body | Must-change | Fix, or sign a deviation |
| 5–9 | "Add a next link", "expose expand parameters", and three similar suggestions | Improvement | ✅ Ship open |

The five Improvements are the reviewer's taste with no rule cited. The method treats a blocking comment with no cited rule as a defect in the review, so these five cannot block. Pagination links and expand parameters are also additive, so adding them later breaks no one.

## Why "clean up in the first maintenance release" fails for the four

Fixing the four after launch is not a cleanup. It is a breaking change to a public API, and nobody can list or contact the clients of a public API.

- **200 with an error body.** Clients will write error handling around that exact behavior. Switching to a 4xx after GA breaks their handling. The checklist calls this the worst status-code finding.
- **Casing.** Renaming fields after launch means serving both names and deprecating one on a published schedule, so you carry two field names on every affected response. The rule is consistency, so which casing wins matters less. The majority casing on your surface is the cheapest pick.
- **Verb in URI.** The fix is a new route plus a deprecated alias, and the old route lives on until clients migrate.

Today, if no external client depends on these behaviors yet, each fix is a simple pre-launch change. After Thursday, each one needs the deprecation process. The press embargo adds to this, because launch posts, docs and sample code will print the wrong field names and route in public.

## Recommendation

1. **Fix all four before Thursday.** Engineering finished three weeks ago, so ask them for an estimate today. Casing is often a serialization setting, and the route rename is small. I can't judge the effort from here.
2. **Ship the five Improvements open.** Put them in the maintenance-release backlog.
3. **If engineering can't finish all four, record a deviation for the cheapest to defer.** That is the verb-in-URI route, because an alias plus deprecation is the least painful retrofit. Fix the 200-with-error item and the casing items first, since they hurt clients most after launch.
4. **Write each deviation down.** The record has the rule, the reason (expediency, a launch date that can't move), an owner, and a removal date through your versioning policy. The VP is the right person to authorize the exception. They should do it knowing it makes the later fix a breaking change.

## What I'd confirm before you commit

- **Are there existing clients?** This is the key question. Any beta users, partners, your own frontend or SDKs, or published examples that rely on the current behavior make the fix a breaking change even before GA.
- **Are the four citations accurate?** Check that each one points to a real, adopted style-guide rule. A cited rule that turns out to be aspirational drops that item to Improvement.
- **Did the reviewer cover everything?** The ship gate also needs all eight dimensions walked: URIs, methods, status codes, field naming, pagination, filtering, errors, and backward compatibility. It needs one-line checks on versioning, idempotency, auth, rate limits and docs too. Nine findings don't show full coverage, so ask the reviewer which dimensions they walked.
- **Does any of the five actually break a style-guide rule?** If one does, such as an unpaginated collection or a silently ignored filter, it becomes a Must-change.

## For next time

This review arrived after the code was finished, which is the late-gate failure mode. Reviewing the spec before implementation would have made all four of these cheap fixes. For the next release, trigger the review at beta, on the spec.