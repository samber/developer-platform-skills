# Review: `brimhaven/brimhaven-action` v1.0.0

**Verdict: do not publish Friday as written.** There are three blockers. Security's sign-off also rests on a premise that doesn't hold.

## The sign-off premise is wrong

A commit SHA pins the contents of this repo, meaning `action.yml` and nothing else. Two things in it are not pinned:

- **The `bhv` binary.** It is fetched at run time from `dl.brimhaven.io/latest/`, which changes whenever you publish a new CLI. A customer on a pinned SHA still runs whatever `latest` is today.
- **`actions/setup-node@v4`.** This is a mutable tag, resolved when the customer's job runs. It also looks unneeded, because `bhv` is a standalone binary.

The checksum check doesn't close the gap. `bhv.sha256` comes from the same origin as `bhv`. If the host, CDN, or release pipeline is compromised, the attacker serves a matching pair and the check passes. It only catches corrupted downloads. The binary then runs with the customer's API token and repo checkout.

**Ask security to re-review with the correct scope: what we download and execute.**

## Blockers

1. **`secrets.BRIMHAVEN_TOKEN` is always empty.**
   - Composite actions can't read the `secrets` context, so `BHV_TOKEN` is empty.
   - The `api-key` input is declared and never used, so every scan runs unauthenticated or fails.
   - Fix: `BHV_TOKEN: ${{ inputs.api-key }}`.
   - Also avoid `--token` on the command line, where it shows in the process list. Have the CLI read `BHV_TOKEN` from the environment if it can.

2. **Script injection through inputs.**
   - `${{ inputs.message }}` and `${{ inputs.cli-version }}` are expanded into the shell text before bash runs.
   - A customer who feeds `message` from a PR title or branch name gets arbitrary code execution, with the token in scope.
   - `cli-version` can also path-traverse the download URL.
   - Fix: pass both through `env:` and quote them in the script. Validate `cli-version` against `^v?[0-9]+\.[0-9]+\.[0-9]+$`.

3. **Output and env-file injection from scan output.**
   - `echo "summary=$(cat out.txt)" >> $GITHUB_OUTPUT` breaks on multi-line output. Scanned content such as package names or advisory text can add extra `key=value` lines.
   - The `GITHUB_ENV` line is worse. Anyone who can influence `out.txt` can set `BASH_ENV`, `NODE_OPTIONS`, `LD_PRELOAD`, or `PATH` for every later step in the customer's job, including steps that hold their secrets.
   - Fix: drop the `GITHUB_ENV` write. A scan action shouldn't set environment variables in the customer's job, and nothing documents `BHV_REPORT`. For the output, use a heredoc with a random delimiter:

   ```bash
   delim="EOF_$(openssl rand -hex 16)"
   { echo "summary<<$delim"; cat "$RUNNER_TEMP/out.txt"; echo "$delim"; } >> "$GITHUB_OUTPUT"
   ```

## Fix the download trust model

- **Default `cli-version` to a concrete version, not `latest`.** Otherwise v1.0.0 behaves differently each week.
- **Put the expected SHA-256 for each supported version inside `action.yml`,** keyed by version and OS/arch. The commit SHA then covers the hash and the check is meaningful. Alternatively, verify a cosign or minisign signature against a public key embedded in the action.
- **Drop the `.sha256` fetched from the same host,** or keep it only as a secondary check.
- **Add `--fail` to `curl`** (`curl --fail -sSL -o ...`) so HTTP errors stop the step. Add `--proto '=https' --tlsv1.2` as well.
- **Remove `actions/setup-node@v4`** unless `bhv` needs Node. If you keep it, pin it to a full commit SHA.

## Smaller issues

- **Files land in the customer's workspace.** `bhv`, `bhv.sha256`, and `out.txt` can collide with their files or get committed by later steps. Use `$RUNNER_TEMP`.
- **`sha256sum` may be missing on macOS runners.** Use `shasum -a 256 -c`, or document that the action is Linux-only. Declare which runners you support.
- **`message` has no default.** An empty string becomes `--message ""`. Make sure the CLI accepts that, or omit the flag when it's empty.
- **Document the `summary` output** as untrusted data, because customers will likely put it in PR comments or later `run:` blocks.
- **Add the usual pinning guidance to the README:** pin by SHA, and keep a `v1` tag only as a convenience.

## Corrected scan step

```yaml
- id: scan
  shell: bash
  env:
    BHV_TOKEN: ${{ inputs.api-key }}
    BHV_MESSAGE: ${{ inputs.message }}
  run: |
    "$RUNNER_TEMP/bhv" scan --message "$BHV_MESSAGE" > "$RUNNER_TEMP/out.txt"
    delim="EOF_$(openssl rand -hex 16)"
    { echo "summary<<$delim"; cat "$RUNNER_TEMP/out.txt"; echo "$delim"; } >> "$GITHUB_OUTPUT"
```

## Before Friday

1. Fix the three blockers.
2. Embed the hashes and pin the default version.
3. Run the action in a test repo with a hostile `message` such as `"; echo pwned #`, and with scan output containing a newline plus `foo=bar`. Confirm neither executes or injects.
4. Get security to re-sign off on the download and execution path.

I haven't run any of this. The review is from reading the YAML you pasted.