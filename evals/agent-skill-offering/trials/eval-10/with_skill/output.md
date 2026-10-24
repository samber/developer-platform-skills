**Verdict: 2 of the 5 items are wrong, 1 is unsafe as stated, and 2 are right.** I checked the plan against the `agent-skill-offering` skill and its references. I haven't seen the sdg repo, so I haven't checked the actual files.

## Do now

1. Rewrite the `metadata.openclaw` block in block style (plan item 1).
2. Delete the `openclaw.plugin.json` idea (plan item 2).
3. Replace the reusable workflow with a direct `clawhub` CLI step (plan item 3).
4. Move `icon` and `documentationUrl` back into `.claude-plugin/plugin.json` only (plan item 4).
5. Get written sign-off from Sedgebrook on the MIT-0 point (plan item 5).

## Item by item

**1. `metadata.openclaw: {"requires": {"bins": ["sdg"]}}`: right idea, wrong form.**
- OpenClaw reads the value only as an object, so a JSON string is ignored.
- Flow style (`{...}`, `[...]`) is rejected by strict YAML validators, including the spec's reference validator.
- Use block style, with the list also in block style:

```yaml
metadata:
  version: "3.1.0"
  openclaw:
    requires:
      bins:
        - sdg
```

- Run the version-equality gate with `--allow-nested openclaw`. Without it the gate rejects the nested key.
- `requires.bins` checks the host. An agent in a sandbox also needs `sdg` inside the container.
- No OpenClaw key gates on the tool's version. The body's `Skill version: 3.1.0` guard stays the only version check.

**2. Root `openclaw.plugin.json`: drop it.**
- OpenClaw needs no extra manifest. It already installs the repo as a bundle from your existing `.claude-plugin/`, `.codex-plugin/` or `.cursor-plugin/` manifests, pointed at `./skills/`.
- A root `openclaw.plugin.json` turns the repo into a native OpenClaw plugin instead of a bundle. That is a different contract, and nothing in the plan asks for it.
- If you keep it anyway, its `version` becomes a manifest that gate 2 must check on every release.
- OpenClaw users install with:

```
openclaw plugins install git:github.com/<owner>/sdg@v3.1.0
```

- `openclaw skills install git:` needs `SKILL.md` at the repo root. It does not fit your `skills/sdg/` layout, so do not document it.

**3. ClawHub's reusable `skill-publish.yml`: don't use it.**
- It has no version input. ClawHub then picks its own next patch (1.0.0 first), which breaks lockstep rule 2: the skill version must equal the code version, 3.1.0.
- Call the CLI in your release job instead, after the stale-skill gates pass and the tag exists:

```
clawhub skill publish ./skills/sdg --version 3.1.0 --owner <sedgebrook-org> \
  --categories development --topics <up-to-5-topics>
```

- Derive `3.1.0` from the same source of truth as every other version field. Never type it by hand.
- Set `--categories` (up to 3) and `--topics` (up to 5) once. Passing them publishes a new version even when the files are unchanged. `openclaw`, `clawhub`, `community` and `official` are reserved topics.
- ClawHub keeps a release out of search and install until its security scan passes. Treat "published" as "scan passed", not "CI green".
- Run prereleases off the ClawHub path.
- I haven't checked ClawHub's auth setup (token or login) or how the CLI gets installed in CI. Test those on a throwaway run first.

**4. `icon` and `documentationUrl` in `marketplace.json`: wrong file, and "both files carry them" is the bug.**
- These are the five listing fields: `icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl`, `termsOfServiceUrl`.
- They belong only in `.claude-plugin/plugin.json`. In a marketplace entry the validator reports them as unknown.
- Copies in two files can drift, and the marketplace copy is ignored anyway.
- Move both fields back to `plugin.json`, remove them from the `marketplace.json` entry, then run `claude plugin validate --strict .`.
- `icon` must be a `./` path inside the plugin. `documentationUrl` must be `https://`.

**5. "Fine keeping Apache-2.0 on ClawHub": not true as worded. This needs sign-off.**
- ClawHub releases every published skill under MIT-0, whatever the `license` field says.
- Your repo and the in-repo skill stay Apache-2.0, and the skill's `license` must keep matching the repo's license.
- The ClawHub copy of `skills/sdg/` is MIT-0. That drops Apache's attribution, NOTICE and patent-grant terms for that copy.
- Ask Sedgebrook (and their counsel, if any) to confirm in writing that publishing the skill text under MIT-0 is acceptable. This isn't legal advice.
- If they say no, skip ClawHub and ship the git bundle install only. Nothing else in the plan depends on ClawHub.

## Release gates for 3.1.0 (lockstep check)

Run these before the tag exists:

1. Spec validation of `skills/sdg/`.
2. Version equality. These must all say `3.1.0`:
   - `metadata.version`
   - the `Skill version:` body line
   - `plugin.json` in `.claude-plugin/`, `.codex-plugin/` and `.cursor-plugin/`
   - `gemini-extension.json`
   - `openclaw.plugin.json`, only if you kept it
   - Leave `version` out of the `marketplace.json` entry.
   - The script is `scripts/check-skill-version.py 3.1.0 --allow-nested openclaw`.
3. Content check: every command and flag the skill names must exist in the built `sdg` (`sdg --help`). Every new public command must be mentioned or allowlisted. Assert the packaged artifact contains `skills/`.
4. Security scan of `skills/`.

Then tag, then `clawhub skill publish` with `--version 3.1.0`.

Add this line to the release-note install block, next to the other channels:

```
openclaw plugins install git:github.com/<owner>/sdg@v3.1.0
```

Add the ClawHub line only if item 5 is approved. Existing OpenClaw users re-run it with `--force`.

## Open questions

- Which release tool cuts the tag, and where does the version live? This decides how the bump script is wired.
- Is the sdg binary installed mostly through a package manager? If so, print the tag-pinned skill install command in `sdg --help` or first-run output.

## Next

Open `skills/sdg/SKILL.md` and swap the `metadata.openclaw` line for the block above. That takes about 2 minutes. Then send Sedgebrook the MIT-0 question.