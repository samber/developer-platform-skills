# Can we ship Thursday with all 9 items open?

**Answer: no for 4 of them, yes for 5.** Fix the four style-guide items before Thursday. The five reviewer suggestions can wait for the first maintenance release.

I haven't seen the review itself, so this rests on your descriptions. Engineering should check the assumptions at the end.

## Why the split matters

Severity isn't the question. The question is whether we can fix an item after GA without breaking customers. Once the API is public, anything a client can depend on becomes a contract.

| Item | Fixable later without breaking clients? | Call |
|---|---|---|
| 2 casing inconsistencies | **No**, if they are field, parameter or path names. Renaming breaks every integration. | Fix before GA |
| Verb in URI | **No.** The path is the contract. Fixing it later means a new route plus a deprecation window. | Fix before GA |
| 200 with an error body | **No.** Clients will write "200 means success, else parse body" logic. Switching to 4xx later breaks them. | Fix before GA |
| 5 reviewer suggestions (`next` link, expand params, etc.) | **Yes**, if each one only adds something. | Defer |

Before GA, nobody depends on the current behavior, so a fix is just a code change. After GA, the same fix becomes a breaking change that needs a deprecation policy.

## The cost of fixing the four now

- This is likely days of work, not weeks. The rename and status-code changes are mechanical.
- The change touches more than the code. Update the OpenAPI spec, SDKs, examples, docs and any press or demo material that shows the old names.
- Press material is the hidden risk. The embargo is set, so any screenshot or snippet showing the old URI or field names needs a refresh.

## Why we shouldn't ship with the four open

- The "first maintenance release" label doesn't fit these fixes. A maintenance release promises no breaking changes, and these are breaking.
- We would have to bump the major version, ship a v2, or run a deprecation window. That means support burden and a visible "the GA API was wrong" story within weeks of launch.
- The inconsistencies would also be in every SDK and tutorial from day one.

## Why the five can wait

Most of them are additive. A `next` link in paginated responses and opt-in `expand` parameters add capability without changing existing responses. They fit a maintenance or minor release.

**Exception to check:** any suggestion that changes a default response shape is not additive. For example, embedding objects by default instead of IDs would be breaking. Engineering should confirm each of the five is purely additive. If one isn't, move it into the pre-GA group.

**Pagination:** if the API paginates without a `next` link, clients will hand-build offsets or cursors. That is still additive to fix, but document the current pagination clearly so customers don't rely on undocumented behavior.

## Plan

1. **Today and tomorrow:** engineering classifies all 9 items as breaking-if-changed or additive, and gives an estimate for each of the four.
2. **Monday:** VP of Eng makes the go/no-go call on the four.
3. **Tuesday:** code freeze for the four fixes. Regenerate spec, SDKs and docs.
4. **Wednesday:** run the integration tests and check press assets against the new names. The checks are green.
5. **Thursday:** GA ships.
6. **After GA:** the five suggestions go into the first maintenance release.

## Fallback if the four don't fit in the window

Don't ship them as-is and promise a cleanup. Instead, pick one of these:

- **Leave the offending endpoint out of GA.** Mark it beta or experimental, outside the stability promise, and keep it out of the press story.
- **Move the GA date.** A few days' slip costs less than a breaking change on a public API, but the embargo has to be re-coordinated. Treat this as the last resort.

Shipping all nine open is the one option I'd rule out.

## Assumptions to verify

- The casing issues are in names clients see (fields, params, paths), not internal naming. If they're internal, they drop to the deferrable group.
- The verb-in-URI endpoint and the 200-with-error endpoint are few, not systemic. If the 200-with-error pattern is the API-wide error convention, the fix is bigger and the fallback matters more.
- All five suggestions are additive.
- Nobody outside the company, such as design partners or beta users, already depends on the current behavior. If they do, the fixes need a heads-up to them.