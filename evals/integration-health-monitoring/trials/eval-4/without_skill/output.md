Today, send the unknown caller to security and platform engineering. That is not partner work. Then chase in this order:

**Off the partner queue**

0. **Unknown caller (#6)**: 12,000 calls/day to `/v1/contacts` with no API key means either unauthenticated access to contact data or a leaked or shared credential. Send it to security and platform engineering today with the endpoint, volume, and sample IPs and user agents. Partner managers cannot chase an unknown party. If logs identify the caller, it moves into the queue.

**Partner queue**

1. **Zapline (#4)**: the cert expires Nov 30, 31 days from now. This is the only hard date inside a month. 410 installs break all at once. The vendor needs a new client cert or auth path, which takes the longest to arrange. Contact them this week.
2. **FinBridge (#5)**: enterprise contract with SLA credits, so a forced migration has direct money and renewal risk. First check whether the contract lets you retire the endpoint, and on what notice. Then contact them. Loop in the account owner and legal.
3. **LeadLoop (#2)**: only 40 calls/day, but 2,600 accounts hold the install. The vendor must ship an update, then customers must adopt it, so lead time is long. The low call volume suggests most installs are dormant. Ask the vendor for active-install counts first.
4. **Acme internal sync (#1)**: 2.1M calls/day is the biggest volume, but it is one account with one known date (June 30, about 8 months out). One kickoff email and a migration owner is enough for now. Check in monthly.
5. **Quarterly Forecaster (#3)**: send a notice and then wait. Its use of `/v1/deals` may not be affected by the retirement at all.

**Split between the two managers**
- Manager A: Zapline, then LeadLoop, then Quarterly Forecaster.
- Manager B: FinBridge, then Acme.

**Two things to check in your data**
- **Quarterly Forecaster:** "0 calls in 60 days" conflicts with "last call Oct 2", which was 28 days ago. A quarterly job fits that pattern. It probably ran at quarter start, and the next run would be around early January. Treat it as alive, not dead, and confirm the 60-day figure.
- **Sunset date:** I assumed June 30 applies to all `/v1/contacts` users (Acme, LeadLoop, FinBridge, and the unknown caller). If FinBridge or LeadLoop has an earlier date, move it up.

**Next:** send the unknown-caller details to security, then email the Zapline vendor. Together that is about 30 minutes.