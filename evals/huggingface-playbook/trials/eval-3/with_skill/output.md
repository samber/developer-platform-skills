# Board deck check: Hugging Face and PyPI numbers

**Verdict:** Don't put "Monthly active developers: 2.4M" on the slide, and don't tell the board the launch flopped. Neither claim holds up. Both can be fixed before Thursday (Nov 5).

Labels: **[HF]** is what Hugging Face publishes, **[practitioner]** is reverse-engineered or from experience. Re-check the live HF docs before committing a number to a board.

## 1. "Monthly active developers: 2.4M"

The 2.4M is 2.1M + 310k, and it fails on three counts.

| Problem | Why it breaks the claim |
|---|---|
| Downloads are not developers | A Hub model download is any GET or HEAD on a query file (`config.json` by default). It isn't deduplicated, and a clone or a CI cache miss counts. [HF] |
| Downloads are not "active" | One CI pipeline re-pulling the model every run can produce thousands of "downloads" from one team. Unique downloaders exist only as an Enterprise Plus log export. [HF] |
| The two sources are summed | Hub and PyPI use different counting rules, so the playbook says never add them. PyPI counts also include mirrors and CI installs. [practitioner] |

There is also a likely double count. If your SDK loads the model from the Hub, the same install shows up once on PyPI and again on the Hub. I can't confirm the overlap from here, so check whether the SDK pulls your model.

A technical board member or investor can pick this number apart in one question ("how many unique people?"). That puts the rest of the deck's credibility at risk.

**What to put on the slide instead.** Show each source on its own line with its counting rule:

- Hub downloads, last month: 2.1M. Footnote: "file requests, not deduplicated, includes CI."
- PyPI downloads, last month: 310k. Footnote: "package installs, not deduplicated, includes mirrors and CI."
- Derivatives on the Hub: fine-tunes, quantizations and adapters in the model tree. Count them and put the number on the slide. This is the best adoption signal for an open model, because someone had to do real work to build on it. [HF]
- Real active developers, only if you have them. Use unique API keys or authenticated SDK telemetry from your own systems. A figure from your own logs is defensible. A public download count is not.

If the board insists on one headline, "2.1M model downloads (non-deduplicated)" is true. "2.4M developers" is not.

## 2. "The launch flopped: 140 likes vs 3,000+"

The comparison is not like-for-like.

- Likes go to new frontier releases in their first weeks. Downloads accrue to small, stable models over years. [HF blog, "State of Open Models"]
- Big-lab releases get likes because they are big-lab releases. They don't show that your launch underperformed.
- 2.1M downloads in a month is a strong signal, with the same caveat as above: it isn't deduplicated. A model with few likes and heavy downloads is the normal profile of a useful workhorse model.
- Trending reads roughly the last seven days of likes. [practitioner] If the model is more than a couple of weeks old, 140 likes tells you little about its health.

**What not to do in response.**

- Don't reward or trade anything for likes. The Content Policy restricts "incentivizing manipulation of Hugging Face Hub metrics (e.g., exchanging rewards for likes)", and the sanction includes unranking. [HF]
- Don't ask the whole company to like it at 9am. A spike of zero-history accounts invites a moderation look. [practitioner]
- Drive real visitors to the model page instead.

**What to report to the board.** List likes, downloads and Space visits as three separate lines, each with its counting rule. Add the derivative count, and say the model is performing as a long-tail model, not as a launch spike.

## 3. What I need to firm this up before Thursday

Answers to these would let me tighten the slide wording:

1. How old is the model, and how many likes did it have in week one?
2. Does the PyPI SDK download weights from the Hub?
3. Do you have API keys or SDK telemetry that count unique users?
4. How many fine-tunes and quantizations show in the model tree?
5. Is there an arXiv paper, and how long ago was its first version? Daily Papers submission closes 14 days after the first version. [HF]
6. Is the org on a Team or Enterprise plan? Publisher Analytics (daily counts, still not deduplicated) needs one. [HF]

## 4. Checks you can do before Thursday

1. Count the derivatives in the model tree (about 15 minutes).
2. Check whether the SDK loads the model from the Hub, to size the overlap.
3. Pull unique users from your own logs, if you have them.
4. Re-label the slide with the three separate lines above, each with its counting rule.

## 5. Suggested slide wording

> **Adoption (last month)**
> - Model downloads on Hugging Face: 2.1M *(file requests, not deduplicated)*
> - SDK installs on PyPI: 310k *(not deduplicated)*
> - Community derivatives (fine-tunes, quantizations): <N>
> - Unique active developers: <N from our own telemetry, or "measurement in progress">

If someone asks why there's no single "developers" number, answer: "Public download counters can't tell us unique people. We're instrumenting that, and here is the proxy we do trust."