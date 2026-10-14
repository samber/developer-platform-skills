# Meterly public uptime page

I built the page, but it does **not** carry a 99.99% banner. Publishing 99.99% would be a false public claim. It is a 4.3 min/month budget against a 99.9% internal target (43.2 min/month), with no definition of "down" behind it. Enterprise security and procurement teams read these pages closely, and a claim you can't back becomes a liability the first time one of them compares it with the history.

The page carries the claim you can defend today, plus the definitions and live data that make a stronger claim possible later.

## Decisions for you before launch

1. **Banner copy.** I used "Live status and a public definition of what counts as down." Don't use "99.99%". Re-enable a number only after the page has shown that number for 2–3 quarters.
2. **Latency counts, but separately.** Your two 20-minute p50-doubling events were real customer impact, and the old rule scored them 100% up. Under the definitions below, both would show as **Degraded**. They would not reduce Availability, but they would reduce the separate Performance figure. The thresholds are my proposals, so have engineering sign off on them.
3. **Mark "Target" as a target.** The page says 99.9% is an internal objective and not a contractual commitment. Don't change that wording unless legal and sales agree to an SLA with credits.
4. **No backfilled history.** I invented no numbers. The page shows "No data" until the pipeline feeds it. If you backfill last quarter, count the two latency events as Degraded and say so.

## Definitions published on the page

| Status | Trigger (per 1-minute window, measured externally and server-side) |
|---|---|
| **Operational** | Error rate under 1%, p50 and p95 latency within thresholds, and events become queryable within 60 s |
| **Degraded performance** | p50 latency above 2× its 30-day baseline, or p95 above 1 s, or event-to-query delay over 60 s, for 5 consecutive minutes. Requests still succeed. |
| **Partial outage** | Error rate (5xx and timeouts) from 1% to under 50%, or one endpoint or region failing |
| **Major outage** | Error rate of 50% or more, or external probes failing from 2 or more locations |

- **Availability %** is 1 minus the share of minutes in Partial or Major outage. Degraded minutes are excluded.
- **Performance %** is the share of minutes that are Operational or better.
- **Metering-specific rule.** An ingest call that returns 2xx but whose event is not queryable within 60 s counts as Degraded. Silent data lag is the most damaging failure for a metering API.
- **Exclusions.** Announced maintenance (at least 72 h notice) is excluded from Availability and shown in a separate color. Customer-caused errors (4xx) are never counted.
- **Reading the error rate.** Server-side error rate counts all valid requests. Synthetic probes run every 60 s from 3 or more regions, and either source can open an incident.

## The page (`uptime/index.html`)

