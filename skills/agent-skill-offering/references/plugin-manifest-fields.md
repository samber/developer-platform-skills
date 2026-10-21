# Claude plugin manifest fields

Field reference for `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, plus what Anthropic's plugin directory checks on submission. `claude plugin validate --strict .` is the authority on syntax; the directory portal's **Validate** button adds rules the CLI does not check.

## Contents

- plugin.json fields
- Component path fields
- marketplace.json top-level fields
- marketplace.json plugin entries
- Plugin source forms
- Directory submission checks

## plugin.json fields

Directory column: what the portal does when the field is missing or wrong, only where Anthropic documents it. Blank means no documented directory effect.

| Field | Type | Purpose | Directory |
| --- | --- | --- | --- |
| `name` | string | Only required key. Kebab-case; namespaces every component (`acme:deploy`) | Blocks on non-ASCII, a taken name, or a reserved word as the whole name; warns on other pattern breaks |
| `version` | string | Not checked as semver. Set means users stay on it until it changes | Warns when missing |
| `description` | string | Short summary shown in listings | Warns when missing |
| `author` | object | `name` required, `email` and `url` optional | Warns when missing; held when `author.name` mimics another publisher |
| `displayName` | string | UI label; may contain spaces; never used for lookup | Blocks on mixed writing systems or invisible characters |
| `homepage` | string | Docs URL; must parse as a URL or the plugin fails to load | |
| `repository` | string | Source URL; not validated | |
| `license` | string | SPDX identifier | Blocks when neither this nor a `LICENSE` file exists |
| `keywords` | string[] | Discovery tags | |
| `$schema` | string | Editor autocomplete; ignored at load | |
| `metadata` | object | Free-form; Claude Code never reads it | |
| `icon` | string | Image path inside the plugin, e.g. `./logo.png` | Read for the listing only |
| `documentationUrl`, `supportUrl`, `privacyPolicyUrl`, `termsOfServiceUrl` | string | `https://` links | Read for the listing only |
| `defaultEnabled` | boolean | Starts enabled when the user never chose; default `true` | |
| `dependencies` | array | Plugins that must be enabled: `"name"`, `"name@marketplace"` or `{name, marketplace, version}` | |
| `settings` | object | Applied while enabled; only `agent` and `subagentStatusLine` take effect | |
| `userConfig` | object | Values prompted at enable time; use `sensitive: true` for secrets, referenced as `${user_config.KEY}` | Blocks on credentials committed in any file instead |
| `channels` | object[] | Message channels, each bound to one of the plugin's MCP servers | |
| `types` | path | `.d.ts` file for a mod's state | |

Set the five listing fields (`icon` and the four URLs) only in `plugin.json`: in a marketplace entry the validator reports them as unknown.

## Component path fields

Every path is relative to the plugin root, starts with `./`, must exist and must stay inside the root (`..` fails). The directory blocks a misspelled component key or one placed under `experimental`.

| Field | Accepts | Combines with default location |
| --- | --- | --- |
| `skills` | path or array of directories; `"./"` is the root | Adds to `skills/` |
| `commands` | path, array, or object map of name to `source` or `content` | Replaces `commands/` |
| `agents` | `.md` file path or array (no directories) | Replaces `agents/` |
| `hooks` | path, inline object, or array of either | Merges with `hooks/hooks.json`; never list that file here |
| `mcpServers` | path, inline object, array, `.mcpb`/`.dxt` bundle, or `https://` bundle URL | Merges with `.mcp.json` |
| `lspServers` | path, inline object, or array | Merges with `.lsp.json` |
| `outputStyles` | path or array | Replaces `output-styles/` |
| `workflows` | path or array of `.js` files or directories | Replaces `workflows/` |
| `experimental.themes` | path or array | Replaces `themes/` |
| `experimental.monitors` | path or inline array | Replaces `monitors/monitors.json` |
| `experimental.evals` | directory below the root | Replaces `evals/` for `claude plugin eval` |

A skills-only tool plugin needs no component key: `skills/` loads by default.

## marketplace.json top-level fields

