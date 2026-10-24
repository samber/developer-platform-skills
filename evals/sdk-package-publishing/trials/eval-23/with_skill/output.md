# Incident plan: rogue `dunmore-sdk` 2.8.1

**First: revoke the token you pasted. I did not use it, and it can't do what you want anyway.** PyPI has no API for deleting or yanking a release. Yank and delete are web-UI actions, done by an owner with 2FA. Anyone who has seen that token can still upload `2.8.2`, `2.9.0` and so on, so close that door before anything else.

I ran no registry commands and I'm not asking you for more secrets. Everything below is for you or your team to run.

## Assumptions

- You publish to public PyPI from self-managed GitLab CI. I don't know if the runners are self-hosted.
- The credential is a long-lived project-scoped token in a CI variable. The `AgEIcHlwaS5vcmc` prefix is the standard PyPI token header.
- The last good release is `2.8.0`. `2.8.1` was uploaded by someone else, probably through a stolen token, possibly through a hijacked pipeline.
- I assume `2.8.1` is malicious until proven otherwise. The cause is still a hypothesis. You need the evidence in step 3 before you can say "runner compromised".

## Before the call (about 15 minutes, in this order)

1. **Revoke the token now.** Do this first, because the token is now in this chat, in CI variables, and possibly in the attacker's hands.
   - PyPI → Account settings → API tokens → **Remove token** (or project Settings → if it's an org token).
   - Remove every other token on the project and on every owner account. Forgotten tokens were the second route in the Ultralytics incident.
   - Delete the CI variable in GitLab (Settings → CI/CD → Variables), including any copy in group or instance scope.
   - Also check the PyPI account is not compromised. Review the project's **Security history** and **Collaborators** (project → Settings), and confirm 2FA is on for every owner.

2. **Isolate the build hosts before touching anything else.** Pause the runners (GitLab → Admin/Group → Runners → **Pause**, or stop the runner service). Don't wipe or reimage them yet. Some worms wipe hosts when they lose access, and you need the disks for forensics. Revoke every other credential those jobs could reach:
   - GitLab CI variables and deploy tokens
   - cloud credentials
   - signing keys
   - the runner registration tokens
   - any SSH keys on the runners

3. **Preserve evidence before deleting.** Deletion is permanent, and the filename can never be reused. Capture what is public first, and never install it.
   - Fetch the metadata: `curl -s https://pypi.org/pypi/dunmore-sdk/2.8.1/json -o /tmp/dunmore-incident/meta.json`. It has file URLs, SHA-256 hashes, upload time and the uploader's attestation fields.
   - Download the files with `curl -o` to absolute paths under `/tmp/dunmore-incident/`. Do not use `pip install`. Do not use `pip download` on the sdist, because building its metadata can execute `setup.py`.
   - Unpack them in an empty directory and diff against `2.8.0`. Look for `.pth` files, a changed `setup.py`, `__init__.py` imports, network calls and base64 blobs.
   - Note the upload timestamp. Match it against GitLab pipeline and job logs, runner logs and the audit events. That is the proof of how it got out. If no pipeline of yours ran at that time, the token was used from elsewhere. That points to a leaked token, not the runner.

4. **Ship the fix first: publish `2.8.2`.** The runbook says never wait on a delete, and you can't reuse `2.8.1`.
   - Build from the last known-good commit (the `2.8.0` tag plus only reviewed changes) on a clean machine or fresh runner, not the suspect one.
   - Run `twine check --strict dist/*`, then list the sdist (`tar tzf dist/*.tar.gz`) and compare it to `2.8.0`.
   - Upload with a brand-new token scoped to this project only, from a clean environment. The `twine upload` or `uv publish` is a public action, so you or the release manager run it. Remove that token again once step 7 replaces it.
   - If you can't build clean within the call window, skip this step for now and do step 5 so users stop getting `2.8.1`.

5. **Pull `2.8.1` out of circulation.** Pick one:
   - **Yank (default, reversible):** PyPI project → Manage → Releases → `2.8.1` → Options → **Yank**. Use the reason text: "Unauthorized release, not published by Dunmore. Use 2.8.2 or 2.8.0."
     - A yank hides it from `pip install dunmore-sdk` and `>=` ranges. It does not stop `==2.8.1` pins or lockfiles.
   - **Delete (permanent):** the skill reserves this for malware or leaked secrets. This qualifies if the payload is malicious. Do it after step 3 has saved the artifacts: Options → **Delete**. The filename is burned forever.
   - **Report it:** email security@pypi.org with the package name, version and your findings. Malware reports let the PyPI admins quarantine the project and cut off an attacker you've already locked out. You get a human on the registry side, and I would do this alongside the yank or delete.
   - I would **yank now, then delete once evidence is saved and the call agrees**. A yank takes about 10 seconds and loses nothing. A delete cannot be undone.

6. **Check `latest` and consumers.** A malicious `2.8.1` may have been the newest version for hours. Find who installed it, using your download logs, customer reports and CI logs that resolved `dunmore-sdk`. Tell them to:
   - pin `2.8.0` or `2.8.2` and rebuild lockfiles
   - treat any machine that ran `2.8.1` as compromised and rotate its secrets

## After the call (next days)

7. **Replace tokens with trusted publishing.** This is the lasting fix, and it removes long-lived tokens from the picture.
   - PyPI supports GitLab trusted publishers, but self-managed support is beta. Check PyPI's docs today before relying on it.
   - If self-managed doesn't work yet, use a PyPI organization custom OIDC issuer. Otherwise fall back to a project-scoped token in a protected, masked variable, rotated on a schedule.
   - Publishing is done only from a protected tag, in its own protected pipeline, because on GitLab any job in the pipeline can mint an OIDC token. Add a protected environment with at least two approvers and self-review blocked.
   - Build once in an unprivileged job without secrets. The publish job only uploads the artifact. No restored caches in either job.
8. **Harden the runners.** Rebuild them from a clean image, use ephemeral runners where you can, and review which projects and users can run jobs on them. Apply the same tag protection to release tags so only release managers can create `v*` tags.
9. **Add consumer-side delay:** recommend `uv`'s `exclude-newer = "7 days"` or pip equivalents to customers, so a rogue release does not reach them in hours.
10. **Write it up:** a changelog entry and a security advisory naming `2.8.1` as unauthorized and `2.8.2` as safe. If it's malware, file it with the PyPA advisory database.
11. **Record in your context file:** registries (PyPI), CI (self-managed GitLab), the credential state (old token revoked, new model), and the rollback primitive (yank, with delete reserved for malware).

## Decisions for the call

| Question | Recommendation |
|---|---|
| Yank or delete `2.8.1`? | Yank now, delete after the evidence is saved |
| Pause all runners? | Yes, until you know whether it was the token or the runner |
| Public disclosure? | Yes, after `2.8.2` is out, with the advisory |
| Who owns the PyPI account? | At least two owners with 2FA, under a PyPI organization |

If step 3 shows no pipeline ran at the upload time, say so on the call. That points to a leaked token, not a compromised runner, and it changes what you rebuild. Whichever it is, the token in this chat counts as leaked and must be revoked.

I did not read your repo, so nothing here comes from your pipeline files. If you paste your `.gitlab-ci.yml` with secrets removed, I can draft the protected-pipeline version for step 7.