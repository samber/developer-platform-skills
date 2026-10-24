Ship the skill inside the binary, and make `SKILL.md` a stub that points back to it. Brew and apt upgrade the binary, but nothing upgrades the skill. I haven't read your `SKILL.md` or the lark source, so this rests on your description.

## Root cause

- The skill is a copy, frozen when the user ran `npx skills add`. `brew upgrade lark` never touches it.
- Drift runs both ways. `npx skills add larkspur/lark` takes `main`, so a user still on 1.7 can get a skill that teaches 1.8 syntax.
- Every future breaking change will repeat this. Fixing `lark push` once won't stop it.

## Fix, in order

1. **Patch release 1.8.1 (about 1 hour).** Make old `lark push` syntax fail with a one-line hint, such as `error: 'lark push <x>' was replaced in 1.8. Use: lark push --to <x>`.
   - Agents read stderr and self-correct. This fixes the three open issues without waiting for anyone to update the skill.
   - If the old syntax can still work unambiguously, accept it with a deprecation warning instead.
2. **Embed the guide in the binary (about half a day).** Use `go:embed` to add `lark skill show`, which prints the agent guide for that exact version.
   - Add `lark skill install [--dir <path>]`, which writes the stub `SKILL.md` to the agent's skills directory.
3. **Make the repo's `skills/lark/SKILL.md` a stub (about 1 hour).** Keep a trigger description, then "Run `lark --version`. Then run `lark skill show` and follow its output. Run `lark <cmd> --help` before using any flag."
   - The stub changes only when that mechanism changes, so it can't go stale.
   - This also covers the case where the skill is installed but lark isn't: the stub can say to install lark first.
4. **Rewrite the README install section (about 30 minutes).** Use two steps:
   - Step 1: install the binary with brew, apt or the tarball.
   - Step 2: run `lark skill install`, or use `npx skills add larkspur/lark` or `gh skill install larkspur/lark lark`.
   - Keep the npx and gh paths as discovery channels, since users find skills there. Don't add more channels with a two-person team.
5. **Add a release gate in CI (about half a day).** Build the binary, then run `lark skill show` and a smoke test against every command it mentions (`--help` exits 0).
   - Fail the release if the embedded guide names a command that doesn't exist. This is what catches the next rename.

## Decisions I made for you

- **brew and apt don't install the skill.** Package installs shouldn't write into users' home directories. Add a brew `caveats` line and an apt `postinst` message: "Run `lark skill install` to set up the agent skill."
- **Tarball users** get the same `lark skill install` command, so they need no special path.
- **Don't version-pin the skill by git tag.** It adds a release step for two people and still copies a frozen file. The stub makes it unnecessary.

## Reply to the three issues today

"Re-run `npx skills add larkspur/lark` after upgrading. 1.8.1 adds a clearer error, and from 1.9 the skill updates itself with the binary."

Say "1.9" only if you commit to shipping steps 2 and 3 in it.

**Next, about 2 minutes:** open `cmd/` in the lark repo and find where `push` parses its args. That tells you whether the old syntax can still be accepted or has to fail with a hint.