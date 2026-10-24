# Saltmarsh `saltmarsh_sdk` 2.3.1: fix plan

## Don't yank 2.3.1

Skip the `gem yank` and the "push 2.3.1 again" step. Neither works on RubyGems.

- **A yank is not a PyPI-style yank.** On PyPI it hides the release but keeps the file. On RubyGems `gem yank` deletes the file from the CDN, and lockfiles pinning 2.3.1 stop installing.
- **The version number can never be reused.** After a yank, 2.3.1 can't be published again, so the CI re-push can't happen. The fix has to be 2.3.2.
- **The yank would hit the wrong users.** The `x86_64-linux` users, who aren't affected, would break too, and so would everyone with 2.3.1 in `Gemfile.lock`. The skill reserves yank for malware, leaked secrets, or a release nobody can have installed yet. A crash on arm64 macOS is none of those.
- **RubyGems has no soft-removal primitive.** There is no unlist or deprecate, so the rollback is "publish the fix, then announce."

I haven't run any publish or yank command, and I won't. The commands below are for your CI or for you.

## Assumptions

Tell me which are wrong.

- CI is GitHub Actions on hosted runners. Trusted publishing works only there, and it decides the OTP fix below.
- The gem already exists on rubygems.org, so you create a normal trusted publisher, not a pending one.
- The bug is in the native extension code or its arm64-darwin build.
- No private gem server is involved.

## Why CI asks for an OTP

`spec.metadata["rubygems_mfa_required"] = "true"` makes every push to the gem need MFA. An API key still needs an OTP on each push, so no unattended key can satisfy it.

The fix is trusted publishing (OIDC), not a workaround:

- **Keep `rubygems_mfa_required`.** It protects the gem.
- **Move CI to trusted publishing.** GitHub Actions mints a short-lived credential per run, with no OTP and no stored key.
- **Don't switch CI to a different key or a bypass.** On this gem no API key can push unattended.

If your CI is not GitHub Actions, there are two options. Neither is a plain key swap:

- Run only the publish job on GitHub Actions.
- Remove the MFA flag. That weakens the gem, so don't do it without an explicit decision from you.

## Steps

### 1. Fix and preflight (Ruby team)

1. Fix the native extension and bump `version` to `2.3.2` in the gemspec.
2. Add a smoke test on an arm64 Mac runner. This is what 2.3.1 lacked. Build the `arm64-darwin` gem, install it on `macos-latest` (arm64), and run `ruby -e 'require "saltmarsh_sdk"; <call one native method>'`. Gate the release on it.
3. Build all platform gems for the version in one build job: `x86_64-linux-gnu`, `arm64-darwin` and the source gem. Use `rake-compiler-dock bash -c "bundle && rake cross native gem"` per platform, as in your current setup.
4. Check that `required_ruby_version` covers the ABIs the precompiled gems actually support.

### 2. Set up the trusted publisher (a maintainer does this in the rubygems.org UI)

On the `saltmarsh_sdk` gem page, go to Trusted publishers and create one with:

- your GitHub repository owner and repository
- the workflow filename, `release.yml`
- the environment name, `release`

Then in GitHub:

- Create the `release` environment with a reviewer team, or at least two people besides whoever cuts releases. Block self-review and restrict deployments to `v*` tags.
- Add a tag ruleset so only release managers can create `v*` tags.

### 3. Pipeline (draft, pending your approval)

Replace each `<sha>` with a real pinned SHA. Resolve it with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`, or let Dependabot or Renovate pin it.

```yaml
# .github/workflows/release.yml  (DRAFT)
name: release
on:
  push:
    tags: ["v*"]
permissions: {}

