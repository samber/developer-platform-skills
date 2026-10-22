# What happened to `search_deals` at Tollgate CRM, and how to stop a repeat

I couldn't check your server logs or the customer's config, so the cause below is the best-supported explanation, not a confirmed one. Two changes shipped in the same release, and either could explain it. A few checks tell them apart.

## What most likely happened

Your schema-diff CI watches the wrong layer. For an agent, a tool's name, description, and toolset grouping are part of the interface. The model chooses between `search_deals` and `list_deals` mostly by reading their descriptions. In a published analysis of 61,097 catalogued tools, changing a description's wording measurably changed how often the model picked that tool, with the JSON schema untouched.

Your CI compared schemas, so it passed for nine months and still passed on the two changes that mattered. Nothing failed loudly. The agent adapted, and it adapted badly.

There are two suspects.

1. **Copy edit (the description change).**
   - A writer tightening wording will often cut the lines that tell an agent when to use a tool and how it differs from its neighbours. Examples are "use this to find deals matching a query; prefer over `list_deals` when you have any filter," or notes on required parameters and expected output.
   - Once `search_deals` stopped saying that, `list_deals` became the safe generic choice. That fits the customer's symptom: it is called for everything, with no filter, so it pulls too much data.
   - Nobody with engineering context reviewed the PR, and no test existed to catch it.

2. **Toolset rename (`pipeline` → `deals`).**
   - Agents key on names for discovery. If the customer's client or gateway enables toolsets by name, an allowlist still saying `pipeline` would silently stop loading `search_deals`. The agent then has only `list_deals` and uses it for everything.
   - This explains the symptom just as well as the copy edit, and it is a breaking change. A toolset rename should have been a major version, or an aliased change.
   - Because both changes shipped together, you can't yet say which one did the damage, or whether both did.

## How to tell which one it was (about an hour)

1. **Customer config.** Ask for their MCP client or gateway config. Look for the toolset name `pipeline`, or a tool allowlist.
2. **Your logs.** For their credential, do `tools/list` responses after the release still show `search_deals`? Compare call counts for `search_deals` and `list_deals` before and after the release date.
   - `search_deals` never offered to them: the rename is the cause.
   - Offered but never chosen: the description is the cause.
3. **Replay.** Take 10–20 real prompts from their workflow and run them against the old and new descriptions in a test harness. Count how often each picks `search_deals`. This confirms the description theory and becomes your first golden test.
4. **Diff the docs PR.** Check which sentences were removed from the `search_deals` and `list_deals` descriptions.

## Fix now

- **Restore the old behaviour:**
  - Add the old `pipeline` toolset name as an alias that resolves to `deals`.
  - Revert the two descriptions to their pre-edit text, then re-apply the writer's edits one at a time through the process below.
  - Tell the customer what changed and why. They found this before you did.
- **Fix the over-fetching:**
  - Make `search_deals` and `list_deals` descriptions state explicitly how they differ ("use `search_deals` for any filtered question; `list_deals` only to page through everything").
  - Give `list_deals` a default `limit` of 20–50 with cursor and has-more fields.
  - Make sure responses support a compact format.
  - Together these cap the damage if an agent picks the wrong tool again.

## Put in place so it doesn't repeat

Treat names, descriptions, and schemas as one compiled contract. Do these in order; each is cheap.

1. **Review gate (today).**
   - Add a CODEOWNERS rule so any file holding tool names, descriptions, or toolset definitions requires an engineering reviewer.
   - A description edit is a code change, not a docs fix. Writers keep editing; they just can't merge alone.
2. **Surface hash in CI (this week).**
   - Hash the full surface (names, descriptions, schemas, toolset membership) and commit the snapshot.
   - CI fails when the hash changes without an updated snapshot, so any change is deliberate and visible in the PR diff.
   - This is the check your schema diff was missing.
3. **Golden-prompt tests (next).**
   - Build a fixed set of representative tasks, seeded from your customer's real prompts. Each must still select and call the expected tool, and `search_deals` for filtered queries must beat `list_deals`.
   - Run them on every change to the tool surface. Run each prompt several times, since selection is probabilistic.
4. **Additive-only changes.**
   - Default every change to additive.
   - Alias old tool and toolset names instead of renaming.
   - Treat a rename or removal as a major version.
   - Give deprecations a window of at least 90 days with a machine-readable header.
5. **Version marker and telemetry.**
   - Put a surface version in the response envelope and log it on every call.
   - Alert on a shift in per-tool call share. A tool going from many calls to zero the day after a release would have caught this in days, not two weeks.
   - Log which toolsets and tools each client was offered.
6. **Customer comms.** Announce surface changes to integrators through your changelog, as you would an API change.

## Gaps and caveats

- The cause is unconfirmed until steps 1–3 above are done.
- The 61,097-tool analysis shows that wording changes shift tool selection in general. It doesn't prove your edit did.
- The stage thresholds and golden-test pass bars should be calibrated against your own first month of data. They are defaults, not industry standards.