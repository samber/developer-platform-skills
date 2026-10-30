# Chase order for Brightmoor's retiring CRM API integrations

**Today is 2026-10-30. Chase them in this order:**

| # | Integration | Days to break | Customers hit | Why here |
|---|---|---|---|---|
| 1 | **Zapline connector** | **31** (cert expires Nov 30) | 410 installs | It breaks first. It is a fleet app, so one fix covers all 410 installs. |
| 2 | **LeadLoop app** | ~243 (Jun 30, assumed) | 2,600 accounts | It has the most customers behind it. 40 calls a day is irrelevant, because one conversation fixes 2,600 breakages. |
| 3 | **FinBridge** | ~243 (Jun 30, assumed) | 1 account | Commercial weight promotes it into the top tier. An enterprise SLA contract carries credit exposure. |
| 4 | **Quarterly Forecaster** | Unknown, see below | 85 accounts | It looks dead but is seasonal. One check-in now saves a January failure. |
| 5 | **Acme internal sync** | 243 (Jun 30) | 1 account | It has a known date and a single, reachable owner. Email and in-response warnings may be enough. |
| – | **Unknown (12,000 calls/day, no key)** | – | – | The partner managers can't chase it. See "Not on the managers' list" below. |

I ranked by days to break first, then by customers affected. I did not rank by call volume. Acme's 2.1M calls/day does not move it up, since one account is one conversation.

## What each manager does

**Zapline (do this week).**
- Send the notice today with the confirmation request inside it. Name the cert, the Nov 30 expiry, the replacement cert or auth path, and one sample request ID.
- Tell Zapline to reply with a named owner and a ship date.
- The window is under three notice intervals, so compress it. Send now, again at the midpoint (~Nov 15), and again one week before (~Nov 23).
- Call Zapline's technical contact this week.
- If Zapline is silent by ~Nov 10, notify the 410 installing customers' admins. Clear that template with legal or partner management first.
- **Check first:** a new cert path must exist and be documented. If it doesn't, the real owner of this row is engineering.

**LeadLoop.**
- Make a named-outreach call to a person, not a no-reply list.
- Bring the census row, two sample request IDs, the migration guide, and a technical contact on your side.
- Ask for an owner and a ship date, and write both into the row afterwards.
- Also send the targeted email and the in-response warning. The 2,600 customer-admin notice is the fallback if the developer stays silent.

**FinBridge.**
- Call the account owner, with the customer's commercial contact in the loop.
- Pin down when their last job runs, since an enterprise integration may run monthly or quarterly jobs.
- Get written confirmation that every job has moved. One call on the replacement proves nothing.
- Raise the exception path only if June 30 can't be met. A per-credential exception with an owner, a reason, and one expiry is acceptable. A global slip is not.
- Have the contract owner check what the SLA says about a deprecation they initiate.

**Quarterly Forecaster.**
- The 60-day window misleads. Its last call was Oct 2, right after Q3 close, so it is dormant and about to resume. It is not abandoned.
- The next run is probably around the start of January. If `/v1/deals` retires before then, it breaks on its first Q4 run.
- Send a targeted email, then one call to confirm it has moved or will move before that run.
- **Do not revoke its credential.** Revocation would break the seasonal job.
- Set the lookback to at least one quarter (a year if it also runs a year-end close).

**Acme.**
- Send the targeted email and in-response warnings with the sample request ID.
- Ask for a named owner and a date.
- The email on file may go to a mailbox nobody reads, so ask for a reply.
- Add a named call only if the managers have hours left after the four above.
- Tell engineering about the 2.1M calls/day. The replacement must have headroom for that load before any brownout.

## Not on the managers' list: the unknown caller

12,000 calls/day with no API key on a public endpoint can't be notified. Only in-response warnings and brownouts reach it. Give it to engineering and security:

1. Add the deprecation headers and a body warning on `/v1/contacts`.
2. Group the calls by User-Agent, IP range, and referrer. A shared HTTP library hides identity, so treat User-Agent as a hint.
3. If it looks like abuse or scraping, hand it to security rather than the sunset program.
4. Set a floor for unattributed public-surface calls and defend it in the readiness gate.
5. Schedule brownouts last, announced and short, and only once the replacement meets its service objective.

## Assumptions to confirm

- **Jun 30 is 2027, and it also applies to LeadLoop and FinBridge.** Both call `/v1/contacts`, and only Acme's date was given. If their dates differ, re-bucket them.
- **No break date was given for `/v1/deals`.** If it retires before ~Jan 2, Quarterly Forecaster moves to #3.
- **Two partner managers is the capacity.** I assumed they can run named outreach for four rows. If they have fewer hours, drop from the bottom of the list.
- **The replacement surface is stable and feature-complete.** If it isn't, escalating beyond a reminder is unfair. Brownouts and cutoffs would then break partners through your own defect.

## Do these before outreach

- **Close the door.** On notice day, new accounts, app registrations, and webhook destinations go to the replacement. Rotated keys and new installs of existing apps keep the old surface until their break date.
- **Verify contacts in the same message as the notice.** Don't hold the notice for verification. An unverified contact counts as no contact.
- **Send only to integrations that actually call these surfaces.** Don't blast every developer.