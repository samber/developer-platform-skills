**Don't plan to re-push 2.3.1. RubyGems never lets a yanked version number be reused, so push 2.3.2.**

**First action:** fix the native extension, bump `version` to `2.3.2`, and release 2.3.2 before you yank anything.

## Corrections to the plan

1. **A yanked version can't be pushed again.** The 2.3.1 push from CI would be rejected. Ship 2.3.2 instead.
2. **RubyGems yank is not a PyPI yank.** PyPI's yank (PEP 592) is soft: the file stays and exact pins still install. `gem yank` removes the gem file from the index. Bundler then fails on every `Gemfile.lock` that pins 2.3.1, with `Could not find saltmarsh_sdk-2.3.1`. That includes healthy `x86_64-linux` users. The closer PyPI equivalent is delete.
3. **Plain `gem yank -v 2.3.1` yanks only the `ruby` (source) gem.** The two precompiled gems stay live unless you pass `--platform` for each.
4. **Yanking is optional.** A new default install already resolves to 2.3.2. Yank only if the 2.3.1 source gem crashes too, or if you want a hard stop for new pins.

## Yank commands (after 2.3.2 is live)

**Yank is irreversible.** Each command needs a fresh OTP, because the yank is also MFA-gated by `rubygems_mfa_required`. Run these from your own terminal, not CI.

```
gem yank saltmarsh_sdk -v 2.3.1 --otp <code>
gem yank saltmarsh_sdk -v 2.3.1 --platform x86_64-linux --otp <code>
gem yank saltmarsh_sdk -v 2.3.1 --platform arm64-darwin --otp <code>
```

- Check the exact platform strings on rubygems.org under saltmarsh_sdk > Versions. Use what is listed, for example `arm64-darwin-23` if it was built that way.
- If you yank only the `arm64-darwin` gem, arm64 Mac users fall back to the source gem. That gem still crashes if the bug is in the C source.

## Fix the CI OTP failure

`rubygems_mfa_required` makes RubyGems demand an OTP on every push. A plain API key can't supply one. Don't remove the metadata, and don't hardcode OTPs.

**Fix: trusted publishing (OIDC).** CI gets a short-lived token from GitHub, so there is no API key and no OTP. It satisfies the MFA requirement.

1. On rubygems.org, open saltmarsh_sdk > Trusted publishers > add a GitHub Actions publisher. Enter the org, repo, workflow filename, and optionally an environment name.
2. Add a publish job to that workflow file. It needs `permissions: id-token: write`.
3. Delete the old API key secret from the repo and revoke the key on rubygems.org.

Workflow skeleton for the source gem plus the two precompiled gems:

```yaml
name: release
on:
  push:
    tags: ["v*"]

jobs:
  build:
    strategy:
      matrix:
        include:
          - { os: ubuntu-latest, platform: x86_64-linux }
          - { os: macos-14, platform: arm64-darwin }
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: "3.3", bundler-cache: true }
      - run: bundle exec rake native gem   # your rake-compiler task
      - run: bundle exec rake test         # smoke-test the built extension on this platform
      - uses: actions/upload-artifact@v4
        with: { name: "gem-${{ matrix.platform }}", path: pkg/*.gem }

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release            # must match the trusted publisher config
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { path: pkg, merge-multiple: true }
      - run: gem build saltmarsh_sdk.gemspec -o pkg/   # source gem
      - uses: rubygems/configure-rubygems-credentials@main
      - run: for g in pkg/*.gem; do gem push "$g"; done
```

- The `macos-14` runner is arm64, so the test step catches this crash before publish. Keep it as a gate. This is the missing test that let 2.3.1 ship.
- If you build with `rake-compiler-dock`, keep that step and keep the same publish job.
- A single-gem repo can use `rubygems/release-gem@v1` instead of the push loop.

## Order of work

1. Fix the extension. Reproduce the crash on an arm64 Mac first, and add a regression test.
2. Bump to 2.3.2 and add a CHANGELOG line: "Fixes arm64-darwin crash in 2.3.1."
3. Set up the trusted publisher and merge the workflow.
4. Tag `v2.3.2` and let CI push all three gems.
5. Verify on an arm64 Mac with `gem install saltmarsh_sdk -v 2.3.2` and a require. Then verify on Linux.
6. Decide on the yank. If you do it, yank all three 2.3.1 gems with the commands above.
7. Add a note on the 2.3.1 release page: "Crashes on arm64 Macs. Upgrade to 2.3.2."

Time: about 30 minutes for the trusted publisher and workflow. The extension fix depends on the bug.

**Next:** open rubygems.org > saltmarsh_sdk > Trusted publishers and add the GitHub Actions entry (about 2 minutes).