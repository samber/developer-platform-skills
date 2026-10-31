# Brightpath on AppExchange: pricing path and re-review prep

## Short answer

1. **Don't treat "COA + auto-renew + card" as one rail.** Salesforce splits those across different rails, so check your PADA first.
2. **Check whether your PADA has GTM app terms.** Your deals are exactly what the GTM app is for, so net-new orders may be required to use it instead of COA. The GTM app allows no auto-renew and takes ACH, not cards.
3. **Cards through Salesforce means Checkout.** That is a listing change, and the listing goes back to approval.
4. **Yes, the prompt templates need work before re-review.** Summarising support cases passes untrusted text into a prompt, which is a named failure class. Harden and test them now.

## Assumptions

I could not ask, so these are assumptions. Please correct any that are wrong.

- Your PADA is offline and negotiated, since finance files everything through COA. I don't know whether it includes GTM terms or your product sits in the Partner Product Catalog.
- Billing is USD, per seat, 12 months, to US companies. I assume you invoice customers yourself.
- You have no Connected App or External Client App (ECA) used by more than two customer production orgs. Please confirm.
- "Next quarter" means Q1 2027 (January to March), about 9 weeks away.
- The March review passed on the current managed-released version, and the Agentforce AI details are on the listing.
- No re-review notice has arrived yet.

## Part 1: What should change for payments

### Each of sales' three asks, by rail

| Ask | COA (your current rail) | GTM app private offers | Checkout |
|---|---|---|---|
| New customers keep going through COA | Fits usage, tiers, multi-year and negotiated deals. Flat per-seat 12-month deals are not its sweet spot. | Fits "seat-based deals with new US customers." Net-new orders that qualify must use it. | n/a |
| Auto-renew everything | Set by your contract and PADA. Cancellations must be filed 30+ days before renewal† (COA blocks them within 5 days†). | **Not allowed:** 12-month orders, no auto-renew† | Subscriptions exist (monthly or annual)†. Whether they auto-renew is not confirmed; ask. |
| Customers pay by card | Offline billing, so your own processor is plausible. This is unconfirmed; ask. | **No:** NET30 ACH, paid upfront† | **Yes:** 15% of net revenue plus $0.30 per card payment† |

### What to do about the conflicts

1. **Ask your account manager this week (three questions):**
   - Does my PADA carry GTM terms, or is the product in the Partner Product Catalog?
   - If so, which of my new-customer deals must go through the GTM app instead of COA?
   - May I collect card payments under COA through my own processor, and is the PNR still owed on that revenue?
2. **If your PADA has no GTM terms:** keep COA. This is the least disruptive option. There is no listing re-approval and no new clickthrough PADA, and you keep your negotiated PNR rate†. Add auto-renew to your own contract, and add card collection only if the account manager confirms it.
3. **If your PADA has GTM terms:** the GTM app is mandatory for qualifying new US deals. That means 12-month orders, ACH, and no auto-renew on those deals. Sales' auto-renew and card asks cannot be met for them. Existing COA customers keep expanding through COA until renewal.
4. **Choose Checkout only if Salesforce must run card collection and subscription billing.**
   - You qualify on company location (US) and per-seat pricing, as long as you are not OEM.
   - It needs a clickthrough PADA, which replaces your negotiated one.
   - Switching Checkout ↔ non-Checkout sends the listing back to approval†. Salesforce gave no duration, so I cannot promise Q1 2027.
   - Cost at 100 seats: $4,500 per month, or $54,000 per year. 15% is $8,100 per year†, plus $0.30 per card payment†.
5. **Fix the COA cancellation clock if you auto-renew.** Your customer cancellation-notice window must be longer than the 30+ day COA window†, with a buffer. Otherwise a customer cancels in time under your contract, but you cannot file in COA in time. You would then keep owing revenue share on a customer who has left. Unpaid revenue share also expires the review and pulls the listing†. Assign someone to file cancellations.
6. **Check COA compliance now.** Every sale needs a COA order within one business day†. Audit the last two quarters of finance filings against that.

