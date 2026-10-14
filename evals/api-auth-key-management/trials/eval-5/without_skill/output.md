Both plans have a problem. Neither needs to be dropped.

**Do first (about 30 min):** ask the sales owner and the auditor one question: "Is the 10 weeks the start of the observation window, the fieldwork, or the report date?" The answer decides almost everything below.

## 1. "PCI requires 90-day rotation of every API key"

The hire is half right. PCI requires rotation, but it does not set 90 days for API keys.

- **Where the 90 days comes from:** Req 8.3.9. It applies to user passwords with single-factor auth, and it has an alternative path (dynamic risk analysis). It is not about API keys.
- **API keys and service secrets:** Req 8.6.3 applies. You must change application and system credentials periodically, at a frequency set by your own targeted risk analysis (Req 12.3.1). You must also change them on suspected compromise. It has been mandatory since 2025-03-31.
- **Encryption keys protecting stored card data:** Reqs 3.6 and 3.7 apply. You define a cryptoperiod based on industry practice such as NIST SP 800-57 (3.7.4). There is no fixed number.
- **Hard-coded secrets:** 8.6.2 forbids them in scripts and config.
- **Customer-facing API keys Fintar issues:** the customer owns their rotation. Your duty is to make rotation possible without downtime.

I recalled these clause numbers from DSS v4.0.1 and did not re-check them against the document. Have your QSA confirm them.

**Verdict:**
- Do not buy a tool yet.
- Your frequency is a documented decision, not a fixed 90 days. Different key classes can have different cadences. For example, a CI token can rotate every 30 days while a PAN-encryption KEK rotates yearly with a dual-key rollover.
- Check whether your cloud secrets manager (AWS Secrets Manager, Vault, GCP Secret Manager) already rotates natively. Most do, at low cost.
- The real gaps are usually an inventory of keys and owners, and rotation without downtime. A tool does not fix either.
- Ask the hire to show the clause text behind "90 days". Treat it as a good faith mix-up, not a failure.

## 2. "Write the key-management policy the week before the auditor arrives"

This fails for Type II. It may fail for Type I as well.

- **What Type II tests:** operating effectiveness over an observation window, usually 3 to 12 months and rarely under 3. The auditor samples evidence from across that window: rotation tickets, access reviews, approvals, dated logs.
- **A policy dated the week before the audit:** it covers about 1 week of the window. Every earlier control point is an exception, or the window start moves to your adoption date.
- **Backdating the policy:** never do it. Auditors check document metadata and approval trails. Backdating turns a gap into an integrity problem.
- **If the 10 weeks is the window start:** the report lands in about 3 to 6 months after that, not in 10 weeks.
- **Possible mix-up:** sales may have meant Type I (design only, point in time) and written "Type II". Check the contract language.

## 3. Plan

1. **Today, 30 min:** answer the question at the top. Also ask the customer if they accept a SOC 2 Type I plus a signed commitment to a Type II date. Many enterprise buyers accept this. Do not let sales promise a date before you have this answer.
2. **This week, about 1 day:** key inventory, covering every secret and key, owner, location, current rotation, and blast radius. The policy and the risk analysis both depend on it.
3. **Next week, about 1 day:** write the key-management policy from what you actually do, plus the rotation cadence per key class. Choose a cadence you can meet automatically, because SOC 2 tests you against your own policy. A 90-day rule you miss twice is two exceptions. Get it approved and dated now. This starts your evidence clock.
4. **Weeks 2 to 4:** run the rotations for real and keep the evidence (tickets, logs, approvals). Close gaps found in the inventory.
5. **Week 4, decision:** buy a rotation tool only if the inventory shows many manual, cross-system keys. Native secrets-manager rotation is the default.
6. **Ongoing:** monthly check that the controls ran. Keep the evidence in one folder, which makes the audit cheaper.

The two issues are linked. The cadence you put in the policy for PCI is the cadence the SOC 2 auditor tests. Fix it once and make it realistic.

**Next:** send the window-start question to sales and the auditor, then start the key inventory.