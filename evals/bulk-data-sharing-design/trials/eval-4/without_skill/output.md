# Ferrolane data export: design review

I answered from your description alone and read nothing from the repo. The design has two paths to the same data, API streaming and direct bucket access, and the direct path is the one most likely to hurt you.

## Verdict

- 🔴 Fix before shipping: emailed long-lived keys, the quarterly manual review as the only revocation control, and the Azure story.
- 🟠 Fix or have a written answer: streaming through the API pods, single-bucket isolation, and the split audit trail.
- 🟢 Fine as-is: authenticating the download in the Go API.

## 🔴 1. Emailed, long-lived IAM user keys

- **Plaintext secrets sit in mailboxes forever.** They get forwarded, archived, and searchable by anyone with access to the recipient's inbox.
- **There is no rotation.** Nothing forces a customer to rotate, and "per customer" means one key pair shared by every pipeline and every person at that customer. An employee who leaves still holds a working key.
- **You can't tell integrations apart.** A leaked key and legitimate use look identical. Revoking means breaking all of that customer's pipelines at once, so in practice you won't do it.
- **Leaks happen on the customer's side, where you can't see them.** Typical places are CI variables, a public repo, or a laptop.
- **Revocation depends on a human.** Churn, downgrade, contract end, and security incidents don't automatically kill a key. A churned customer keeps read access to their data, and to anything new under their prefix, until someone notices.
- **Prefix isolation is one policy mistake from a cross-tenant leak.** Per-customer `s3:prefix` conditions, or `${aws:username}` policy variables, are easy to get wrong. A single bad `ListBucket` condition exposes every customer's object names, and a bad `GetObject` resource exposes their contents.

**Fix:** no static credentials at all.

- **Preferred:** drop direct bucket access. Add `GET /v1/exports` (list, with pagination and filters) plus a completion webhook. The customer's pipeline calls your API and never needs to list a bucket.
- **If direct access must stay:** use an IAM role per customer. Customers assume it with short-lived credentials (1 hour) via an external ID or federation. Scope it with S3 Access Points (a policy per customer, roughly 10,000 per region) instead of one giant bucket policy.

## 🔴 2. The Azure third

- **You are handing Azure customers AWS secrets.** Their pipelines must store an AWS key pair in Azure. That is a cross-cloud static credential, exactly what their security teams hate. Expect it to show up in questionnaires and procurement blockers.
- **Egress costs.** Every byte leaves AWS to Azure at internet egress pricing, roughly $0.09/GB at list. Decide who pays, and check that your pricing tiers cover it.
- **Private-subnet routing can add cost.** If pods or customer pipelines sit behind NAT, you also pay per-GB NAT processing. Use an S3 gateway VPC endpoint on your side.
- **Latency and reliability.** Cross-cloud transfers of large exports are slower and fail more often. That compounds with item 3 (no resume).
- **Data residency.** Do any Azure customers sit in regions or sectors with residency rules? A single-region bucket may already violate a contract.

**Options, in order of preference:**

1. Workload identity federation. The customer's Azure managed identity gets an Entra ID token, which maps to an IAM role via an OIDC identity provider. No secret is stored anywhere.
2. Replicate exports to Azure Blob for Azure customers and hand out user-delegation SAS tokens. This is best for egress cost and customer experience, but it is a second storage system to run and audit.
3. Pre-signed URLs only, with an egress surcharge. This is the cheapest to build and the worst on cost.

## 🟠 3. Streaming through the API pods

- **Bandwidth and connections.** Slow or large downloads pin goroutines, sockets, and pod bandwidth. One customer pulling a 50 GB export can starve everyone else on that pod.
- **Autoscaling follows the wrong signal.** CPU stays low while connections and network saturate, so HPA doesn't react.
- **No resume.** A dropped connection restarts from zero unless you implement `Range`, `If-Range`, and a stable `ETag` correctly. Large cross-cloud downloads will fail often enough to matter.
- **Timeouts.** The ALB idle timeout defaults to 60 seconds, and Go's `WriteTimeout` kills long streams. Check both, plus your proxy and ingress.
- **Deploys cut downloads.** Rolling updates terminate pods mid-stream unless the grace period covers your longest download.
- **Cancellation leaks.** If the client disconnects, the S3 `GetObject` body must be closed and the context cancelled. Otherwise you pay for bytes nobody receives.
- **Auth is checked once.** A long stream can outlive the token or the customer's entitlement.
- **IDOR on `{id}`.** Confirm the handler checks that the export belongs to the caller's tenant, and that IDs are unguessable. Sequential IDs plus a missing tenant check is a classic cross-tenant leak.
- **Double the cost.** You pay for S3 to pod to internet, plus pod and LB capacity, when S3 could serve the bytes directly.

