# Sample-repo archive rules (draft)

## Before you apply the VP's rule

⚠️ Don't run it as written. Four repos in your list break it, and the rule has two flaws.

1. **Delete is irreversible, archive is not.** Replace "delete under 10 stars" with "archive, then review for deletion". Stars measure popularity, not harm or use.
2. **Commit age is a weak signal for a sample repo.** A stable sample needs no commits. Use the evidence gates below.
3. **Verify the "16 of 38".** I have not seen your repo list. Check whether 16 is the union of both criteria or only one.
4. **Archive does not remove forks.** Hundreds of forks stay live, keep their code, and keep working. Archiving hides nothing.

## Rules

**R1. Default action is archive. Never delete.**
- Delete only after a repo has been archived for 6 months, has zero inbound links, and a named owner signs off.
- Public repos with forks are never deleted. The forks detach and keep the code, and you lose issues and history.

**R2. Candidate filter: flag, don't act.**
- Flag a repo if it has no commits in 18 months, or fewer than 10 stars. Flagging only opens a review.

**R3. Hold gates. Any "yes" blocks archiving until it is resolved.**
1. Does it have an open security issue or a leaked-secret history?
2. Is it tied to a dated event, such as an SDK EOL or a launch?
3. Is it linked from external material, such as partner decks, docs, blog posts, or package READMEs? Search your docs and ask partner managers.
4. Does it have a deploy button, template link, or one-click flow?
5. Does it have more than 50 forks or active clones? If yes, notify via README and an issue before archiving.
6. Does it have an open PR or issue from an outside user?

**R4. Archive procedure, in order.**
1. Add a README banner: status, date, reason, and the replacement repo.
2. Update the repo description to start with "Deprecated" or "Archived".
3. Add the topic `deprecated`.
4. Remove or redirect inbound links in your docs, and remove any deploy button.
5. Close or answer open issues and PRs with a pointer.
6. Archive. Log the repo, date, owner, and reason in one tracking file.

**R5. Cadence.** Review quarterly. Each archive needs one named owner and one reviewer.

## The four named repos

| Repo | Decision | Reason and next step |
|---|---|---|
| `deploy-shopfront` | 🔴 **Security incident first. Do not delete.** | The key sat in build logs for about a year and roughly 200 people deployed it. Deleting the repo does not fix any of that. The leaked keys and logs live in each deployer's account, and every fork still carries the logging code. |
| `cart-sdk-v2-examples` | 🟠 **Hold until SDK v2 EOL, then archive.** | Archiving early blocks fixes while v2 users still depend on the examples. On the EOL date, add a v3 migration link to the banner and archive. |
| `checkout-react` | 🟠 **Hold. Contact the partner first.** | The URL appears in a partner onboarding deck. Archiving keeps the link working but closes issues and PRs for partner users. Agree on the new location with the partner owner and confirm the code still works. |
| `storefront-legacy` | 🟢 **Mark and archive now, regardless of the filters.** | It's an unmarked dead repo that coding assistants recommend. Add the deprecation banner, the `deprecated` topic, and a replacement pointer, then archive. Keep it public and undeleted so the pointer stays visible. |

### `deploy-shopfront` steps
1. Revoke or rotate every API key that could have been written to logs. Check whether it was one shared key or one per deployer.
2. Fix the template so it no longer logs the key, and ship that fix first.
3. Notify the roughly 200 deployers and tell them to rotate keys and purge or restrict their build logs.
4. Check your API access logs for the key's use over the exposure window.
5. Keep the repo as evidence. Then apply R4 and remove the deploy button from docs.
6. Write a short incident record. Get the security owner's sign-off before anything public.

## Open questions for you
1. Which 12 other repos are in the 16? I'll run them through R3.
2. Was the `deploy-shopfront` key per deployer or shared?
3. Does the partner for `checkout-react` need to approve the move?
4. Is `storefront-legacy` among the 16, or outside them?
5. Who is the named owner for each archive?