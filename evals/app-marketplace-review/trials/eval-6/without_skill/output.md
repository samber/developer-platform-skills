# Northcut Marketplace Policy: Enforcement

Two decisions need your sign-off before the text. Both change what the policy says.

1. **Vulnerabilities:** I did not write "confirmed vulnerabilities are delisted immediately." Used literally, it fails in both directions. Delisting one low-severity bug takes an app away from every user who depends on it. Delisting also does nothing for the 900 people who already installed the app, and they carry the actual risk. The policy below gives security a delist-now power for serious cases and a clock for the rest.
2. **SBOM:** Two weeks of notice is thin for 300 apps. I made Nov 1 a real enforcement date for new submissions and updates, and gave existing apps a window before they lose listing. Enforcing against all 300 on day one would delist every publisher who is slow or on holiday, and that is not a security outcome. If you want a harder date, change the dates in section B5. The structure still holds.

Dates assume today is Sat Oct 3, 2026. I used Fri Oct 16 for the announcement. Nov 1 is a Sunday, so enforcement is effective Mon Nov 2.

---

## A. Vulnerability response and delisting

### A1. Scope
This section applies to any vulnerability in a listed app, whether it comes from a researcher, a user, Northcut, or the publisher itself.

### A2. Confirmation
- Northcut Security triages every report. A vulnerability counts as **confirmed** when Northcut reproduces it, or when the publisher acknowledges it.
- Triage assigns a severity (A3) and records the reasoning.
- Northcut sends the publisher the full report and repro steps within 2 business days of receiving it. A publisher's request for a repro is answered within that window.

### A3. Severity

| Severity | Examples |
|---|---|
| **Critical** | Remote code execution, authentication bypass, bulk customer-data exposure, or any vulnerability under active exploitation |
| **High** | Stored XSS or injection that runs in a privileged or shared context and can reach user data or sessions; privilege escalation |
| **Medium** | XSS or injection requiring unusual user action or limited to the attacker's own session; limited data exposure |
| **Low** | Minor information leaks, hardening gaps, no practical exploit path |

Stored XSS falls under High or Medium depending on where the payload executes and what it can reach. Security decides and writes down why.

### A4. Remediation clocks
Clocks start when the publisher is sent the report.

| Severity | Acknowledge | Fix shipped | If the deadline is missed |
|---|---|---|---|
| Critical | 1 business day | 7 days | Suspend (A5) |
| High | 2 business days | 14 days | Suspend after one reminder |
| Medium | 5 business days | 30 days | Warning, then suspend after 14 more days |
| Low | 10 business days | 90 days | Warning only |

**Non-responsive publisher.** Northcut sends two notices to every contact on file, at least 3 business days apart. If neither gets a reply:
- Treat the app as non-responsive.
- Move it up one escalation step: suspend if it is Medium or above, warn if Low.
- Do not wait out the full fix clock.

### A5. Actions
- **Suspend (delist).** The app is hidden from new installs and search. Existing installs keep working unless Disable applies.
- **Disable.** Northcut turns off the app for existing installs. Use this only for Critical vulnerabilities, or High ones with a demonstrated exploit path to user data. It needs sign-off from the head of security.
- **Emergency authority.** The head of security may suspend or disable any app immediately, at any severity, when there is credible risk of active harm. They record the reason and notify the publisher at the same time. No clock applies.
- **Everything else follows the clocks in A4.** A confirmed vulnerability alone is not grounds for immediate delisting.

### A6. Communication
- The publisher receives the report, severity, deadline, and the exact action that follows a missed deadline.
- Installers are notified when an app is disabled, or when it is suspended for a High or Critical vulnerability. The notice says what is affected and what to do. It does not publish exploit details.
- Researchers get an acknowledgment, status updates at each step, and notice of the fix.
- Public disclosure happens when the fix ships, or at 90 days after the report, whichever comes first. Security may extend this once, by up to 30 days, with the researcher's agreement.

### A7. Reinstatement
A suspended app returns once the publisher ships a fix, Northcut verifies it against the original repro, and security signs off. Verification target: 3 business days.

