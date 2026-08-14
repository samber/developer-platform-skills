# Developer platform skills

Skills for building and running the **developer-facing surface of a SaaS product**: public APIs and their lifecycle, webhooks, SDKs, the developer portal, and the connector marketplace around it.

Written for **platform PMs, API and DX engineers, SDK authors, and partner engineering**: design and policy work, not code generation. Every skill is **tool-agnostic**: it teaches the decision, not one vendor's console.

## Install

Install every skill in this repo, not just one. Skills here are atomic by design and reference each other freely — picking a single skill leaves its sibling skills uninstalled, so cross-references and routed handoffs go nowhere.

**skills.sh (universal)** — works with any Agent Skills-compatible tool:

```bash
npx skills add samber/developer-platform-skills
```

**Claude Code** — install the plugin:

```bash
/plugin marketplace add samber/cc
/plugin install developer-platform-skills@samber
```

**Codex (OpenAI)** — install via the Codex CLI:

```bash
codex plugin add github:samber/developer-platform-skills
```

**Cursor** — copy into Cursor's skills directory:

```bash
git clone https://github.com/samber/developer-platform-skills.git ~/.cursor/skills/developer-platform-skills
```

Cursor auto-discovers skills from `.agents/skills/` and `.cursor/skills/`.

**Gemini CLI** — install as a Gemini extension:

```bash
gemini extensions install https://github.com/samber/developer-platform-skills
```

Update with `gemini extensions update developer-platform-skills`.

## 📚 Related Collections

- [`developer-relations-skills`](https://github.com/samber/developer-relations-skills) — DevRel strategy & execution — _for developer advocates, DevRel managers, community managers_
- [`dev-event-organizer-skills`](https://github.com/samber/dev-event-organizer-skills) — Technical event operations — _for event organizers, conference producers, hackathon leads, community builders_

_Part of the [samber skills ecosystem](https://github.com/samber?tab=repositories&q=skills)_

## 📦 Skills

This collection covers the full developer-platform surface. Start here:

- [`developer-platform-kickoff`](./developer-platform-kickoff) — Routes any developer-platform task to the right skill in this collection, returning a ranked short-list, an ordered chain, and an honest gap list.

Browse all skills and their descriptions in [`references/skill-catalog.md`](./references/skill-catalog.md).

## 📄 License

MIT © 2026 Samuel Berthe
