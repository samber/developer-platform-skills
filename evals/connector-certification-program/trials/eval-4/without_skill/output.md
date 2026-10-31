# Brackenfield ERP connector: decision and policy

## Recommendation

Your boss is right about the direction and wrong about "everywhere, today." Do these today:

1. **Delist now.** Remove it from the catalog and block new installs. This costs customers nothing and stops the exposure from growing.
2. **Contain the leak path now.** Rotate the credentials the connector holds and cut its exposure at the platform layer. Examples: stop logging or echoing credentials, restrict egress, and narrow scopes. This is where most of the risk reduction comes from.
3. **Notify all 340 customers today.** Say what's affected, what you know and don't know, and the action they must take. Mandate credential rotation for everyone.
4. **Disable immediately** for installs that are idle or non-critical, and for any install showing signs of abuse.
5. **Give payroll-sync customers a short, dated cutoff.** I suggest 5 to 7 days, with a named contact at your company.
6. **Pull the cutoff forward** if you see evidence of exploitation.

**Why not a hard kill for payroll customers.** A sudden shutdown can cause missed payroll runs. That is a certain, immediate harm to your customers' employees. The leak is a known risk with no evidence of exploitation yet (see Check first). Containment plus rotation gets most of the risk reduction without that harm. The short cutoff then forces the migration.

**Escalate to Brackenfield today, in writing, on every channel.** Use the security contact, the account or partnership owner, and an executive or legal contact. Set a firm deadline, such as 5 days, after which you remove the connector.

## Check first (about 2 hours)

These answers can change the call, so settle them before you commit to the timeline.

- **Evidence of exploitation?** Check logs for credential use from unexpected IPs or unusual API activity. If yes, shut it off for everyone immediately and treat it as an incident.
- **What exactly leaks, and to whom?** Examples: logs, error messages, or a third-party endpoint. This sets how much platform-side containment can achieve.
- **Can you patch it yourself?** Check the partner agreement and the connector's license. If it allows, a hotfix or a platform-side wrapper may beat a shutdown.
- **Can you suspend it contractually?** Read the certification and partner agreement for suspension rights and notice requirements.
- **Who reported it, and what is their disclosure deadline?** A typical deadline is 90 days. At 5 weeks you have roughly 7 weeks, but you may be on the clock. Ask the reporter, and coordinate any public advisory with them.
- **Legal and privacy.** Payroll data is personal data. If you find evidence of actual exposure, breach-notification clocks may start (for example, GDPR's 72 hours). Loop in legal today. Don't say "breach" in customer comms until you have evidence.

## Today's timeline

| When | Action | Owner |
|---|---|---|
| Hour 0–2 | Run the checks above, name one decision-maker, and open an incident channel | Security lead |
| Hour 2–4 | Delist the connector, block new installs, pull the install list with scopes and payroll usage | Platform / catalog |
| Hour 2–6 | Apply containment, force credential rotation, email Brackenfield on all channels | Security / platform |
| Hour 4–8 | Send customer notice, with a tailored version for payroll users | Support / comms |
| Hour 8 | Disable idle and non-critical installs | Platform |
| Day 1–7 | Run migration help for payroll customers, then execute the cutoff | Support / solutions |
| Day 5 | Brackenfield deadline: if there's no response, the permanent removal decision stands | Security lead |

## Customer notice (key points)

- The connector has a known credential-exposure vulnerability, and the vendor has not shipped a fix.
- We've delisted it and contained X. We have found no evidence of exploitation. Say this only if it's true.
- **Action for you:** rotate the ERP credentials used by this connector by [date].
- It will be disabled on [date]. Here is the alternative or migration path, and here is who to contact.

## Policy: Certified Connector Security and Lifecycle

Last time, nothing started a clock. Five weeks passed with no deadline, no owner, and no defined next step. The policy fixes that.

**1. Partner obligations (put them in the agreement and re-certify annually)**
- A monitored security contact, with acknowledgement of a report within 2 business days.
- Fix SLAs: **Critical** (credential or data exposure) 7 days, **High** 30 days, **Medium** 90 days.
- A maintenance heartbeat: at least one release or a signed "no changes needed" attestation every 6 months.
- Platform rights to suspend, delist, and patch or wrap the connector for security reasons.
- A named backup maintainer or source escrow for payroll-class connectors.

**2. Escalation ladder (the clock starts at report triage)**

| Day (Critical) | Action |
|---|---|
| 0 | Triage, assign an owner, notify the partner |
| 2 | No acknowledgement: escalate to partner management and executive contacts |
| 7 | No fix or plan: add a warning badge in the catalog and notify customers |
| 14 | No fix: delist (new installs blocked) and apply platform containment |
| 21 | No fix: suspend with a customer grace period |

Use a longer ladder for High and Medium severity. A partner who is communicative and working on a fix can get a pause. A silent partner cannot.

**3. Critical-flow carve-out**
Connectors touching payroll, payments, or other business-critical flows get a fixed grace period of 7 days before suspension. The exception is active exploitation, which means immediate disable. Customers get a migration plan and a named contact.

**4. Abandonment rule**
No release in 12 months and no response to a heartbeat check means the connector moves to "unmaintained." That status brings a catalog label, a new-install block, and a 90-day sunset notice.

**5. Platform-side defenses**
- A managed secrets broker, so connectors never see or log raw credentials.
- Least-privilege scopes and egress allowlists per connector.
- A per-connector kill switch that doesn't require a deploy.
- A live inventory of installs with scopes and a payroll/critical flag, so "who is affected?" is a query rather than a project.

**6. Governance**
- Security owns the decision. The catalog owner executes. Support owns customer comms.
- Pre-approved customer-notice templates and a legal checklist for breach-notification triggers.
- Everyone follows the same ladder, with no exceptions for large partners.
- Run a post-incident review after every use, and report open connector vulnerabilities and their ages to leadership quarterly.

## Immediate next steps for you

1. Confirm the Check-first answers, especially exploitation evidence and contract rights.
2. Get your boss to approve "delist + rotate + notify today, dated cutoff for payroll" in place of "kill everywhere today." Frame it as faster risk reduction without causing missed payrolls.
3. Name the single decision-maker for today.
4. Start drafting the policy from the sections above, and add the Brackenfield timeline as the first case study.

One caveat: I don't know your contract terms, the vulnerability details, or your legal exposure, so treat the day counts and thresholds as starting values to adjust.