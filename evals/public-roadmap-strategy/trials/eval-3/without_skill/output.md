# Pinnacle Ledger public roadmap: ready to publish

I split your list into what can go in a public repo this week and what has to wait. The NDA list and a public list are different documents. A GitHub repo is indexed and cached, and deleting a file later doesn't remove it from clones, forks, or caches.

## Publish now (4 items)

### `ROADMAP.md`

```markdown
# Pinnacle Ledger Roadmap

Directional, not a commitment. Priorities and timing change. No dates are promised.

## Now

### Key rotation v2
- **Area:** Security / API
- **Status:** In progress
- **Summary:** An improved key rotation workflow for API credentials.
- **Feedback:** Open an issue with the `key-rotation` label.

## Next

### Bulk export of ledger data to your warehouse
- **Area:** Data / Integrations
- **Status:** Planned
- **Summary:** Export ledger data in bulk to your own data warehouse.
- **Feedback:** Open an issue with the `data-export` label.

### Multi-entity consolidation
- **Area:** Core accounting
- **Status:** Planned
- **Summary:** Consolidated reporting across multiple legal entities.
- **Feedback:** Open an issue with the `consolidation` label.

### Configurable SAML attribute mapping
- **Area:** Identity / Enterprise
- **Status:** Planned
- **Summary:** Map SAML attributes from your identity provider to Pinnacle Ledger user fields.
- **Feedback:** Open an issue with the `saml` label.

## Later

### Platform infrastructure upgrades
- **Area:** Platform
- **Status:** Exploring
- **Summary:** Ongoing database and service-architecture work to improve reliability and scalability.
```

The status labels (Now, Next, Later, In progress, Planned) are my placeholders. Set them from the real Jira state.

## Hold back (5 items)

| Ticket | Why it stays out | When it can go public |
|---|---|---|
| PL-301 auth token replay | This is an unfixed weakness from your SOC 2 audit. Publishing it hands attackers a lead, and SOC 2 findings are usually confidential. | Never as a roadmap line. After the fix ships, announce it through a release note or security advisory. |
| PL-287 v1 endpoint sunset | Nobody has been told. Customers on v1 should hear it from you directly, not from a repo. | After customer notification. Then publish with a dated deprecation timeline and a migration guide. |
| PL-312 pricing and Growth tier | Unannounced pricing leaks to customers and competitors. It also isn't a product roadmap item. | At the pricing announcement, on your pricing page. |
| PL-298 Tarnbrook Bank sync | The partner hasn't announced. Naming them breaks the partner's announcement timing, and the NDA briefing logic doesn't carry over to a public repo. | After the joint announcement. |
| PL-305 Harrowgate Insurance | A named customer and a renewal promise are confidential. I kept the generic feature in the list above, with no customer name. | Keep the name out permanently. Check that the generic entry doesn't signal the renewal timing. |

I changed two items on purpose:
- **PL-320:** I dropped "split the billing service" and the Postgres version. They are internal detail and add no customer value. The generic infrastructure line stands in for them.
- **PL-305:** The public line is the feature only.

## Before you publish

1. **Account team check on PL-305.** Confirm Harrowgate's contract allows the feature to appear publicly.
2. **Security sign-off.** Have them confirm that "Key rotation v2" doesn't hint at PL-301. If the two are linked, move it to "Later" or reword the summary.
3. **Keep the Jira export out of the repo.** Don't commit it, even in history. Jira exports carry assignees, comments, and linked issues.
4. **Scrub commit history and metadata.** Use a fresh repo with a single clean commit. Check that file names, branch names, and labels carry no ticket IDs (PL-xxx) or customer names.
5. **Keep NDA content separate.** Store the full list with partner names in a private repo or a briefing deck, not a private branch of this repo.

If you want, I can draft the post-fix security advisory for PL-301 and the v1 sunset announcement with a migration timeline, ready to use when each is cleared.