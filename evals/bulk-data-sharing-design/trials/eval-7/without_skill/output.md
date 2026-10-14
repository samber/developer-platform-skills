# What needs to change before you scale Vantablue's export bucket

**Short version:** the bucket's location is the smallest problem. The bigger ones are the unscoped Manila access, tenant isolation, and a legal position that is weaker than "we have SCCs, so we're covered." I'm not your lawyer, so check the legal points with counsel.

**Assumptions to confirm:**
- Vantablue is a processor, and your customers are the controllers.
- Manila staff work for a Vantablue entity or a BPO.
- Your SCCs are the 2021 set.

## 1. The SCC claim doesn't cover your situation ⚠️

SCCs only legitimize the transfer from the EU to your US entity. They don't cover the following:

- **Manila access is a second transfer.** Remote querying from the Philippines is an onward transfer to a country with no EU adequacy decision. You need three things for it:
  - a processor-to-processor contract with whoever employs those staff (SCC Module 3 or equivalent);
  - Manila listed on the sub-processor list in each DPA;
  - customer notice and an objection window under GDPR Art. 28(2) and (4).
  If Manila isn't on that list today, you have a contractual gap with about 1,066 EU customers (41% of 2,600). Fix it by notifying them, not by hoping nobody asks.
- **A transfer impact assessment is also required.** Schrems II requires one for SCC transfers. Ask counsel whether you have one that covers the US and the Philippines.
- **Your DPAs describe security measures you may not follow.** If the SCC annexes promise access control and least privilege, and support staff can run Athena over every tenant's national IDs and salaries, you are in breach of your own contract. Compare the annexes with what actually happens.
- **Check the paperwork itself.** Which SCC version and module did you sign? Are the annexes complete? Is the signing entity the one that actually holds the data? UK and Swiss customers need the UK addendum and the Swiss addendum, which are separate instruments.
- **Check the Data Privacy Framework (DPF).** If you're DPF-certified, ask whether your certification covers HR data. Payroll is HR data, and it needs its own certification.
- **GDPR doesn't require EU data localization.** Don't tell customers it does. But the SCCs plus a US bucket only hold up if access controls are tight, and today they aren't.

## 2. Manila's Athena access is the biggest real risk 🔴

Today, standing access gives every support agent every tenant's names, national IDs, and salaries. For payroll data that is a breach waiting for one stolen credential. Do these now:

1. **Pull the audit trail first.** Check CloudTrail data events and Athena query history for the last 90 days. Find out who queried what and which tenants they touched. If data events weren't enabled, you can't answer that question, and that is a finding in itself.
2. **Remove standing access.** Replace it with just-in-time access tied to a ticket ID, time-boxed, with a named approver.
3. **Give support masked views instead of raw data.** Debugging a failed export rarely needs the actual national ID. Use Lake Formation column-level controls, or tokenized or masked views, with an unmasked break-glass path that is logged and alerts.
4. **Lock down the Athena output location.** Query results contain PII too. Check which bucket they land in, whether it's encrypted, and how long results live. Also check whether agents download them to laptops.
5. **Add scan limits and logging.** Set per-workgroup scan limits and alert on wide queries, such as queries that cover multiple tenants.
6. **Consider removing the need.** Better export job logs and error metadata, plus a "reproduce on synthetic data" tool, would remove most of the reasons to query the content.

## 3. One bucket for 2,600 tenants is one misconfiguration from a full leak 🟠

- **Isolate tenants.** Use per-tenant prefixes with IAM or S3 ABAC (attribute-based access control) and per-tenant or per-region KMS keys. Don't create 2,600 buckets, because of the AWS bucket quota (1,000 by default).
- **Encrypt and limit exposure.** Use SSE-KMS with bucket policies that deny non-TLS requests, and give presigned URLs short expiries. Run Macie, or an equivalent scan, on the bucket.
- **Set a retention policy.** Two years of exports with no lifecycle rule is a deletion-right (Art. 17) and minimization problem. Set expiry per customer contract, and check that versioning isn't silently keeping deleted objects.
- **Document the processing.** Your processing register should cover the export flow. Employee data at this scale is a likely DPIA (data protection impact assessment) case, and you owe your customers help with theirs.
- **Check national ID rules.** Some member states restrict processing of national ID numbers (GDPR Art. 87), so ask counsel which countries matter for you.

## 4. Regional architecture: needed, but design it small

Build it as a tenant "home region" attribute that routes exports to the right region's bucket and KMS keys. Keep the control plane global and the data plane regional.

- **Start with three regions:** US, EU (Frankfurt or Ireland), and India (Mumbai) only if the deal needs it.
- **Moving the bucket doesn't remove the access problem.** If US or Manila staff can still read EU data, the transfer analysis stays the same. So fix section 2 first, then build the region. The region move also protects you against the CLOUD Act exposure customers will ask about.
- **Migrating existing EU tenants is the hard part.** You need dual-write or backfill, cutover per tenant, and verified deletion of the old copies.

## 5. The Indian prospect: get the real requirement before building

Don't build a region for one RFP answer. Ask procurement these questions in writing:

1. Is localization a legal requirement, a sector rule, or a preference?
2. Does the conglomerate have a regulated arm, such as banking or insurance?
3. Is Indian-only storage a contract condition for the deal?

Facts to bring to Indian counsel:
- **DPDP Act 2023:** it doesn't impose a general localization rule, but its rules are being phased in, so confirm the current status.
- **Sector rules:** RBI and SEBI rules can require localization.
- **Aadhaar handling:** storing Aadhaar numbers carries its own restrictions, such as the vault-and-reference-key model. If their payroll contains Aadhaar or PAN, ask what that implies.
- **Manila and the US:** the Manila access path matters to them as much as the bucket location.

Until Mumbai exists, give procurement a **truthful** current answer: US East storage, Manila support access, and the controls you're adding. Evasive answers kill enterprise deals faster than a clear "not yet, here is the plan and date."

## Order of work

| When | What |
|---|---|
| Week 1 | Pull the Athena and CloudTrail evidence. Get the executed SCCs and DPF scope. Enable data-event logging. |
| Weeks 1-2 | Remove standing Manila access. Lock down the Athena results location. Brief counsel on Manila, the sub-processor list, and the transfer impact assessment. |
| Weeks 2-6 | Notify customers if Manila was missing from the sub-processor list. Mask support views. Set a retention policy. |
| Quarter 1 | Tenant isolation with ABAC and KMS. Region routing design. |
| Quarter 2+ | EU region migration. Mumbai only when the deal requirement is confirmed. |

## Three questions only you can answer

1. Is Manila your own entity or a BPO, and is it on the sub-processor list?
2. Do you have audit logs showing past Athena access?
3. Which customers sit in the other 59%, and do they come with their own rules?