It's a single static file that reads `/uptime.json`. Host it on infrastructure separate from the API, so it stays up when you don't.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Meterly Status</title>
<meta name="description" content="Live status, 90-day history, and the exact definition of downtime for the Meterly API.">
<style>
  :root{--ok:#1a7f4b;--deg:#a15c00;--part:#c2410c;--maj:#b42318;--none:#8a8f98;--maint:#2457c5;--bg:#fff;--fg:#14171c;--mut:#5b616b;--line:#e3e6ea}
  @media (prefers-color-scheme:dark){:root{--bg:#0f1115;--fg:#e8eaee;--mut:#9aa1ab;--line:#262a31}}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,sans-serif}
  main{max-width:860px;margin:0 auto;padding:32px 20px 64px}
  h1{font-size:1.6rem;margin:0 0 4px} h2{font-size:1.15rem;margin:40px 0 12px}
  .mut{color:var(--mut)}
  .banner{border:1px solid var(--line);border-left-width:6px;border-radius:8px;padding:16px 18px;margin:20px 0}
  .banner strong{font-size:1.15rem}
  .s-ok{border-left-color:var(--ok)} .s-deg{border-left-color:var(--deg)}
  .s-part{border-left-color:var(--part)} .s-maj{border-left-color:var(--maj)} .s-none{border-left-color:var(--none)}
  .comp{display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid var(--line);gap:12px}
  .badge{font-size:.85rem;font-weight:600}
  .bars{display:flex;gap:2px;height:30px;margin:6px 0 4px}
  .bars i{flex:1;border-radius:2px;background:var(--none)}
  .bars i.ok{background:var(--ok)} .bars i.deg{background:var(--deg)} .bars i.part{background:var(--part)}
  .bars i.maj{background:var(--maj)} .bars i.maint{background:var(--maint)}
  .legend{display:flex;flex-wrap:wrap;gap:14px;font-size:.85rem;color:var(--mut)}
  .legend span::before{content:"";display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;background:var(--c)}
  .metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
  .metric{border:1px solid var(--line);border-radius:8px;padding:14px}
  .metric b{display:block;font-size:1.5rem}
  table{width:100%;border-collapse:collapse;font-size:.95rem}
  th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
  .inc{border-bottom:1px solid var(--line);padding:12px 0}
  .note{font-size:.9rem;color:var(--mut)}
  a{color:inherit}
</style>
</head>
<body>
<main>
  <h1>Meterly Status</h1>
  <p class="mut">Live status and a public definition of what counts as down. Updated <span id="updated">…</span>.</p>

  <div id="banner" class="banner s-none" role="status" aria-live="polite">
    <strong id="banner-title">Loading status…</strong>
    <div id="banner-sub" class="mut"></div>
  </div>

  <h2>Components</h2>
  <div id="components"></div>

  <h2>Last 90 days</h2>
  <div id="history"></div>
  <div class="legend" aria-hidden="false">
    <span style="--c:var(--ok)">Operational</span>
    <span style="--c:var(--deg)">Degraded performance</span>
    <span style="--c:var(--part)">Partial outage</span>
    <span style="--c:var(--maj)">Major outage</span>
    <span style="--c:var(--maint)">Maintenance</span>
    <span style="--c:var(--none)">No data</span>
  </div>

  <h2>Measured results</h2>
  <div class="metrics" id="metrics"></div>
  <p class="note">Our internal reliability objective is 99.9% availability. It is a target we measure ourselves against, not a contractual guarantee. Contractual terms, if any, are set in your agreement.</p>

  <h2>Incidents</h2>
  <div id="incidents"><p class="mut">No incidents recorded.</p></div>

  <h2 id="definitions">What counts as down</h2>
  <p>We measure every minute, from outside our network (synthetic probes from at least three regions, every 60 seconds) and from inside (real request outcomes). Either source can open an incident.</p>
  <table>
    <tr><th>Status</th><th>Definition</th></tr>
    <tr><td>Operational</td><td>Error rate under 1%, latency within thresholds, and ingested events queryable within 60 seconds.</td></tr>
    <tr><td>Degraded performance</td><td>Requests succeed, but p50 latency is above 2× its 30-day baseline, or p95 is above 1 second, or event-to-query delay exceeds 60 seconds, for 5 consecutive minutes.</td></tr>
    <tr><td>Partial outage</td><td>Error rate (5xx and timeouts) from 1% to under 50%, or a single endpoint or region failing.</td></tr>
    <tr><td>Major outage</td><td>Error rate of 50% or more, or probes failing from two or more locations.</td></tr>
  </table>
  <p><strong>Availability %</strong> is the share of minutes that are not in a Partial or Major outage. <strong>Performance %</strong> is the share of minutes that are Operational, so it also counts Degraded minutes against us. We report both because a service that responds slowly is not fully working.</p>
  <p><strong>Excluded:</strong> maintenance announced at least 72 hours ahead (shown in blue) and errors caused by the client request (4xx). Nothing else is excluded.</p>
  <p class="note">Thresholds were last reviewed on <span id="defs-date">…</span>. We publish every change to them here.</p>

  <h2>Subscribe</h2>
  <p><a href="/uptime.rss">RSS</a> · <a href="mailto:status@meterly.example">Email us about an issue</a></p>
</main>

<script>
const LABEL={ok:"Operational",deg:"Degraded performance",part:"Partial outage",maj:"Major outage",maint:"Maintenance",none:"No data"};
const pct=v=>v==null?"No data yet":v.toFixed(3)+"%";
const el=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

fetch("/uptime.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw 0;return r.json()}).then(d=>{
  el("updated").textContent=d.updated_at?new Date(d.updated_at).toUTCString():"never";
  el("defs-date").textContent=d.definitions_reviewed||"—";

  const worst=d.components.reduce((a,c)=>{const o=["ok","deg","part","maj"];return o.indexOf(c.status)>o.indexOf(a)?c.status:a},"ok");
  el("banner").className="banner s-"+worst;
  el("banner-title").textContent=worst==="ok"?"All systems operational":LABEL[worst]+" in progress";
  el("banner-sub").textContent=worst==="ok"?"Every component is meeting its thresholds.":"See incidents below for details.";

  el("components").innerHTML=d.components.map(c=>
    `<div class="comp"><span>${esc(c.name)}</span><span class="badge" style="color:var(--${c.status})">${LABEL[c.status]}</span></div>`).join("");

  el("history").innerHTML=d.components.map(c=>
    `<div><div class="mut">${esc(c.name)}</div><div class="bars" role="img" aria-label="${esc(c.name)} 90-day history">`+
    c.days.map(x=>`<i class="${x.s}" title="${esc(x.d)}: ${LABEL[x.s]}"></i>`).join("")+`</div></div>`).join("");

  const m=d.metrics;
  el("metrics").innerHTML=[
    ["Availability, 30 days",pct(m.availability_30d)],
    ["Availability, 90 days",pct(m.availability_90d)],
    ["Performance, 30 days",pct(m.performance_30d)],
    ["Performance, 90 days",pct(m.performance_90d)]
  ].map(([k,v])=>`<div class="metric"><span class="mut">${k}</span><b>${v}</b></div>`).join("");

  if(d.incidents&&d.incidents.length)
    el("incidents").innerHTML=d.incidents.map(i=>
      `<div class="inc"><strong>${esc(i.title)}</strong> <span class="badge" style="color:var(--${i.severity})">${LABEL[i.severity]}</span>
       <div class="mut">${esc(i.started)} – ${esc(i.resolved||"ongoing")}</div><div>${esc(i.summary)}</div></div>`).join("");
}).catch(()=>{
  el("banner-title").textContent="Status data unavailable";
  el("banner-sub").textContent="We cannot load live data right now. This does not by itself mean the API is down.";
});
</script>
</body>
</html>
```

## Data contract (`/uptime.json`)

```json
{
  "updated_at": "2026-10-03T09:00:00Z",
  "definitions_reviewed": "2026-10-03",
  "metrics": {
    "availability_30d": null, "availability_90d": null,
    "performance_30d": null, "performance_90d": null
  },
  "components": [
    { "name": "Event ingestion API", "status": "ok", "days": [{ "d": "2026-10-02", "s": "ok" }] },
    { "name": "Usage query API",     "status": "ok", "days": [] },
    { "name": "Dashboard",           "status": "ok", "days": [] },
    { "name": "Webhooks",            "status": "ok", "days": [] }
  ],
  "incidents": []
}
```

- Leave the metrics as `null` until real data exists. The page then shows "No data yet" instead of a made-up number.
- Generate the file from your monitoring data with a cron job that rolls up per-minute windows. Do not hand-edit it.
- Add a feed step so the RSS file stays in sync with `incidents`.

## What I could not do

- **Wire it to your monitoring.** I haven't seen your stack, so the generator that classifies minutes into the four statuses is yours to build. It needs the four rules in the definitions table.
- **Validate thresholds.** The 2× p50, 1 s p95 and 60 s queryability numbers are placeholders. Check them against last quarter's data first. Your two incidents should land as Degraded, and a normal week should not.
- **Contract language.** If sales wants to promise something, that needs a separate SLA document (credits, exclusions, measurement source) from legal. The page deliberately promises nothing.

## Path to a stronger claim

1. Ship this page and run it for one full quarter with no number in the banner.
2. If Availability holds at or above 99.9%, say "99.9% availability over the last 90 days" with a link to the live data. Customers can verify this claim.
3. Ask for a 99.95% or 99.99% target only once your internal objective supports it and sales has an SLA to back it.