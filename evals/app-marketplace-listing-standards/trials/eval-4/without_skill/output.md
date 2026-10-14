# Cadenza partner directory: staleness policy

## Position on the $200 fee

The fee won't fix this, and the audit shows why. Every one of the ~600 listings has paid it, and 41% (~246) are still stale. The fee says "I'm listed". It doesn't tell a partner their link broke or their screenshot aged out. Nobody has been showing partners the problem, and nothing has happened when they ignored it.

Use the fee as the lever, not as the fix. It funds a health dashboard for partners and ties renewal to a short attestation. Detection and consequences have to exist either way.

## Principles

1. **Detect automatically, and tell the partner first.** No one is penalised for a problem we haven't shown them.
2. **Degrade before delisting.** Delisting is the last step, not the first. Most staleness is fixed by hiding a broken element, not removing the listing.
3. **Every listing runs on its own clock.** Deadlines start at that listing's first notice. A catalog-wide cliff can't recur.
4. **Throttle enforcement.** A monthly cap bounds the damage if the response rate is worse than expected.
5. **Anchor integration staleness to the API schedule you already publish.** No second calendar for partners to learn.

## Three staleness types, treated differently

| Type | Detection | Severity | Fix effort for partner |
|---|---|---|---|
| **Dead link** | Automated weekly check | Objective, user-facing | Minutes |
| **Stale screenshot** (old Cadenza UI) | Screenshot tagged with the UI release it shows | Cosmetic and misleading | Hours |
| **Integration on deprecated API** | Derived from API/OAuth app telemetry, not self-declared | Functional: it will break | Days to weeks |

### 1. Dead links

- **Link tiers.** Critical: install/connect, docs, support. Minor: marketing site, social, blog.
- **What counts as dead.** 3 consecutive weekly failures from two different egress points, so bot-blocking and transient outages don't trigger it. A redirect to a different domain's homepage counts as dead.
- **Ladder** (days from the first confirmed failure):
  - **Day 0:** the partner gets an email and a dashboard alert. The link is flagged internally.
  - **Day 14:** reminder. The listing's broken link is replaced with a "link unavailable" state, so visitors don't hit a 404 on our page.
  - **Day 45:** the listing drops out of search ranking boosts and "featured" slots.
  - **Day 90 (critical links only):** the listing is hidden from browse and search. It stays reachable by direct URL, so existing customers aren't stranded.
  - **Day 180:** delisted.
- Minor-tier link failures never go past the Day 14 step.

### 2. Screenshots

- **Staleness is measured in UI generations, not calendar age.** A screenshot is stale when it shows a Cadenza UI more than 2 major UI releases back. Tag each upload with the UI version, from the upload date or a quick partner confirmation.
- **Stale screenshots are hidden, never grounds for delisting.** The listing stays up with its logo and description. The partner sees "your screenshots are hidden, upload new ones" in the dashboard.
- **Cadenza shouldn't make partners do this alone.** Ship a current-UI screenshot kit: frames and a sandbox tenant they can capture from. Without it, the fix costs partners hours and many won't bother.
- Listings with zero visible screenshots rank lower in browse but aren't otherwise penalised.

### 3. API version compatibility

Reuse the deprecation schedule. Each version has a published sunset date `S`.

| State | Trigger | Listing treatment |
|---|---|---|
| **Current / Supported** | Built on a supported version | Normal |
| **Upgrade needed** | Version deprecated (announced) | Dashboard notice and email to the partner. No public change. |
| **Deprecated badge** | `S` minus 90 days | Public "Built on a deprecated API" badge. Dropped from featured slots. |
| **Hidden** | `S` reached, still on the sunset version | Hidden from browse and search. The integration is functionally broken, so this isn't a punishment. |
| **Delisted** | `S` plus 180 days, no upgrade | Removed |

