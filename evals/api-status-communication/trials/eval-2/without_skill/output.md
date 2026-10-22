# Status page process for Quotable

## Diagnosis

Monitoring caught the problem. The delay came from the process: three people had to act in sequence, and each one could block the next. Nothing forced the page to update. A human-review gate with no deadline, no backup, and no fallback means one unavailable person leaves the page green.

The review step also guards against two different risks, and they need different handling:

- **Wrong claims**: saying "outage" when there is none. Confirmation by the engineer already covers this.
- **Typos and tone**: these are cosmetic. They matter far less than 45 minutes of silence.

Before changing anything, pull the timeline from the last incident. Find where the 45 minutes went: page-to-ack, ack-to-confirm, or confirm-to-publish. Whichever segment ate the time gets the strictest deadline below. Check it against the targets in step 3.

## Principle

**Speed first, polish second.** The first public message goes out fast, from pre-approved wording. Humans refine it afterward. Review moves off the critical path.

## New flow

| # | Step | Owner | Deadline (from page) |
|---|------|-------|------|
| 1 | Alert fires, on-call acknowledges | On-call | 5 min, else auto-escalate to secondary |
| 2 | On-call confirms the problem is real | On-call | 10 min |
| 3 | **Publish "Investigating" from a pre-approved template** | On-call | 15 min |
| 4 | Support lead reviews and edits the live post | Support lead | 10 min after publish |
| 5 | Updates every 30 min until resolved, even if "no change" | Incident owner | Fixed cadence |
| 6 | Resolved notice and postmortem link | Incident owner | On resolution |

### Why this is safe

- **The engineer's confirmation is the false-alarm gate.** It stays, with a 10-minute timebox.
- **Templates remove the typo risk from the critical path.** Wording is written and reviewed in calm conditions, once.
- **The first message is deliberately vague.** For example: "We are investigating elevated errors on the Quotable API." That claims little, so it carries little embarrassment if the issue turns out minor.
- **Support lead review still happens**, on the live post. A typo fixed 8 minutes later is cheap. A silent outage is not.

## Pre-approved templates

The support lead approves these once, then reviews them quarterly. They need no per-incident approval.

- **Investigating**: "We are investigating `{elevated errors | increased latency | stale data}` affecting `{endpoint or component}`. Next update by `{time}`."
- **Identified**: "We have identified the cause and are working on a fix. Next update by `{time}`."
- **Monitoring**: "A fix is in place. We are monitoring results."
- **Resolved**: "This incident is resolved. Duration: `{start–end}`."
- **Data-quality variant**: for wrong or stale pricing data, which your probes may not catch as an outage. Name the affected data set and the time window.

Fill in at most three fields. Free-text composition is for later updates only.

## Remove single points of failure

- **Review SLA with auto-publish.** If the support lead hasn't reviewed within 10 minutes, the template message stays live. Review never blocks.
- **Named backup reviewers**, at least two people with status-page access in every timezone you cover. Put them on a rota, not an ad-hoc list.
- **On-call can always publish.** Give them status-page access and the authority to post a template without anyone's approval.
- **Escalation chain with timers.** If step 1 or 2 stalls, the page goes to the secondary, then to the engineering manager. Wire this into your paging tool, not into people's memory.
- **Check off-hours coverage.** If the last outage fell outside support's hours, the process had no reviewer at all. The backup rota fixes this.

## Automate the green-to-yellow flip

You already have health checks, latency thresholds, and uptime probes. Use them to cut the human delay further:

- **Auto-post a generic "Investigating" notice** when an uptime probe fails on N consecutive checks across M endpoints. Pick thresholds conservative enough to avoid flapping, such as 3 failures in 5 minutes.
- **Auto-flip component status to "Degraded"** for latency breaches, with no text. A yellow component with no message is far better than green.
- **Let on-call retract** an auto-post in one click ("false alarm, auto-resolved"). This catches embarrassing false alarms cheaply.
- If you can't automate the post, automate a **draft** with the template pre-filled. The on-call engineer only presses publish.

## Guardrails against the process regressing

- **A visible clock.** The incident channel shows "time since page" and "time since last public update." If the page has been green for 10 minutes into a confirmed incident, the bot says so.
- **Rule: confirmed incident plus green page for 15 minutes escalates automatically.** Treat that as a process failure.
- **Watch public channels** (Reddit, X, support inbox) for Quotable mentions. A customer report beating your page means the process failed. Alert on it and use it as a trigger to post immediately.
- **Drill quarterly.** Run a game-day incident and time page-to-publish. The target is under 15 minutes. Test the backup reviewer path and the off-hours path.

## Metrics

Track these per incident and review them monthly:

- **Time to first public update** (target: under 15 min)
- **Time to acknowledge**
- **Number of incidents where customers reported first** (target: zero)
- **False-alarm posts** (a handful of retractions is acceptable, and far cheaper than silence)
- **Review latency** (should be under 10 min, and nobody waits on it)

## Rollout

1. **Day 1**: pull the last incident's timeline and find the stalled step.
2. **Week 1**: write and approve templates. Grant on-call publish access. Set up the backup reviewer rota.
3. **Week 2**: add escalation timers in your paging tool and the clock bot.
4. **Week 3–4**: add the auto-draft or auto-post from probe failures. Run the first drill.
5. **Quarter 1**: review the metrics and tune thresholds.

## Decisions for you

1. **Auto-post or auto-draft?** Auto-post gives the fastest, most reliable result. Auto-draft keeps a human in the loop at about a 2-minute cost. I recommend auto-post for total endpoint failure and auto-draft for everything else.
2. **Who owns the 30-minute update cadence?** Name a role, not a person.
3. **Does the support lead accept post-publish review?** This is the key culture change. Frame it as "you still own wording, you just edit live."