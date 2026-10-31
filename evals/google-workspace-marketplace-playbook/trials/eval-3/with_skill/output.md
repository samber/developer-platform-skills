# Gmail inbox-summary app: CASA and model-training answer

Figures marked † are Google's and change often. I could not check them against live Google docs, so confirm them before you quote them to your CTO.

## Answer

1. ❌ **The CTO's plan doesn't work.** You can't pick a tier, self-scans are deprecated†, and CASA repeats every year, so it is not a one-time purchase.
2. ❌ **Product's plan is banned.** Limited Use forbids using Gmail data to train or improve a model that serves everyone. Nothing in the playbook exempts customer emails behind a consent screen.
3. ⚠️ **You are missing several other requirements.** They are listed below, and the AI-specific ones are likely to fail an assessment.

## 1. CASA: what to do instead of booking Tier 2 this week

Assumptions, since I couldn't ask:
- You already filed the OAuth data-access request.
- You requested `gmail.readonly` or another restricted Gmail scope.
- Your servers receive the data.

Correct any of these and the plan changes.

**Why the CTO's plan fails:**
- **You don't choose the tier.** Google assigns AL1 or AL2†. Older pages and labs still say "Tier 2" or "Tier 3", so don't buy by that name.
- **Self-scan is deprecated†.** A cheap self-scan will not give you a valid Letter of Validation.
- **Trust & Safety controls the start.** Their email is the start signal, and it comes as the last step of verification. Read it for the assigned level, the deadline, and the authorized-lab instructions. Book only after that.
- **Revalidation repeats.** You renew 12 months† after the letter date. Google may also raise your level as users grow†, and a new restricted scope can force an early re-assessment. "Done forever" is wrong.
- **The cheapest option may not be cheap.** Google charges nothing and labs set the price. Reports range from about $500 to $4,500†. TAC Security's 2026 list prices are $675 for AL1 and $5,400 for AL2†, so AL2 can cost more than the usual range. Labs quote 2-6 weeks†, so nothing finishes this week.

**This week:**
1. Read the Trust & Safety email and note the assigned level and the response deadline. Reply quickly, because the review pauses until you do.
2. Get quotes from two or three authorized labs for that level. If you hold ISO 27001 or SOC 2, ask about the accelerator, which can shorten the assessment.
3. Put a calendar reminder for revalidation 12 months† after the letter date. Keep the Cloud project's Owner and contact emails current, or renewal notices go nowhere.
4. Decide up front whether the CASA AL2† security badge matters to you. It needs AL2 and takes up to 3 weeks† to appear.

## 2. Fine-tuning on customer emails: don't

- **The rule:** data from Gmail, Drive, Chat, Calendar and the other sensitive or restricted scopes is Limited Use. It may serve only user-facing features. It must not train or improve AI models beyond that one user's own personalized model.
- **Why "for everyone" fails:** a shared summarization model trained on pooled customer emails is exactly what the rule bans. This holds even if you add a consent checkbox.
- **What is allowed:** a model personalized for one user, with that user's explicit consent shown in the demo video.
- **Audit past use.** If any summarized email has already gone into a training set, a fine-tune, an eval set or a vendor's logs, stop it and find out. Misuse is a policy breach and can lead to losing verification.
- **Check your LLM vendor.** The vendor's terms must exclude training on your API traffic. A generalized-model training right on their side breaks Limited Use for you.

**Alternatives for product:**
- Synthetic emails.
- Licensed or public email corpora.
- Test mailboxes you own, such as employee accounts whose owners explicitly agree.
- Per-user personalization, built with the consent flow above.

## 3. What else you are probably missing

1. **Prompt-injection protection.** CASA requires it for AI features, and an email summarizer reading untrusted mail is the textbook attack surface. Build and test mitigations before the lab arrives.
2. **Token security.** OAuth tokens must be encrypted at rest with managed keys.
3. **No human reading.** Engineers and support staff must not read users' emails unless the user consented for that specific data. Check your logging, debugging and support tooling for this.
4. **In-app disclosure.** Show what data is used and why immediately before the consent request. The privacy policy alone is not enough.
5. **Privacy policy.** It must be on your homepage's domain, use the same URL everywhere, and carry the Limited Use statement: "The use of information received from Google Workspace scopes will adhere to the Google User Data Policy, including the Limited Use requirements."
6. **Help docs on deleting data.** Users need instructions for deleting their data.
7. **Agentic features.** If summaries call tools or an MCP server, you need in-context consent before each capability first touches user data.
8. **Scope justification.** Use the template "`<scope>` lets `<feature>` … `<narrower scope>` cannot work because …". For server-side summarization the restricted rung is probably justified, because narrower add-on scopes don't cover it. Write that argument down.
9. **Identical scopes in three places.** Code, Marketplace SDK and consent screen must match. Drift triggers the unverified-app screen or a second prompt.
10. **Granular consent.** Detect missing scopes and re-prompt. Reviewers reject apps that break on a partial grant.
11. **Demo video.** It needs an unlisted YouTube link, an English consent screen, the address bar showing the client ID, and one segment per restricted scope.
12. **App type.** "AI summaries" is a permitted Gmail productivity category. If unsure, leave the field empty and Google assigns one.
13. **Cloud project ownership.** The project should sit in an organization with two or more owners. Listing, verification and CASA all key on it.
14. **Listing, if you want one.** Run Marketplace review in parallel with verification, but it can't be approved first. Do not set the consent screen to Internal.
15. **The 100-user cap.** Unverified apps with restricted scopes are capped at 100† users for the app's lifetime. Check where you stand.

## Plan, working backward

| When | Step | Owner |
| --- | --- | --- |
| Today | Freeze any training use of Gmail data, and audit past use | Product + CTO |
| Today | Read the Trust & Safety email; reply with the assigned level | CTO |
| This week | Request 2-3 lab quotes; ask about the ISO/SOC 2 accelerator | CTO |
| This week | Draft the in-app disclosure, Limited Use statement and delete-data docs | Product + legal |
| Weeks 1-2 | Prompt-injection mitigations, encryption check, support-access review | Engineering |
| Weeks 2-6 | Lab assessment (2-6 weeks†) | Lab + engineering |
| After the letter | Marketplace submission, if you want a listing; allow one rejection round | Product |
| Letter + 12 months† | Revalidation | CTO |

## Questions for you

- What level did the Trust & Safety email assign?
- Which scopes does the app request?
- Has any customer email already reached a training or eval set, or a vendor with training rights?
- Who owns the Cloud project, and is it in an organization?

Your answers could change the plan, especially the training audit.