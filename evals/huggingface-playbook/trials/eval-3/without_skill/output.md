# Board deck sanity check

**Verdict:**
- ❌ Don't use "Monthly active developers: 2.4M".
- ⚠️ The "flop" claim isn't supported by 140 likes vs 3,000+.

I worked from the numbers you gave me, not from your dashboards.

## 1. "Monthly active developers: 2.4M"

Three problems, each enough to sink the number if a board member probes.

1. **Downloads are not developers.** One developer, one CI pipeline, or one Docker rebuild can generate thousands of downloads. Hugging Face counts requests, not unique people. PyPI counts installs, including CI runs, mirrors, and bots.
2. **"Active" claims a behavior you haven't measured.** Active means a unique person did something in 30 days. Neither source gives you unique people.
3. **The sum double counts.** The same developer who pulls the model and installs the SDK is counted twice. You're also adding two different units: model-file requests plus package installs.

**Fix: pick one of these.**

| Option | Slide wording | Defensibility |
|---|---|---|
| 🥇 Best | "Monthly active developers: X", from your own logs: unique API keys or accounts that made at least one call in 30 days | High |
| Fallback | "Monthly downloads: 2.4M (Hugging Face 2.1M + PyPI 310k)", footnote: "not deduplicated, includes automated installs" | Medium. Honest, but invites "so how many people?" |
| ❌ Avoid | "Monthly active developers: 2.4M" | Fails on first question |

If you use the fallback, pull PyPI stats **without mirrors** (pypistats has that filter). Expect the SDK figure to drop.

## 2. "The launch flopped: 140 likes vs 3,000+"

Likes are a weak and unfair yardstick here.

- **Lifetime counter.** Likes accumulate over time, so a model with a long run shows more than a recent one.
- **Audience-driven.** Big labs arrive with millions of followers and press cycles. The gap measures brand reach, not launch quality.
- **Different signal.** Likes are a social bookmark. Adoption shows up in downloads, derivatives, and usage.
- **Internally inconsistent.** 2.1M downloads against 140 likes is about 15,000 downloads per like. Either people use the model without liking it, or automated pulls inflate downloads. Neither reading supports "flop", and the second undermines your own 2.4M claim.

**"Flop" needs a goal.** Ask marketing: *what was the target, and by when?* Without that, the word has no meaning.

**Better evidence, all checkable before Thursday:**
- Downloads trend, week over week since launch.
- Derivatives: fine-tunes, quantizations, and Spaces built on the model.
- Citations or mentions, GitHub issues and stars on the SDK.
- Real usage: API calls, unique orgs, customers who adopted.
- Comparison against **peers of similar size**, not big-lab releases.

## 3. Your two numbers conflict

The slide says 2.4M active developers while marketing says flop. The deck can't have both on the same evidence. Decide the narrative first, then choose metrics that support it honestly.

## Before Thursday

1. ⏳ Pull unique active accounts or API keys for the last 30 days from your own logs. This is the number to put on the slide.
2. Get PyPI stats without mirrors.
3. Ask marketing for the original launch goal and the peer set.
4. Replace the likes comparison with a trend chart plus peer-sized comparison.
5. Footnote every metric with its source and what it counts.

**Questions for you:**
- Do you have API logs or accounts that identify unique users?
- Was there a written launch target?
- Is the 2.1M Hugging Face figure for the model alone, or does it include variants and quantizations?

Answer those and I can draft the exact slide wording.