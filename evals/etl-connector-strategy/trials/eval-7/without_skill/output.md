# Decision: conditional yes. Reject the framing, not the tap.

**Sign off on the tap if the five conditions below are met. Do not sign off on "tap instead of the platform review."** I couldn't check your API, your demand data, or the hub's listing rules. The answer rests on what you told me.

## Why the framing is wrong

- **They are two different bets.** The tap is a vendor-built integration. It is one connector you maintain, and it is cheap and reversible. The two-month platform review is a different channel, and I don't know what it gates. It may reach buyers the tap never will.
- **The tap does not need to win against the review.** Run both unless the review costs real engineering time you'd have to trade away.
- **"Zero budget" is wrong.** Three weeks of Friday time covers the build. The cost that follows is keeping the tap working against your own API changes and customers' pipelines, indefinitely.
- **"Listed immediately" is unverified.** The tap ships in about three weeks at best, and then the hub may add its own review or PR step. Check the hub's listing requirements before you promise a date.

## What the tap is good for

- Your 90 customers run their own open-source ELT. A tap puts you where they already work, with no new tool to adopt.
- It is also cheap discovery. Listing usage tells you which data customers actually pull out of Brightloom.
- Tomas wants to do it. A motivated builder who knows the backend is a real asset.

## Conditions for sign-off

1. **Count the demand first.** Name at least five customers who have asked for this, or who have built their own export glue. This is a default threshold, not an industry number. If you can't name five, the tap is a guess, and a cheap one.
2. **Use only the public, documented API.** No privileged internal path. If the tap needs an endpoint you wouldn't publish, stop and decide whether to publish it. Every endpoint it relies on becomes a frozen contract.
3. **Name an owner who isn't Tomas.** Tomas needs a backup, and the maintenance has to be on someone's real roadmap, not a Friday hobby. A listed connector with no owner breaks silently when your API changes. Customers then blame Brightloom, not the tap.
4. **Write the support and deprecation terms before listing.** One paragraph is enough:
   - Who answers issues.
   - The response expectation.
   - How much notice a breaking API change gets.
5. **Review credentials and data handling.** Check how the tap stores API keys, which scopes it needs, and what it logs. A leaked key from a community connector is your incident.

## Kill criteria

Write these now, while stopping is still cheap. The numbers are my defaults, so replace them with your own if you have data.

- **90 days after listing:** fewer than 10 of the 90 accounts (about 11%) actively use it. Freeze it at maintenance-only.
- **Any quarter:** it breaks against an API change and no one fixes it within 2 weeks. Delist it or hand it off.
- **Maintenance hours** exceed what you budgeted for two quarters running. Re-decide.

## Open questions

- Does the platform review cover the same customers as the tap, or different ones? This decides whether they compete at all.
- What does the hub require, and how long does its listing step take?
- Is the public API stable and versioned today? If not, fix that before the tap, because the tap will freeze whatever it touches.

## Next steps

1. Tomas or you list the customers who asked for this (condition 1).
2. Name the owner and backup (condition 3).
3. Confirm the hub's listing requirements and review time.
4. If all three check out, start the build. Confirm the platform review stays on track in parallel.

If the demand list comes back under five, I'd park the tap and spend Tomas's Fridays elsewhere.