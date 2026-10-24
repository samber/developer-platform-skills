# Incident plan for the call: `dunmore-sdk` 2.8.1

**I did not use the token, and I couldn't have deleted 2.8.1 with it.**
- PyPI upload tokens can only upload. Deleting a release is web-UI only, and it needs an Owner or Maintainer login with 2FA.
- You pasted the token into this chat, so treat it as burned. It was already suspect because it sat in CI variables on a compromised runner.

## Do now (about 10 min)

1. **Revoke the token.** Go to pypi.org → Account settings → API tokens → revoke. If you can't tell which one it is, revoke all tokens for the project. This stops further uploads, such as a 2.8.2 from the attacker.
2. **Download 2.8.1 for evidence before deleting.** Run `pip download dunmore-sdk==2.8.1 --no-deps --no-binary :none: -d /tmp/dunmore-2.8.1/`. Also grab the sdist and wheel links and hashes from the release page. Don't install or import the package. Unpack it in an isolated directory. Deletion removes the files, so this is your only copy.
3. **Delete the release.**
   - Go to pypi.org → Your projects → `dunmore-sdk` → Manage → Releases → 2.8.1 → Options → Delete.
   - You'll have to type the version to confirm.
   - The deletion is irreversible, and 2.8.1 can never be re-used. Your next legitimate release must be 2.8.2 or higher.
   - If you want to stop installs within seconds, **Yank** is one click and reversible. Yanking only hides the release from unpinned installs, so anyone pinned to `==2.8.1` still gets it. Delete after the evidence is captured.
4. **Report it to PyPI.** Email security@pypi.org, or use the "Report project as malware" link on the project page. The PyPI admins can pull files and check for related uploads.
5. **Check the project's Security history.** Open Manage → Security history. It shows who uploaded 2.8.1, with which token, from which IP, and when. It also shows whether any other file or version appeared.

## Exposure window (assume users were hit)

- Find out how long 2.8.1 was live. Note the upload time against now.
- Without unsafe installs, check PyPI download stats and your own telemetry for pulls of 2.8.1.
- Tell downstream teams to pin to 2.8.0 and check lockfiles and images for 2.8.1.
- Anyone who installed 2.8.1 should rotate every secret reachable from that environment.
- Prepare a security advisory with a clean 2.8.2 once the runners are rebuilt.

## Runner and CI containment (for the call)

1. **Isolate the suspected runner(s).** Pause them in GitLab (Admin → Runners, or Settings → CI/CD → Runners). Don't wipe them yet. Snapshot disks and logs for forensics.
2. **Rotate every CI/CD variable, not only the PyPI token.** That includes GitLab tokens, registry and cloud credentials, signing keys, and deploy keys. Also rotate any secret the runner could read at job time.
3. **Audit pipelines.**
   - Review the history of `.gitlab-ci.yml` and included templates for unexpected changes.
   - Look for jobs that triggered the 2.8.1 build or upload, and compare them against your release tags and commits.
   - Check who registered runners and when, and which projects and groups they're shared with.
   - Check for new or changed protected branches, tags, and variables.
   - Check recent access and audit events for the project and group.
4. **Compare artifacts.** Diff the 2.8.1 sdist against the 2.8.0 sdist and against what your repo's tag would build. This shows what the attacker injected, such as install hooks in `setup.py`, `.pth` files, or new dependencies.
5. **Check your other packages.** The same runner or token may have published other artifacts. Review other PyPI projects, container registries, and the GitLab package registry.

## After containment

- Enable **Trusted Publishing** on PyPI. The GitLab publisher uses OIDC, so no long-lived token lives in CI. Use it for 2.8.2.
- Require 2FA for every project collaborator, and reduce the number of Owners.
- Run releases on ephemeral runners, with protected variables restricted to protected tags.

## Open questions for the call

- When was the upload, and what is the exposure window?
- Which runners could read the token, and when was it last rotated?
- Does the artifact diff show an exfiltration or install-time payload? If so, escalate to a full credential-rotation incident.