### Irreversible-choice register (rows this touches)

| Choice | Status | Owner | Decision date |
|---|---|---|---|
| Pricing path (COA, GTM or Checkout) | Open | CFO or finance lead with sales lead | After account-manager reply, by mid-November |
| Listing type | Fixed (Packaged Solution) | n/a | n/a |
| Namespace | Fixed | n/a | n/a |
| OAuth controls | Verify (see Part 2) | Engineering lead | Before enabling anything; they lock once enabled |

## Part 2: Prompt templates before the periodic re-review

### Why it matters

Your templates summarise support cases. Case subject, description, comments and inbound emails are written by outside parties, so they are attacker-controlled input to the model. Passing untrusted record data into prompts without enclosure or hardening is failure class 6 in the review kit. Agentforce solutions must also have their actions and prompts tested for prompt injection. Periodic re-reviews are chosen by risk and time since listing, and a $999† fee is due.

### Do this before the re-review

1. **Wrap case text as data.** Put subject, description and comments inside explicit delimiters. Instruct the model to treat that block as data only and to ignore any instructions inside it. Strip or neutralise delimiter-lookalike strings in the input.
2. **Make the summary output inert.**
   - No Agentforce action should fire on text derived from case content without a human step.
   - Summarisation templates should not be chained to write actions such as updating cases or sending email.
   - If summaries render in an LWC or Visualforce page, escape the output (class 4, XSS).
3. **Test with real injection cases.** Build a test set of cases containing payloads: "ignore previous instructions," requests to reveal the system prompt or other records, requests to call an action, and delimiter-breaking text. Keep the results as evidence for the submission.
4. **Harden the actions' Apex (classes 1 and 2):**
   - `with sharing` on every class.
   - `WITH USER_MODE` or `AccessLevel.USER_MODE` on every query and DML.
   - Bind variables in SOQL.
   - Give prompt templates and actions the minimum field access needed.
5. **Run the scanners now.** Run Code Analyzer with `--rule-selector AppExchange --rule-selector Recommended:Security`, and Checkmarx at 3 runs per version†. Add DAST of any external endpoint that authenticates users or moves Salesforce data. Write up false positives with the guarding line named.
6. **Check the listing and OAuth.**
   - Confirm the AI details on the listing are current.
   - If you have a Connected App or ECA used by more than two customer production orgs, the OAuth controls were mandatory by May 11, 2026†. They are PKCE, refresh-token rotation, 30-idle-day expiry and the IP allowlist (≤256 addresses). Delisting is the stated sanction. Each control locks once enabled, so ship client changes first, test in a sandbox, then enable.
7. **Fix the admin items.** Keep the security contact on Company Info current, since a missed re-review expires every version. Keep a working test org and credentials ready. Build any new version on the last passed version so it lists without a new review. A failed re-review gives about 60 days†.

## Timeline

| When | Action |
|---|---|
| Week of 2 Nov | Account-manager questions; COA compliance audit; start Code Analyzer and injection test set |
| By mid-Nov | Pick the payment path; if Checkout, start the clickthrough PADA and listing change |
| Dec | Template hardening; DAST and false-positive write-ups; confirm security contact |
| Q1 2027 | New-customer paperwork live on the chosen rail |
| On notice | Re-review submission: assemble the kit, pay the fee, allow for one failed attempt (60 days†) |

If a failed re-review lands in Q1, two things overlap: the pricing change and the 60-day fix window. Do not change the pricing path and ship new package versions in the same weeks.

## Open items for you

- Does your PADA include GTM terms?
- Is a Connected App or ECA in use today, and in how many customer production orgs?
- Does the March submission include the AI details for the Agentforce actions?

† Verify against current Salesforce partner documentation before quoting: fees and shares, durations, deadlines and rail rules (including the GTM no-auto-renew, ACH and 12-month terms).