### A8. Records
Every report keeps its triage reasoning, notices sent, and action taken. Publisher disputes go to the head of security, who answers within 5 business days.

### Applying this to the open XSS report
The policy does not yet exist, so apply it in good faith now:
1. **Confirm that Northcut itself has reproduced the XSS.** If not, do that today. Everything else depends on it.
2. **Check that the publisher actually received the repro.** They asked for one, and nine days of silence may mean they never got it.
3. **Assign severity.** Where does the payload execute, and what can it reach? A stored XSS in an app with 900 installs may well be High.
4. **If it is High or Critical, and the repro is solid:** send two notices 3 business days apart. Then suspend, or suspend now under the head of security's emergency authority.
5. **Notify the 900 installers** if the exposure is real.

---

## B. SBOM requirement

### B1. Requirement
Every listed app must provide a Software Bill of Materials (SBOM) for each published version.

### B2. Format and content
- **Format:** CycloneDX 1.5 or later, or SPDX 2.3 or later, as JSON.
- **Minimum content** (the NTIA minimum elements): supplier, component name, version, unique identifier (such as a purl), dependency relationships, SBOM author, and timestamp.
- **Scope:** direct and transitive dependencies shipped in the app, including bundled and vendored code.
- **Delivery:** uploaded with the submission, or linked to a stable URL that Northcut can fetch.

### B3. Validation
- Northcut validates every SBOM automatically on upload: schema check, required fields present, component list not empty, and the version matches the submitted version.
- A failed check returns a specific error to the publisher. A human reviews only the apps that fail twice.
- Northcut does not verify that the SBOM is complete. It rejects only SBOMs that are structurally invalid or clearly inconsistent with the app.

### B4. Freshness
Each new version needs its own SBOM. An update that ships without a matching SBOM is rejected at submission.

### B5. Timeline

| Date | What happens |
|---|---|
| **Fri Oct 16** | Announcement to all publishers: requirement, format, deadlines, and a how-to guide. |
| **Mon Nov 2** | **Gate on new submissions and updates.** Any new app and any update to an existing app needs a valid SBOM to be accepted. |
| **Nov 2 to Jan 15** | **Compliance window for existing apps** with no pending update. Publishers upload an SBOM at any time. |
| **Dec 1, Jan 1, Jan 8, Jan 14** | Reminders to non-compliant publishers. |
| **Mon Jan 18, 2027** | Final notice to every app still non-compliant. |
| **Mon Feb 1, 2027** | **Suspension from new installs** for apps still non-compliant. Existing installs keep working. |

Reinstatement happens within 3 business days of a valid SBOM.

### B6. Escalation ladder
1. Announcement and reminders (above).
2. A final notice to all listed contacts, with the exact suspension date.
3. Suspension from new installs.
4. After 90 days of suspension, with no response, Northcut may remove the app and notify installers.

Northcut does not disable apps for existing installs over a missing SBOM.

### B7. Exceptions
- A publisher can request a one-time extension of up to 30 days by Jan 8, with a written reason. Security approves or denies within 3 business days.
- An app with no third-party components can ship a minimal SBOM that says so.
- Exceptions are logged and published as a count only.

### B8. Operational plan for 300 apps
- **Before Oct 16:** export the publisher contact list and check how many apps have a working security or admin contact. Fix gaps first. A publisher who never receives the notice cannot comply.
- **At announcement:** publish the spec, an example SBOM, and a free generator guide (Syft, cdxgen, or the ecosystem's own tooling). The generators produce a valid file in minutes for most apps.
- **Dashboard:** track compliant, in progress, and no contact. Review it weekly.
- **Measure early:** by Nov 6, count the share of apps that have uploaded or submitted a valid SBOM. If under 50%, widen the window before the Dec reminder. Do not hold the Feb 1 date until you have seen that number.
- **Support:** one support alias and a standing 2-business-day reply target.

---

## Questions for you
- Does the head of security want the emergency authority in A5 as written?
- Do you have the real severity of the open XSS, and has Northcut reproduced it?
- Are the contact data for the 300 publishers reliable?
- Is a Feb 1 suspension date acceptable, or does something outside the policy force Nov 2 for all 300?