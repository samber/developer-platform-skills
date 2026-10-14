# Verdict: the "CDC support" checkmark does not stay

Replace it with an **"Incremental sync"** row, scoped as below. I'm assuming no one has checked your delete handling or the objects without `updated_at`. Those are the two open facts the copy depends on.

## Why

- **"CDC" means log-based CDC to buyers.** It reads a database's transaction log and captures every insert, update, and delete. A multi-tenant SaaS can't offer that through a public API, and neither can any ELT platform pulling from one. The platforms' own SaaS-source "CDC" is `last_modified` polling with an eventual-consistency model.
- **What you have is polling.** You expose `updated_at` on most objects and customers' platforms pull every 6 hours. That is incremental sync. A data-team buyer who checks "CDC" will assume deletes and intermediate changes are captured. Neither is guaranteed here.
- **The failure is a known one.** The first hard delete that goes missing fails a customer's data audit, and the checkmark is what they'll point to.
- **Competitors' checkmarks aren't your evidence.** Two competitors showing it, plus one prospect asking, is thin demand. Don't match a claim you can't back. The prospect's question deserves an honest answer, which is below.

## Page copy: "Data sync"

**Headline:** Keep your warehouse current with Lumenstack

**Subhead:** Incremental sync through our public REST API. Works with the ELT platform your data team already runs.

**Body:**

> Every contract, party, and obligation you can see in Lumenstack is available through our public REST API. Most objects carry an `updated_at` timestamp, so your ELT platform fetches only what changed since its last run instead of re-reading everything.
>
> **How fresh is the data?** Most ELT platforms pull from Lumenstack every 6 hours by default. Your data is eventually consistent: a change made now shows up in your warehouse on the next sync.
>
> **What incremental sync doesn't capture:**
>
> - **Changes overwritten between two syncs.** If a field changes twice within one interval, the warehouse sees the final value, not both.
> - **Deleted records.** `[Choose one, see below.]`
> - **Objects without `updated_at`.** `[List them, or link to the object-by-object table.]` These are re-read in full on each sync.
>
> Need a complete picture? Run a periodic full refresh alongside incremental syncs to reconcile deletes and missed changes.
>
> [Read the data sync guide →]

**Delete sentence: pick the one that is true:**

- If the API exposes no delete signal: *"Hard-deleted records are not reported by the API, so they remain in your warehouse until a full refresh."*
- If it exposes soft-deletes or a deleted-since feed: *"Deleted records are flagged via `[field/endpoint]`, so your platform can mark them removed."*

## Comparison table

| Before | After |
|---|---|
| CDC support ✅ | **Incremental sync (API-based, `updated_at`)** ✅ |

Keep the footnote visible: *"Eventual consistency, typically 6-hour sync interval set by your ELT platform."* If a competitor's CDC row sits next to yours, don't relabel their feature. Show only your own accurate row.

## Reply for the prospect

> "We don't offer log-based CDC. We offer incremental sync over our REST API using `updated_at`, usually on a 6-hour cycle through your ELT tool. Here's exactly what it does and doesn't capture. What does your pipeline need: deletes, sub-hour latency?"

Their answer is your real demand signal. Log it.

## Before PMM publishes

1. **Deletes:** Does the API expose any delete signal? This sets the delete sentence.
2. **Objects:** Which objects lack `updated_at`? Name them on the page or in a linked table.
3. **Cadence:** Is the 6-hour interval your customers' platform default, or something you control? The copy says "typically, set by your ELT platform." If you guarantee it, you can say so.

## If "CDC" becomes the goal later

The honest upgrade is a **deletion/change feed** on your API: a versioned "changes and deletes since cursor" endpoint. Build it when customers report missed deletes, not at launch. When it ships, announce it as the completeness upgrade. Still don't call it log-based CDC.

Skill steps not run: the demand, platform, and certification steps. They apply to a connector build, not to this page.