- Link-only listings (no API usage) are exempt from this track.
- Listings whose API usage shows no real traffic get a "confirm still active" prompt instead of the badge.
- Each new six-month version should reuse the same notice templates. The cost per cycle is low once the machinery exists.

### Annual attestation (renewal gate)

At fee renewal, the partner confirms three things: contact owner, listing description accuracy, and that the integration is still maintained. This takes about two minutes and is the one place the fee gets teeth. Because renewals fall on each listing's anniversary, the workload spreads across the year.

## Clearing the backlog without delisting a third

The 246 flagged listings are an inherited debt. They get an amnesty path, not the steady-state clock.

### Step 0, weeks 0 to 2: classify before telling anyone

Break the 41% down. I don't know the split, so this step decides everything else.

- Dead links versus screenshots only versus both.
- Critical-tier link failures versus minor-tier.
- Traffic per listing (views and installs).
- Listings with a verifiable API integration versus link-only.

Expect many listings to be screenshot-only or minor-link-only. Under this policy those lose no visibility beyond the screenshots, so the real at-risk group is probably much smaller than 246. Count it before announcing anything.

### Step 1, weeks 2 to 4: auto-fix and notify

- Auto-repair what we can: follow redirects to a clearly moved page, hide dead minor links and stale screenshots.
- Send every partner with a flag a single message: what's wrong, exactly where, and the date their clock started.
- Ship the screenshot kit and the dashboard first, so a partner who clicks through finds something to act on.

### Step 2, weeks 4 to 12: staggered cohorts

- Split the at-risk listings into 3 cohorts by traffic, highest first. High-traffic partners are most likely to respond, and their breakage hurts customers most.
- Each cohort's Day 0 is a week apart. No cohort reaches a hide step before day 45 of its own clock.
- Human outreach (email from a named person, or a call) for the top-traffic listings before any ranking penalty applies.

### Step 3: enforcement throttle

- **Cap: at most 5% of the catalog (about 30 listings) moves to "hidden" in any calendar month**, whatever the ladder says. The overflow waits for the next month, oldest first.
- Delisting in the backlog window requires a human sign-off per batch.
- If the first month's hide count lands above the cap, pause and review. The thresholds may be wrong, or the detection may be mislabelling working links.

### Illustrative outcome (assumptions, not data)

If 246 flagged listings split roughly 60% cosmetic-only (no real loss), 40% with a critical dead link, and about half of the second group fix within the notice window, the hidden count after month 3 would be around 50, or about 8% of the catalog. A third of the catalog (~200) is only reachable if almost no one responds at all. Replace these guesses with real numbers after Step 0 and again after wave 1.

## Reinstatement and appeals

- A hidden listing is reinstated within 2 business days of a verified fix, at no extra charge.
- A delisted partner can relist at no fee for 12 months after delisting if they pass a fresh health check.
- Delisting does not refund the fee. Hiding doesn't pause the term unless the problem was on our side (our checker misflagged it, or our UI link was wrong). Leadership should confirm this fee treatment, because it affects partner trust.

## Ownership and metrics

- **Owner:** one named person on the partner/ecosystem team owns the policy. Engineering owns the checker and the telemetry lookup.
- **Weekly:** count of listings per state (healthy, flagged, hidden, delisted), plus false-positive reports from partners.
- **Targets by month 6:**
  - Share of listings with at least one flag: below 10%.
  - Median days from first notice to fix.
  - Percent of notices that got a partner response.
  - Number of listings hidden or delisted, against the cap.
- **Review point:** after wave 1 (about week 8), re-tune thresholds using the real response rate before wave 2 runs.

## Decisions I need from you

1. Does the audit data already separate dead links, screenshots, and traffic per listing? If not, Step 0 is the first task.
2. Can we reliably tell which API version a partner's integration uses from telemetry? The API track depends on it.
3. Fee treatment on hide and delist (see Reinstatement). It's your call, and leadership will have views.
4. Is 5% per month the right enforcement cap, or should it be tighter during the first quarter?