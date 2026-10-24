Start with the CEO's "why". Don't start with a roadmap format. A public roadmap is a commitment device, so settle the purpose and the rules before you draft any content.

## Step 1 of 6: ask the CEO one question (15 min)

"What outcome do you want from this roadmap?" Ranked options:

1. **Trust with existing integrators.** They need predictability and deprecation warning. This is the usual real driver.
2. **Adoption by new developers.** They want to see momentum and a direction to bet on.
3. **Partner and enterprise sales support.** Buyers want proof that the platform has a future.
4. **Fewer "when will X ship" tickets.** This is support deflection.

Recommendation: pick #1 as primary. It sets what you can safely publish. Also ask what triggered the request, because a lost deal, a competitor's roadmap, or a customer complaint each point to a different format.

## Step 2 of 6: decide what you will not promise (1 hour, with product and engineering leads)

- **No dates.** Use Now / Next / Later. Dates turn into broken promises.
- **Commit hard only to deprecations and breaking changes.** Give a fixed notice window, for example 12 months. This is the part integrators value most.
- **Name an owner and a publishing cadence.** Review quarterly. A stale roadmap does more harm than none.
- **Decide the removal policy.** If an item is dropped, say so publicly and give a reason. Silent deletion costs trust.

## Step 3 of 6: audit the inputs (half a day)

1. Collect internal API plans and rank them by developer-facing impact.
2. Tag each item: **safe to publish**, **needs legal or partner clearance**, or **internal only**. Check for NDA'd partner work and security fixes before disclosure.
3. Pull the top 20 asks from support tickets, community channels, and sales notes. Developer demand should shape the list, not only engineering plans.
4. List current deprecations and their dates.

## Step 4 of 6: choose the format (1 hour)

| Option | Fit |
|---|---|
| GitHub Projects board or issue labels | Developer-friendly, supports voting and comments. Best if you already run public repos. |
| Page on the docs site | Full control over wording. Pair it with the changelog. |
| Dedicated tool (Canny, Productboard) | Voting plus status. Adds a vendor. |

Recommendation: a docs-site page (Now / Next / Later), linked to the changelog, plus a public feedback channel. Add an RSS or email subscription.

## Step 5 of 6: draft v0 and test it (2 to 3 days)

1. Draft 8 to 12 items. Each gets a problem statement, not a feature spec, and a status.
2. Add a "How to read this roadmap" disclaimer and the deprecation policy.
3. Show it privately to 3 to 5 friendly integrators and 1 enterprise customer. Ask: "What would you change in your plans because of this?"
4. Run a final legal and security check.

## Step 6 of 6: launch and measure (ongoing)

- Announce through the changelog, email, and community channels.
- Track roadmap page views, subscriptions, feedback submissions, and "when will X ship" support tickets before and after.
- Review the roadmap every quarter. Mark each item shipped, moved, or dropped.

## Main risks

- **Over-promising.** Mitigation: no dates, plus the disclaimer.
- **Competitors reading your plans.** Publish problems and themes, not designs.
- **No owner.** Without one, it goes stale within two quarters.
- **Showing only wins.** Include dropped items, or trust won't build.

## Time estimate

About 1 to 2 weeks of part-time effort from one product owner to reach a v0 launch. The CEO conversation and the clearance check are the likely blockers.

**Next action (2 minutes):** send the CEO this message: "Before I draft: is the main goal integrator trust, new-developer adoption, or sales support? And what prompted the ask?"