jobs:
  build:                                # unprivileged: no secrets, no id-token
    runs-on: ubuntu-latest
    permissions: { contents: read }
    strategy:
      matrix:
        platform: [x86_64-linux-gnu, arm64-darwin]
    steps:
      - uses: actions/checkout@<sha>    # v6
        with: { persist-credentials: false }
      - uses: ruby/setup-ruby@<sha>
        with: { ruby-version: "3.4", bundler-cache: false }   # no restored caches
      - name: Tag must equal gemspec version
        run: |
          tag="${GITHUB_REF_NAME#v}"
          version="$(ruby -e 'puts Gem::Specification.load("saltmarsh_sdk.gemspec").version')"
          [ "$tag" = "$version" ] || { echo "tag $tag != version $version"; exit 1; }
      - name: Build platform gem
        run: |
          bundle install
          # Wire the platform into your Rakefile as you do today; the pattern is:
          bundle exec rake-compiler-dock bash -c "bundle && rake cross native gem"
      - uses: actions/upload-artifact@<sha>   # v5
        with: { name: "gem-${{ matrix.platform }}", path: "pkg/*.gem" }

  build-source:
    runs-on: ubuntu-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - uses: ruby/setup-ruby@<sha>
        with: { ruby-version: "3.4" }
      - run: gem build saltmarsh_sdk.gemspec --output pkg/saltmarsh_sdk.gem
      - uses: actions/upload-artifact@<sha>
        with: { name: gem-source, path: "pkg/*.gem" }

  smoke-arm64-darwin:                   # the check 2.3.1 lacked
    needs: build
    runs-on: macos-latest               # arm64 runner
    permissions: { contents: read }
    steps:
      - uses: actions/download-artifact@<sha>
        with: { name: gem-arm64-darwin }
      - uses: ruby/setup-ruby@<sha>
        with: { ruby-version: "3.4" }
      - run: |
          gem install ./*.gem --local
          ruby -e 'require "saltmarsh_sdk"; <call one native method>'

  publish:
    needs: [build, build-source, smoke-arm64-darwin]
    runs-on: ubuntu-latest
    environment: release                # must match the trusted publisher exactly
    permissions:
      contents: read
      id-token: write                   # OIDC, this job only
    steps:
      - uses: actions/download-artifact@<sha>
        with: { path: pkg, pattern: "gem-*", merge-multiple: true }
      - uses: ruby/setup-ruby@<sha>
        with: { ruby-version: "3.4" }
      - uses: rubygems/configure-rubygems-credentials@<sha>
      - run: for g in pkg/*.gem; do gem push "$g"; done   # every platform gem from one job
```

How the pipeline is built:

- **Separate build and publish jobs.** The build job runs all project code and has no credential. The publish job holds the only OIDC identity and runs no project code.
- **No `rake release`.** `rubygems/release-gem` builds inside the privileged job. The split shape fits an SDK with many dependents better.
- **No `contents: write`.** Tag the release by hand or in a separate job.
- **Partial push.** If a push dies partway, finish pushing the missing platform gems for 2.3.2 and don't yank the ones that made it. A missing platform gem makes those users compile from source, which fails without a toolchain.
- **Attestations.** On stable RubyGems 4.0, sign with sigstore-ruby and pass `--attestation <file>`. Check the gem page for the attestation after release either way.

### 4. Cut 2.3.2 and then clean up

1. Tag `v2.3.2` on the protected tag ruleset. A reviewer approves the `release` environment.
2. Confirm all three gems appear on the gem page: the source gem, `x86_64-linux` and `arm64-darwin`.
3. On a real arm64 Mac, run `gem install saltmarsh_sdk` and the one-line smoke call.
4. **Only now:** revoke the old CI API key and delete the `GEM_HOST_API_KEY` secret. A key left alive is a forgotten attack path.
5. Confirm at least two owners on the gem, with phishing-resistant MFA.

### 5. Announce (this is the rollback)

2.3.1 stays installable, so say so clearly:

- Add a changelog entry and GitHub release note: "2.3.1 crashes on arm64 macOS in the native extension; upgrade to 2.3.2."
- Add a workaround for locked users: `bundle update saltmarsh_sdk`, or pin `gem "saltmarsh_sdk", "~> 2.3", "!= 2.3.1"`.
- Say whether compiling from the source gem avoids the bug (`BUNDLE_FORCE_RUBY_PLATFORM=true`). If the defect is in the C code, the source gem has it too. Test this before you claim it.
- Publish a GitHub security advisory only if the crash has a security impact. A plain crash probably doesn't need one.

## Evidence

Record these in your release notes or runbook:

- the trusted publisher configuration
- the arm64 smoke job passing
- the deleted key
- the 2.3.2 gem page showing every platform

## Decisions for you

1. Confirm CI is GitHub Actions. Otherwise pick between GitHub Actions for publish only and dropping the MFA flag.
2. Confirm 2.3.2 as the fix version. 2.3.1 can't be reused in any case.
3. Approve the draft workflow before I write it into the repo.