| Field | Type | Purpose |
| --- | --- | --- |
| `name` | string | Required. Letters, digits, `.`, `_`, `-`; users type it after `@`. Reserved names include `agent-skills`, `claude-plugins-official` and any `claudeai-` prefix |
| `owner` | object | Required. `name` required, `email` and `url` optional |
| `plugins` | array | Required. Each entry validated on its own |
| `$schema` | string | Editor autocomplete |
| `description` | string | Shown to users; validate warns when missing |
| `version` | string | Version of the marketplace file itself, not of any plugin |
| `metadata.description`, `metadata.version` | string | Alternate location for the two above |
| `metadata.pluginRoot` | string | Directory that bare source names resolve under |
| `forceRemoveDeletedPlugins` | boolean | Uninstalls a plugin removed from `plugins` |
| `allowCrossMarketplaceDependenciesOn` | string[] | Marketplaces whose plugins may be dependencies |
| `renames` | object | Old plugin name to new name, or `null` for removed; migrates existing installs |

## marketplace.json plugin entries

An entry accepts every `plugin.json` field except the five listing fields, plus its own. With a `plugin.json` present, entry `mcpServers`, `lspServers`, `userConfig` and `channels` are ignored, and an entry `skills` list on a `"./"` source replaces the default `skills/` scan instead of adding to it.

| Field | Type | Purpose |
| --- | --- | --- |
| `name` | string | Required. Users type it before `@`; keep it equal to `plugin.json` `name` |
| `source` | string or object | Required. See source forms below |
| `strict` | boolean | Default `true`: entry components append to `plugin.json`. `false` plus any of `commands`, `agents`, `skills`, `hooks`, `outputStyles`, `themes` in the entry fails the load |
| `category` | string | Free-form catalog grouping |
| `tags` | string[] | Free-form search tags |
| `relevance` | object | Signals for when Claude Code suggests the plugin |
| `displayName`, `description`, `author`, `homepage`, `repository`, `license`, `keywords` | as in plugin.json | Display fields; the entry value wins over `plugin.json` |
| `defaultEnabled` | boolean | Entry value wins over `plugin.json` |
| `version` | string | Avoid: `plugin.json` wins and validate warns |
| `headers`, `headersHelper` | object, string | Auth headers for `archive` sources |

## Plugin source forms

| Form | Fields | Use |
| --- | --- | --- |
| `"./"` (relative path) | the string | Plugin in the marketplace repo itself; the self-hosted tool-repo case |
| `github` | `repo`, `ref`, `sha` | Another GitHub repo; `sha` (40-char) wins over `ref` |
| `url` | `url`, `ref`, `sha` | Any git URL |
| `git-subdir` | `url`, `path`, `ref`, `sha` | One directory of a monorepo |
| `npm` | `package`, `version`, `registry` | Package fetched without install scripts |
| `archive` | `url`, `sha256` | HTTPS zip |
| `command` | `command`, `timeout`, `mode` | Directory printed by a local command |

## Directory submission checks

The directory takes a plugin folder (the one holding `.claude-plugin/plugin.json`), not a marketplace file. Checks a tool repo hits:

- A README of at least 40 words in the plugin folder, code blocks not counted.
- A `LICENSE` file or the `license` field.
- No `.DS_Store`, `Thumbs.db`, `desktop.ini` or `__MACOSX` entries; no symlinks, submodules or LFS pointers for loaded files.
- Every plugin-folder file under 5 MiB, and the repo under 50 MiB archived, 256 MiB unpacked and 10,000 entries, or validation stops with no report.
- Every `npx`/`uvx`-style launcher pinned to an exact version, and no `.npmrc`, `bunfig.toml` or `uv.toml` setting a registry beside one.
- No `export-ignore` or `export-subst` in any `.gitattributes`, and no content filter (Git LFS included) at, above or inside the plugin folder.
- File names valid on Windows and macOS (no colon, trailing dot or space, `con`/`prn`-style device names, case-only twins), and folders on the plugin path limited to letters, digits, `.`, `-`, `_`. These three report only **Couldn't validate that repository**.

Held for a reviewer, not blocked: more than 512 files, a non-image file over 256 KiB, any non-text binary, a root `package.json` with a lockfile. With `plugin.json` at a tool repo's root, the whole source tree is the plugin folder, so expect these holds. A root lockfile also makes Claude Code install the tool's npm dependencies into the plugin cache on every install and update. When that cost matters, move the plugin to a subfolder that holds `skills/` itself, then repoint every manifest's skills path and gate 2's `--skills-dir`; a component path outside the plugin folder blocks.
