# Rosterly: safest sequence

**Don't turn off public distribution.** Deactivate Public Distribution uninstalls the app from every other workspace, and a listed app can't use it. Rosterly is listed, so that switch would wipe your install base. It would also put you back under the install gate (10 or more active workspaces†) and a new review of up to 10 weeks†. Nothing in the Slack playbook gives you a way to pause new installs, so I haven't offered one.

**Don't enable token rotation in production first.** It is irreversible. Each token must be refreshed within 12 hours†, and every new refresh token must be persisted. A bug in your refresh code on the live app breaks every workspace at once. Enable it on the staging app first.

## Assumptions

- Rosterly is currently listed, not an unlisted pilot.
- The rewrite changes features, and possibly scopes. A rewrite counts as a new feature or scope change, so it needs a resubmission.
- Enabling rotation on the live app is a configuration change. Configuration changes go through resubmission too, so rotation rides along with the rewrite.
- You still have 10 or more active workspaces†. Check that count now, because the uninstall spike may have lowered it.

## Sequence

**Step 0: this week, protect the listing.** This is your biggest risk, not the rewrite.
1. Tripled uninstalls plus unanswered tickets is the profile Slack contacts you about. If it goes unanswered, Slack delists while it retries.
2. Name a stand-in for the departed support engineer.
3. Answer the backlog, and commit to replies within 2 business days†.
4. Update the developer, support and security contacts on the app.
5. Add a second collaborator to the app.
6. Check the support page, privacy link and landing page for breakage. A broken landing page or install flow means delisting without notice.
7. Check your own `app_uninstalled` ledger to find what the bad release broke.

**Step 1: keep installs working.** If you want fewer new installs during the rebuild, do it on your side. Add a notice on your landing page or a waitlist. Never break the install flow itself, because that is a delisting trigger.

**Step 2: build the rewrite off-production.**
1. Keep one manifest template in your repo.
2. Create `<app>-dev` with distribution off.
3. Create `<app>-staging` with distribution on, never listed.
4. Give each app its own secrets and tokens. Never share tokens between environments.
5. Don't ship the rewrite into the live app. A substantial change shipped without review is a delisting trigger.

**Step 3: enable token rotation on staging only.** Soak it for at least a full week and several 12-hour† cycles. Test:
- the refresh path
- concurrent refreshes
- a failed refresh
- a restart that loses in-memory tokens

Existing workspaces carry their own tokens, so plan how they move to rotating tokens on reinstall.

**Step 4: resubmit once, with everything bundled.**
1. Diff the manifest template against the live app (`apps.manifest.export`). That diff is the reviewers' change list.
2. Give reviewers the staging install link and a video showing each new feature and how each new scope is used.
3. Justify every new scope one by one.
4. Update the Security & Compliance "token rotation" answer to yes.
5. Remove test slash commands and clear the automated checks.
6. Fix all feedback in one pass. Each preliminary resubmission resets your queue position.

The live listing stays up during review.

**Step 5: after approval, stagger the rollout.**
1. Update the OAuth URL only after approval. An unreviewed scope in the live install URL makes installs fail.
2. Switch rotation on in production.
3. Ask existing workspaces to reinstall through App Home or a message.
4. Watch uninstalls and errors closely for the first week.

## Timeline (today is 2026-10-30)

| Step | Duration† | Date |
|---|---|---|
| Rebuild | about 1 month | to about 11-30 |
| Preliminary review | up to 10 business days | about 12-14 |
| Functional review (updates) | up to 6 weeks | about late January 2027 |
| One returned round | about 2 more weeks | early February |

Holidays may stretch this, and functional review can't be expedited. Plan for February, and don't promise customers a date.

† Verify against current Slack Marketplace docs. Slack has changed its install gate twice in a year.

## Questions for you

1. Does the rewrite add or change scopes, or move from classic to granular permissions? Granular forces every workspace to reinstall.
2. Do you want rotation shipped with the rewrite (one review, bigger blast radius) or as its own resubmission (an extra review cycle, but a safer rollback story)? I lean toward bundling, since rotation already soaks on staging.
3. Do customers use Enterprise Grid or Slack Connect? If so, test org-ready deployment before resubmitting.