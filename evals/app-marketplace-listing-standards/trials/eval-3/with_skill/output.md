# Northsend taxonomy recommendation

## Recommendation

Ship a small fixed category list with a hard cap of two categories per listing, one marked primary. Reject the plan of eight categories plus unlimited free-text tags. Fix the 40 misfiled listings first, through a notice window and then a browse downgrade, not by delisting. Add capped structured tags later, once search overtakes browsing.

The interview questions went unanswered, so this rests on assumptions. They are listed at the end, and each one can change a part of the answer.

## Why not eight categories plus unlimited tags

The skill puts "uncapped self-selection" on its deleted list, not its demoted list. Uncapped multi-select taxonomies degrade into every listing claiming every plausible tag, until categories stop meaning anything. The proposal fails in two places:

- **Eight categories is effectively uncapped.** The benchmarked caps run from one category plus two industries (Salesforce) to two of ten (Atlassian). Eight is four times the loosest benchmark.
- **Unlimited free-text tags is the same failure on the search side.** The benchmarked search layers are capped and structured. Shopify allows 5 search terms, one idea per term, and rejects "email marketing for leads" for stacking two ideas. Free text with no cap or idea rule makes search results noisy.

The proposal also treats "nobody finds us" as a vendor-side labeling problem. The more likely cause is that Northsend's own browse surface is broken (see the 40 misfiled listings below), and more labels would make that worse.

Each vendor claiming up to eight categories also lowers the value of every category page, because every category fills up with loosely related apps. Vendors who stay honest are then outranked by vendors who don't, which teaches everyone to over-claim.

## What to ship

**1. Category list**
- Use about 10 cross-functional categories organized by the buyer's job to be done, not by technology. Atlassian's flat list of 10 is the benchmarked reference. It is a calibration point, not an industry standard.
- Hard cap of **2 categories per listing**: one primary and one optional secondary.
- Publish a one-sentence definition per category, so a vendor can self-check a choice and a reviewer can enforce it.
- Make a category mismatch a named content-rejection trigger: "the listing's categories must describe what the app does".
- Don't give any category extra vendor-purchasable placement.

**2. Decay rule: staleness downgrade, not delisting**
- A listing whose categorization has drifted from the app is marked **uncategorized** and drops off every browse and filter surface. Atlassian runs this exact mechanism.
- It is soft, self-correcting and automatable. The vendor fixes it by updating the listing, so there is no delisting dispute.
- Name "out-of-date listing content" as an explicit rejectable violation in the published policy.
- Give the trigger an owner and a consequence, which is measurement gate 4: the owner is the marketplace content-review lead, and the consequence is the browse downgrade above.

**3. Search layer: stage it, don't ship it yet**
- The skill's promotion condition is that search overtakes browsing as the discovery path. You said browsing is still the main path and search is climbing, so you haven't hit that condition.
- Write the trigger down now, so the decision isn't re-litigated every quarter. Promote when search sessions reach or exceed browse sessions, measured over a sustained period you choose.
- On promotion, add structured tags on top of categories:
  - per-category feature tags chosen from an operator-defined list
  - a handful of search terms, each capped and limited to one idea per term
- As starting values to tune, copy Shopify's shape: 5 search terms, and a per-category feature list with a cap you set. These are proposals, not standards.
- Never add an unlimited free-text field.

**4. Visibility for vendors who feel invisible**
- Offer operator-curated layers instead of more categories: editorial collections, "works with" labels and persona groupings.
- The skill ranks this as the highest discovery value and also the highest standing editorial cost. Treat it as a later promotion, justified if you want the catalog to compound in value as it grows.
- Keep placement unpurchasable. Once curation is sellable it stops being a discovery signal and becomes inventory.

## The 40 misfiled listings

Forty of 340 is about 12% of the catalog. They are misfiled because of Northsend's taxonomy rewrite, not because of vendor behavior. That changes how you enforce the rule.

1. **Before any downgrade, the operator proposes a remap.** Northsend suggests a new category for each of the 40, and the vendor confirms or corrects it.
2. **Give a notice runway before the downgrade takes effect.** The skill is explicit that new content requirements applied to already-listed apps need one. Downgrading vendors for a mismatch Northsend caused, with no warning, burns the trust the standard exists to build. Pick the runway length yourself. The skill gives no number.
3. **After the runway, apply the downgrade rule as written.** Any listing still unconfirmed is marked uncategorized.
4. **Check the complaint first.** It's possible that many of the vendors saying "nobody finds us" are in this group of 40. They are invisible in the browse path, which is how most buyers find apps. I haven't verified this, and you can check it in one step by comparing the complaining vendors against the list of 40.

Running the rule on the existing catalog also shows how the staleness downgrade will behave at scale. If 12% mismatch after one taxonomy rewrite, expect more drift with each future rewrite, so budget for it.

## Where each option sits

| Option | Verdict |
|---|---|
| Fixed list, cap of 2, staleness downgrade | Ship now. This is the default rung and the efficiency leader. |
| Structured tags on categories | Stage it, with the trigger written down. |
| Operator-curated layers | Later, if you want a compounding asset. Keep it unpurchasable. |
| Eight categories plus unlimited tags | Don't ship it. Uncapped self-selection is a deleted rung. |

## Rulebook gates

- **Gate 3:** a hard per-listing cap of 2 satisfies it.
- **Gate 4:** the staleness downgrade, with an owner and a stated consequence, satisfies it.
- The other gates cover fields outside this taxonomy question.

## KPIs to track once live

- Share of the catalog that is uncategorized.
- Share of the catalog stale beyond your freshness SLA. For a worst case, the skill suggests Adobe's 12-month auto-removal rule as an internal reference, even though nothing external forces it.
- Search sessions versus browse sessions, which is the promotion trigger for tags.
- Rejection-reason distribution. A rising "unclear content" share signals spec ambiguity, not submitter failure.

I'd also add zero-result search rate and per-category listing counts. These are my suggestions, not from the skill, and they would show early whether search is failing or one category is overcrowded.

## Assumptions to confirm

- **Maintenance model:** vendors maintain their own listings. If your team maintains them, the spec can be less strict.
- **Curation rung:** you run an open or hybrid marketplace and have not chosen a hard gate.
- **Buyers:** they self-serve install. Admin or committee diligence would not change the taxonomy, but it would change the media and description rules.
- **Release cadence:** no versioned platform releases. If Northsend ships them, version-currency enforcement becomes available as a stronger decay rung.
- **Deadline and effort:** no hard date, and a modest effort ceiling. A near deadline favors the policy-text rungs above. A compounding mandate favors promoting the curated layers sooner.
- **Search versus browse:** the numbers are directional. Please confirm how you measured both before setting the tag-promotion trigger.

I can draft the published category definitions and the rejection-trigger text next, if you want them.