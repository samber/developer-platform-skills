# Hartwell Data: PHP SDK decision brief

**Recommendation:** Concede the destination and push back on the process. The three numbers don't justify archiving this sprint, but they do justify moving the engineer onto Go this sprint. I'd propose that instead.

I skipped the skill's one-question-at-a-time interview because you asked for the full answer in one pass. Everything below rests on a few assumptions about Hartwell. The section "What would flip this" lists the ones to confirm.

## Why the three numbers don't decide it

- **180 vs 400k vs 260k are download counts, not accounts or revenue.** They include CI reinstalls, mirrors and bots. They say nothing about who is paying.
- **The VP is probably right about direction.** PHP sits far below any sensible traffic threshold, so it fits the skill's "starved option" (an official SDK in a low-traffic language). It loses every efficiency comparison unless something specific promotes it.
- **The missing number is exclusive usage.** The skill warns against "EOL by gut feeling": small is not the same as safe to drop. The decisive figure is revenue from accounts that use only the PHP SDK, because those customers have no other path to your product. A few PHP-only accounts could be worth more than a lot of Python downloads.
- **"This sprint" breaks the sequence.** The playbook order is final release, then announcement, then archive. Published announcement-to-archive windows run 6 to 24 months. Archiving in one sprint skips the announcement entirely.

## What to do, in order

1. **Reframe with the VP (15 min).** The goal is to free the engineer for Go. That doesn't require archiving the repo. Archiving is the last step of a sunset, not the first.
2. **Pull five numbers (about 1–2 days, longer if you have no client telemetry).**
   - Share of API traffic from PHP clients, using `User-Agent` or SDK headers. If you don't have this, say so. It is the first thing to instrument.
   - Accounts that use only the PHP SDK, and the revenue attached to them. This is the Sentry-style check.
   - Open or lost deals where the customer named PHP, from sales or CRM.
   - How much direct-HTTP PHP traffic exists without the SDK. If it's large, PHP users exist and don't rely on the SDK.
   - Real maintenance cost over the last 12 months: engineer-hours, open issues, security patches.
3. **Apply a written rule.** The thresholds are self-set. No vendor publishes a numeric one, so label them as yours.
   - **Archive path:** PHP is under a sustained double-digit share of traffic, has no meaningful exclusive revenue, and has no named deal requests. Then run the sunset below.
   - **Keep path:** There is material exclusive revenue or repeated named deal requests. Then keep PHP, but cut its cost (see the cost-cutting options below).
4. **Move the engineer now in either case.** Put PHP in maintenance mode: security and critical fixes only, no new features. That removes the staffing conflict immediately and doesn't commit you to a shutdown.

## If the data says archive: the sunset

1. Build the evidence file from step 2 and get your manager's approval on record.
2. Name a successor path. Plaid's model fits: publish the OpenAPI spec and point PHP users at open-source generators. Also list any community PHP client with an explicit non-guarantee.
3. Cut a final release pinned to current dependencies.
4. Announce with a fixed timeline. For a very small user base, 6 months is the floor the skill cites (AWS gives at least 6 months' notice before maintenance mode). Azure's advice for tiny user bases is to work with those users individually.
5. Add a pinned deprecation issue stating why, the alternative and the dates. Also add a README banner, a docs banner and the Packagist abandoned marker.
6. Tell support and GTM.
7. Archive only after the window closes. Six to twelve months later, de-index the old docs (keep the URLs reachable) and redirect them to the successor.

## If the data says keep: cheaper options

- **Generate PHP from the OpenAPI spec** if the spec is a real source of truth. That removes the dedicated engineer.
- **Demote it to a community tier.** Write the promotion gate so it can come back later.
- **Keep it as a lower-tier official SDK** with a stated support level.

## What would flip this

These are the facts I assumed because I couldn't ask:

- **Your developer vertical.** Fintech and commerce platforms (Stripe) ship PHP officially. AI and dev-tools platforms don't. If your buyers are commerce or enterprise PHP shops, 180 downloads may understate importance, and the exclusive-usage check matters more.
- **Whether the spec is linted in CI.** If it is, the generate-PHP option is cheap. If it drifts, fix that first.
- **Whether a deal is pending.** A named PHP deal request outranks the telemetry.
- **Whether the engineer's Go move has a hard deadline.** If it does, step 4 already satisfies it.

## Script for the VP

> "You're right that PHP is the smallest SDK by a wide margin, and I agree the engineer should move to Go. I'm asking for two weeks to check one number: revenue from accounts that use only the PHP SDK. If it's low, we announce and archive on a 6-month timeline. Meanwhile the engineer starts on Go now and PHP drops to security-only maintenance. This avoids breaking any customer who has no other path to us."

## Gate

The strategy isn't finished until all seven steps in the skill end in a written, approved policy. This brief covers steps 1, 3, 6 and 7 for PHP only. The language order, build model and versioning steps are still open. Do those after this decision.