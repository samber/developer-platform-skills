**Offering plan: Brindlewood IDE and agent integration**

Ship one shared core, then thin surfaces on top. Do not build one product per signal. Start with the cheap surfaces that close tickets and RFP rows. Defer the React panel.

**Decision needed today:** name one owner (a DRI). Pick one engineer lead plus one product partner. Without an owner, nothing below ships.

## Signals, verdicts, evidence

| Signal | Verdict | Why |
|---|---|---|
| `flags.yaml` typo tickets | Build first | Real pain, measurable, cheap fix |
| 3 lost RFPs: "IDE integration" | Build, but verify | Only 3 deals. Get the RFP text first. |
| 2 customers built their own sidebar | Build official | Best demand proof. Make them design partners. |
| Agents (Cursor, Claude Code) toggling flags | Build as MCP server | IDE-agnostic, thin over your CLI |
| React dashboard in VS Code | Defer | Duplicates your web dashboard. Biggest cost, weakest proof. |

## Architecture: one core, four surfaces

1. **JSON Schema** for `flags.yaml`. Works in VS Code, Cursor and JetBrains through their YAML support. No extension needed.
2. **`brindle validate --json`** in the CLI. It is the same check in the IDE, CI and pre-commit.
3. **MCP server** wrapping the CLI and REST API. It covers Cursor, Claude Code, VS Code and JetBrains AI at once.
4. **VS Code extension**, published to the VS Code Marketplace and Open VSX. Cursor and other forks use Open VSX. It has a native tree view and no webview.

Later, add a **language server (LSP)** for the checks a static schema cannot do. JetBrains then reuses it.

- Extension shells out to `brindle ... --json` first. No new API surface.
- Fall back to REST when the CLI is missing.
- Auth: reuse `brindle auth token --json`. Store the token in VS Code SecretStorage, never in settings.

## Phases

**Phase 0: weeks 1-2, about 1 engineer**
1. Publish the JSON Schema. Submit it to SchemaStore. Document the `# yaml-language-server: $schema=` modeline.
2. Ship `brindle validate --json` with line and column output.
3. Tell support to answer typo tickets with the schema link. Tag those tickets from now on, so you have a baseline.

Open question: are the mistyped keys structural keys, or flag keys the customer defined? A schema only catches structural keys. Flag-key typos need a lookup against the account, so that case moves to the LSP in Phase 2. Check 10 tickets before you commit.

**Phase 1: weeks 2-6, about 1 engineer**
1. Ship the MCP server. Read tools first: list flags, list environments, get rollout state.
2. Add write tools behind guards:
   - Default to read-only.
   - Write requires an explicit flag.
   - Prod writes need confirmation.
   - Use scoped tokens with an environment allowlist.
   - Log every agent action with agent identity.
3. Ship an agent skill that teaches the CLI and MCP usage, as a cheap complement.

⚠️ An agent toggling prod flags is your biggest safety exposure. Design the guards before the tools.

**Phase 2: weeks 4-12, about 1-2 engineers**
1. Build the VS Code extension with:
   - a sidebar listing flags per environment (what the two customers built);
   - rollout state shown inline;
   - toggle with confirmation;
   - diagnostics and completion in `flags.yaml`.
2. Ask the two customers for their code and a design review. Check their licence and ownership before you reuse anything.
3. Publish to both marketplaces on day one.
4. If Phase 0 shows flag-key typos, build the LSP here and host it inside the extension.

**Phase 3: decide at the gate, not now**
- JetBrains: reuse the LSP plus the schema and MCP you already have. Community Edition needs a plugin to host LSP, so budget for that. Go only if gate data supports it.
- Rollout-percentage charts: only a read-only tree or text view, until usage data justifies more. If product still wants a React panel, require evidence that people open the web dashboard from inside the IDE.

## RFP answer

Verify this first: ask sales for the exact RFP wording of all three deals. "IDE integration" may mean SSO, JetBrains, or something else.

After Phase 0 and 1, you can answer yes with a straight face:
- schema validation and autocomplete in every major IDE;
- an agent integration through MCP;
- VS Code extension by the Phase 2 date.

Do not promise JetBrains until the gate passes.

## Gates and metrics

- **Phase 0 gate:** flags.yaml typo tickets drop. Target is a number you set from the baseline. Check at 6 weeks.
- **Phase 1 gate:** weekly active MCP users and write-call share. Zero prod incidents from agent writes.
- **Phase 2 gate:** extension installs and 30-day retention among the 1,400 teams. Compare against the two design partners' usage.
- **JetBrains go/no-go:** at least 20% of extension and MCP users report JetBrains, or two or more RFPs name it.
- **Business:** RFP wins where IDE integration was a checklist row. Track it, but the sample is small.

## Risks

- **Support load:** every surface adds tickets. Staff the DRI with a support liaison.
- **Telemetry:** extension analytics need opt-in and a privacy review before launch.
- **Token handling:** never log tokens. Short-lived, scoped tokens only.
- **API stability:** the extension and MCP depend on `--json` output. Version that contract now.
- **Marketplace accounts:** create the publisher accounts (VS Code, Open VSX) in company name this week. Lead time is real.
- **Sizing:** the week counts above are my estimates, not measured. Re-check them after the Phase 0 spike.

## Next action

1. Pick the DRI. 2 minutes.
2. Then ask support for 10 recent typo tickets and sales for the three RFP texts. About 30 minutes of their time. Those two answers decide whether Phase 0 needs the LSP and whether the RFP ask is what you think it is.