**Fix:** keep authz in the API but move the bytes off it. Return a `302` or JSON with a pre-signed URL that expires in 5 to 15 minutes. Gotcha: a pre-signed URL dies when the signing credentials expire. If the pods sign with an IRSA or STS role, the effective lifetime is capped by that session, so set it deliberately and test a long-lived export.

## 🟠 4. Single bucket, split trust boundaries

- **Blast radius.** One bucket holds all 900 customers. A single misconfigured policy, public-access setting, or lifecycle rule affects everyone.
- **Bucket policy ceiling.** Bucket policies are capped at 20 KB, so don't enumerate customers there. Use access points or per-customer roles.
- **Two authorization models.** The API path checks tenant and entitlement in app logic. The direct path relies on IAM. They drift, and a fix on one doesn't apply to the other.
- **Encryption.** Is it one KMS key for everyone? Per-tenant keys give you cryptographic revocation and a cleaner story for security reviews. Decide explicitly.
- **Retention and deletion.** Logistics data likely includes locations, driver, and consignee details, which is personal data under GDPR. You need a lifecycle policy, a delete-on-request path, and a rule for what happens to exports when a customer churns.

## 🟠 5. The quarterly access review

- **Up to 90 days of exposure by design.** A key leaked the day after a review lives for a quarter.
- **A calendar task fails silently.** Nobody is paged when it's skipped, and reviewing 900 customers' credentials by hand won't happen carefully.
- **Reviewers can't judge the real question.** The security team sees an IAM user. They can't see whether the customer's contact still works there.
- **Auditors will want evidence.** For SOC 2 or ISO, a calendar entry is weak. They want automated, logged evidence of completeness.

**Replace with automated controls:**

1. Keys or sessions expire automatically, so nothing needs reviewing.
2. Billing and contract events (churn, downgrade, suspension) revoke access in code.
3. Pull the IAM credential report and last-used data weekly. Alert on unused keys older than 30 days and on use from a new IP or ASN.
4. Turn on S3 data-event logging (CloudTrail) for the export bucket, and GuardDuty S3 protection.
5. Add a customer-facing page listing active credentials and last use, with self-service revoke and rotate.
6. Keep a quarterly human review for exceptions only.

## 🟢 / 🟠 6. Smaller holes

- **Listing as the interface.** Customers polling `ListObjects` in tight loops cause cost and `503 SlowDown`. There is also no completion signal (manifest or `_SUCCESS` marker), so a pipeline can read a partial export. Webhooks plus a list API fix both.
- **Audit trail is split.** API access logs and S3 data events are separate and hard to correlate per customer, and S3 data events are off by default. Pick one system of record.
- **IAM user scale.** The default quota is 5,000 IAM users per account. That's fine today, but each user has a 2-key limit and slow rotation tooling, and it caps growth.
- **Onboarding friction.** Emailing keys makes onboarding a manual, multi-day step for support. Self-service credentials remove it.
- **Tier gating.** Do all paid tiers get direct bucket access? If it's a perk of higher tiers, enforce that in code, not by convention.

## Recommended target design

1. **Default path:** the API authenticates, authorizes by tenant, and returns a short-lived pre-signed URL. No bytes flow through the pods.
2. **Discovery:** `GET /v1/exports` plus a completion webhook, with a manifest per export. This removes the need for direct bucket listing.
3. **Direct access, if still needed:** a per-customer IAM role or access point with 1-hour STS credentials, assumed via external ID or OIDC federation. AWS customers use IAM roles. Azure customers use Entra workload identity federation, or a replicated Blob copy with user-delegation SAS if egress cost demands it.
4. **Automatic lifecycle:** credentials tied to contract status, expiry as the default, anomaly alerts, and a customer-visible credential page.
5. **Migration:** run both paths in parallel, track last-used per old key to find who still depends on it, announce a sunset (for example 90 days), then delete the IAM users.

## Questions to bring Thursday

1. What is the typical and maximum export size, and how often do customers pull?
2. Who pays egress, especially for the Azure third?
3. How many customers actually use the direct listing path today? Is last-used data available?
4. Do you have EU or other residency obligations on this data?
5. Is SOC 2 or ISO in scope, and what evidence will auditors expect for access control?
6. Are the IAM keys scoped by prefix policy, and has anyone tested a cross-tenant `List` and `Get` with them?
7. Are S3 data events and GuardDuty S3 protection enabled on the bucket today?
8. What happens to a customer's keys and exports on churn?

## Suggested ask for the room

Approve the pre-signed URL path and the list API plus webhook. Set a hard date to retire emailed IAM keys. Pick the Azure option (federation first) before build starts.