**Short answer:** I haven't seen your repo, config, or the customer's setup, so this is an inference from the symptoms. Two changes shipped together, and either could cause what you're seeing. Your CI was green because it never checked either one.

## What probably happened

**1. Tool descriptions are model-facing prompts, not docs.**
- The agent picks between `search_deals` and `list_deals` mostly from their descriptions, since the schemas barely differ.
- A copy edit that tightens wording can remove the signals that made the model choose `search_deals`. Typical losses are "use this when filtering by stage, owner, or amount", "prefer this over list_deals", and "returns a bounded result set".
- The same edit can also make `list_deals` sound more general ("lists deals in your CRM"), so the model reaches for it by default.
- That fits the symptom: the agent now calls `list_deals` for everything and pulls too much data.
- The writer did nothing unreasonable. Nothing in your process told them these strings were behavior.

**2. The toolset rename may be the real cause, or a second one.**
- If the customer's client enables toolsets by name (`toolsets=pipeline`), the rename silently changes what they get.
- If `search_deals` lived in `pipeline` and `list_deals` lives in an always-on toolset, their agent lost `search_deals` entirely. It would then call `list_deals` for everything, with no description involved at all.
- "Stopped using the tool" fits this at least as well as a wording problem.
- Also check for hard-coded tool names or prefixes in the customer's prompts, allowlists, or cached tool lists.

**3. Why CI stayed green.**
- A schema diff checks names, parameters, and types. Descriptions, toolset membership, and annotations are outside what it checks.
- Those are exactly the parts that steer model behavior. After nine months, the CI result only showed that the contract it covers was stable.

## Find out which one it was (about an hour)

1. Pull the customer's exact client config and call `tools/list` with it, both before and after the release. Check whether `search_deals` is present at all.
   - If it's missing, the toolset rename is the cause.
   - If it's present, the descriptions are the cause.
2. Diff the old and new description text for both tools. Look for lost "when to use / when not to use" language.
3. Replay a few of the customer's real prompts against old and new descriptions and compare which tool gets called.
4. Check your server logs. Per-customer call counts for `search_deals` against `list_deals` should show the switch on the release date.

## Fix now

- **Restore the previous descriptions** from git. This is a text-only change and is easy to revert.
- **Keep `pipeline` as an alias for `deals`** (or revert the rename) for at least one deprecation window. Log any request that uses the old name.
- **Tell the customer** what changed and which config value to update.
- **Cap `list_deals`** with a default page size, a hard maximum, and a response size limit. A wrong tool choice should then cost a few rows, not a full dump.

## Put in place so it doesn't repeat

1. **Treat tool metadata as code.**
   - Put descriptions, toolset names, and annotations in one source file.
   - Add CODEOWNERS so engineering must review changes to it, including docs-team PRs.
   - Tell the docs team that these strings are prompts, and give them a short style guide. Each description should say what the tool does, when to use it, when not to, and which tool to prefer.
2. **Snapshot the whole `tools/list` output in CI.** Include descriptions, toolset membership, and annotations. Any diff fails the build unless someone approves an updated snapshot.
3. **Add a tool-selection eval as a CI gate.**
   - Write 30–50 realistic prompts, each with the expected tool, such as "find deals over $50k closing this quarter" → `search_deals`.
   - Run them against the models your customers use.
   - Block the merge if accuracy drops below the baseline, and require the eval on any description or toolset change.
4. **Make renames backward compatible.** Alias old names, deprecate them for a stated window, and note the change in the changelog. Don't ship a rename and a description rewrite in the same release, so you can tell the causes apart.
5. **Monitor production behavior per customer.**
   - Track the tool-call mix and the response size per call.
   - Alert when a customer's `list_deals` share jumps or their payload size spikes.
   - Log unknown or legacy toolset requests.
   - Either of these would have flagged your biggest customer within days instead of two weeks.
6. **Add a rollout step for tool changes.** Ship to an internal or canary customer first and compare the call mix before going wide.

## Open question

Which of the two causes it was changes the postmortem: a process gap (docs PRs bypass engineering) or a compatibility gap (breaking rename with no alias). Step 1 above answers it quickly.