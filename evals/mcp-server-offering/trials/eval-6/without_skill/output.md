# Board slide: MCP adoption and trust

## Problems with the brief

1. **"31,000 organizations" isn't supported by the data.** 31,400 npm downloads counts installs. That includes CI reruns, mirrors, bots, and one developer installing on five machines. Anyone who checks npm will see the match and read it as downloads relabeled as customers. A board member asking "how did you count organizations?" would sink the opener.
2. **The registry listing and directory rank aren't security evidence.**
   - A registry listing shows you published there. As far as I know, the official MCP registry verifies namespace ownership, not security. Check its current policy before Friday.
   - A directory rank is a popularity or ranking-algorithm result.
   - Security-conscious board members know this. Presenting these as proof invites "has anyone audited it?", and you'd have no answer.
3. **The gateway gap changes how you should count.** Your three biggest customers appear in your logs as one gateway source, not as users. You can't extrapolate from partial logs, so present your number as a floor.

## The slide

**Title:** Agent adoption of Pellham: measured floor, growing

**Headline (replaces your opener):**
> **[N] organizations ran agents against Pellham in the last 30 days.** That's a measured floor. Our three largest customers route through their own AI gateways, so their usage is undercounted.

**Left panel, Adoption (pick the first metric you can actually produce):**
- **[N]** organizations with ≥1 authenticated call in the last 30 days (unique org or tenant ID, not IP)
- **[M]** weekly active organizations, with the trend line
- **31,400** npm downloads, labeled "installs, not organizations"
- Footnote: "3 of our largest customers use their own AI gateways. Counted by contract: 3. Usage visibility: partial."

**Right panel, Distribution (not "Trust"):**
- Published in the official MCP Registry
- #4 in category on two MCP directories ([names], as of [date])

**Bottom panel, Security posture (fill only with what's true):**

| Control | Status |
|---|---|
| Independent pen test | [date / vendor / none yet] |
| SOC 2 / ISO 27001 | [Type I / Type II / in progress, target date] |
| Auth model | [scoped tokens, per-tenant isolation, etc.] |
| Audit logging | [available to customers: yes/no] |
| npm provenance and dependency scanning | [yes/no] |
| Vulnerability disclosure or bug bounty | [yes/no] |

Anything you can't fill, show as "planned, Q_" rather than leaving it out. A gap with a date reads better than silence.

## Speaker notes (about 60 seconds)

1. "Here's the number we can defend: [N] organizations active in the last 30 days, counted by authenticated org ID."
2. "It's a floor. Our three largest customers sit behind their own gateways, so we see their traffic but not their users. The true number is higher, and we're closing that gap." (See fixes below.)
3. "Downloads are 31,400, which shows developer pull. I'm not claiming that's the customer count."
4. "Registry listing and directory rank tell you we're discoverable. They aren't a security review. Here's our actual posture:" Then walk the table.
5. "The gap I'd like to close next is [top missing control], targeted for [date]."

## Likely board questions

- **"Why is your number so much lower than downloads?"** Downloads include repeat installs and automation. Organizations are counted by authenticated ID.
- **"How much are you undercounting?"** Give a bound you can defend, such as the three gateway customers' contracted seats or committed volume. Don't estimate by extrapolation.
- **"Is the registry listing a vetting?"** No. It's namespace verification and discovery. Our controls are in the table.
- **"Could rank change?"** Yes. The slide is dated, and rank is a distribution signal only.

## To do before Friday

1. **Pull the real organization count.** Query your own logs for distinct authenticated org or tenant IDs in the last 30 days, then replace [N].
2. **Ask the three gateway customers for a fix.** Request that their gateway pass through a tenant or org header, or send a monthly usage export. This is a reasonable ask under most contracts, and you can present it as a next step.
3. **Confirm the facts you'd put on screen.** Check the directory ranks with screenshots and dates. Check what the official registry actually verifies.
4. **Fill the security table honestly.** If most rows are empty, tell me. Then the right move is to drop "trust proof" from the slide and present a security roadmap instead.

If you can give me the real org count and which security controls exist, I'll finalize the numbers and the notes.