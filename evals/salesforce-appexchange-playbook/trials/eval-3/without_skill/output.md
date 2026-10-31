**Next action:** Tell product the bulk-export feature ships in a later version, and tell the CTO to fix the TLS finding instead of appealing it. Both are the faster path.

## Why

- **Bulk export in the same version:** The scanner and the reviewers cover all code in the package version. This holds even if the feature sits behind a flag.
- **Bulk export is high-risk code:** It has the most CRUD/FLS exposure, and it adds SOQL and CSV injection surface. One new finding means another failed cycle. That costs more than the single extra review product wants to avoid.
- **TLS appeal:** The appeal needs a written argument and a reviewer's answer, and it can lose. The fix takes about 10 minutes of server config. The finding is real on that host, so an appeal rests only on "out of scope".

## Plan

1. **Fix CRUD/FLS (`InvoiceController.cls:88`).**
   - Use `WITH USER_MODE` in SOQL and `as user` on DML, or `Security.stripInaccessible`.
   - Don't fix only line 88. Run `sf code-analyzer run --rule-selector AppExchange` on the whole project. The same pattern probably repeats in other classes, and the reviewers' scanner will find them.
   - Estimate: 2 to 4 hours.
2. **Fix stored XSS (`invoiceTable` LWC).**
   - Find where stored invoice data reaches the DOM: `innerHTML`, `lwc:dom="manual"`, or `lightning-formatted-rich-text` fed raw data.
   - Replace it with plain template binding, which escapes by default.
   - Check every other LWC and Aura component for the same pattern.
   - Estimate: 2 to 4 hours.
3. **Fix TLS on `legacy.ledgerly.io`.** Choose one:
   - Disable TLS 1.0 and 1.1, then allow only 1.2 and 1.3. This takes about 10 minutes.
   - Take the site offline.
   - Confirm whether the host appears in the security review submission (listing, support or marketing URLs). If it does, remove it from the submission.
   - Re-test with `nmap --script ssl-enum-ciphers -p 443 legacy.ledgerly.io`.
4. **Resubmit with only the three fixes.**
   - Write a short note per finding saying what changed.
   - For TLS, add one line: "host not called by the app; hardened anyway".
   - Attach clean scanner reports.
5. **Ship bulk-export as the next version.**
   - Build it on a separate branch, and run the scanner on it before you submit.
   - Ask Salesforce through your partner case whether the upgrade needs a full review or a delta review. Don't assume. The rules on re-review fees and scope change, so check them with your ISV contact before you promise product a price.

## Pitch to product

- Adding bulk-export now raises the risk of a second failure. A second failure costs more time than one extra review does.
- The fixed version ships first and unblocks the listing. Bulk-export follows on a clean base.

## Pitch to CTO

- The appeal is worth nothing if the fix is cheaper than the argument.
- The fix also removes a real weakness on a company domain.
- Keep the written "not app-related" note in the resubmission. That makes the scope point without risking the review.

## One exception

If a customer contract requires bulk-export in this version, ask the Security Review team in a case whether they will review the added feature in this cycle. Do not slip it in without telling them. Undisclosed scope changes can fail the review.

**Next:** Run `sf code-analyzer run --rule-selector AppExchange` and count the findings. That count sets the real estimate for steps 1 and 2.