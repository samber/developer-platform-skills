# Verdict: the "CDC support" checkmark goes

Lumenstack doesn't do change data capture. CDC means reading a database's change log, so every insert, update and delete arrives as an ordered event within seconds. What you have is incremental polling: ELT tools ask the REST API every 6 hours for rows whose `updated_at` is newer than their last pull. The two behave differently, in ways a data team will notice:

- **Intermediate states are lost.** If a contract goes Draft → In review → Signed between pulls, the warehouse sees only Signed.
- **Deletes are invisible** to an `updated_at` filter unless the API exposes soft-deletes or tombstones. I can't tell from what you've told me whether it does.
- **Objects without `updated_at` need full refreshes.** You said "most" objects have it.
- **Latency is up to 6 hours**, not seconds.

A prospect who asked about CDC likely cares about one of these. If they ship the checkmark and find out in a pilot, you lose trust and possibly the deal. The competitors' checkmarks aren't evidence you should match them. They may be doing the same polling and calling it CDC.

**Recommendation:**

1. Remove the "CDC support" row, or show it as not supported if the table must include it.
2. Add a row you can defend: **"Incremental sync (updated_at)"** with a checkmark.
3. Ask the prospect what they need (freshness, deletes, or history). That tells you whether this is a roadmap gap or a wording gap.

# Copy for the "Data sync" page

**Headline:** Your contract data, in your warehouse.

**Subhead:** Pull everything in Lumenstack into Snowflake, BigQuery, Redshift or wherever you analyze it, through our public REST API and the ELT tools you already use.

**Body:**

> **Incremental sync, every 6 hours**
> Most Lumenstack objects carry an `updated_at` timestamp. Your ELT platform asks for only what changed since its last pull, so syncs stay small and fast. Pulls run every 6 hours.
>
> **Same API, no special export**
> Everything you can get out of Lumenstack goes through our public REST API. There's no separate data product and no extra connector fee. [Confirm before publishing.]
>
> **What to expect**
> - Data is as fresh as the last 6-hour pull.
> - You get the latest state of each record, not every intermediate change.
> - Objects without an `updated_at` field sync as full refreshes.
> - [Deletes: pick one before publishing. A) "Deleted records are returned with a `deleted_at` value so your warehouse can mirror removals." B) "Deleted records aren't returned by incremental pulls. Schedule a periodic full refresh to reconcile them."]
>
> **Need something different?** Tell us what you're trying to do, such as near-real-time data or a full change history. We'd like to hear it. [Link to contact or feedback form.]

**Comparison table row:**

| Capability | Lumenstack |
|---|---|
| Incremental sync (`updated_at`) | ✓ |
| Sync frequency | Every 6 hours |
| Log-based CDC / event stream | — |

If the PMM resists the "—", drop the third row. Don't replace it with a checkmark.

# Before publishing, verify

- **Deletes:** does the API return soft-deleted records? This decides which bullet to use.
- **Which objects lack `updated_at`?** Name them in docs if the list is short.
- **"No extra connector fee"** is my assumption. Delete that line if it's wrong.
- **Webhooks:** if you have them, they're the honest basis for a near-real-time claim. If you don't, don't imply them.