**Do not run the plan as written. Four things break it, and the endpoint sunset is the most urgent.**

**Next action (under 2 minutes):** ask platform engineering for two things. First, the exact `/v1/employees` shutdown date. Six weeks from today is about 2026-12-04. Second, whether `id` values are identical between `/v1` and `/v2`.

I didn't read `skill-wip/`, per your instruction, and I ran no tools against your repo. Zapier platform behavior below comes from my knowledge of the platform. Items marked **verify** need a check against current Zapier docs or your Zapier partner contact before you commit dates.

## Verdict

- **Two unrelated changes are tangled in one plan.** The OAuth2 move has a deadline of end of Q1. The endpoint move has a deadline of about 2026-12-04, three or more months earlier.
- **The endpoint deadline kills the plan.** Every 1.x version calls `/v1/employees`. Under your timeline, 1.x stops working at the sunset, long before the OAuth2 migration finishes.
- **The OAuth2 migration is harder than `migrate … 100` suggests.** Migrate moves Zaps between versions. It cannot create OAuth2 tokens for 2,400 connections that only hold a username and password.

## Findings, by severity

### 🔴 1. The `/v1` sunset breaks 1.6.0 first

Both `new_employee` and `find_employee` call `/v1/employees`. In about six weeks every Zap using them fails on every 1.x version. That includes 1.6.0 and anyone you haven't migrated.

**Fix: ship a 1.7.0 now, before 2.0.0.**
- 1.7.0 keeps basic auth and moves both operations to `/v2/employees`.
- Its output must stay shape-compatible with 1.6.0 (see finding 3).
- Because it's non-breaking, migrate users to it gradually, e.g. 1% → 10% → 50% → 100%. Finish at least two weeks before the sunset.
- Ask platform engineering for a sunset buffer or brownouts. Ask for a per-client log of `/v1` callers so you can find Zapier stragglers.

### 🔴 2. Basic → OAuth2 is not a plain migrate

- A migrated Zap keeps its stored connection. A basic-auth connection has no access token or refresh token, so the Zap fails on its first run.
- Users must reconnect through the OAuth consent screen. Zapier does not automate this. **Verify** with Zapier whether it blocks or restricts `migrate` across auth types, and how it handles auth changes on public integrations.
- Treat 2.0.0 as a breaking release for all 2,400 users. `migrate 100` would flip every Zap onto a version with no valid credentials.
- HR-specific risk: connections are owned by individuals. If the person who connected the Zap has left, nobody reconnects, and onboarding and offboarding automations fail silently.

**Fix:**
- Roll out with a small percentage first, to internal accounts.
- Pull the per-account list of Zapier-originated basic-auth traffic from your own API logs.
- Email account admins, not just Zapier users, and track reconnection per account.
- Keep 1.7.0 undeprecated until 2.0.0 has been stable for at least 30 days. A rollback to a basic-auth version is impossible once 1.x is gone.

### 🔴 3. `/v2` schema changes will break Zaps and templates silently

- **`name` → `given_name` + `family_name`.** Any Zap or template that maps `name` gets an empty value. Keep emitting `name`, built as `given_name + " " + family_name`, and handle a null family name or a mononym. Add the two new fields alongside it. Update `outputFields` and the sample data.
- **`hired_on` epoch seconds.** Confirm what 1.6.0 emitted, likely a date string. Keep that format and timezone for `hired_on` and add e.g. `hired_on_epoch` as a new field. Check seconds versus milliseconds. Zaps with filters or date-formatter steps depend on the old format.
- **`id` stability (highest risk).** If `/v2` ids differ from `/v1` ids, the `new_employee` polling trigger sees every employee as new. It re-fires for your entire HR population in every Zap. Test this before anything else.
- **Pagination and sort order.** Polling triggers need newest first. Check that `/v2` ordering and paging match `/v1`.
- **`find_employee` input semantics.** Check that search fields and matching behavior are unchanged.
- **6 live templates.** Open each, list the fields it maps, and test it end to end against 1.7.0 and 2.0.0. Update templates after each promote.

### 🟠 4. A 10-day deprecation notice is too short

- This is a 2,400-user HR integration where Zaps need human action to reconnect.
- Zapier's guidance, as I recall it, is far longer than 10 days, around 90 days. **Verify** the minimum, since Zapier also emails users itself.
- Working back from Q1 end (assumed calendar quarter, 2027-03-31): notice would need to go out by about 2026-12-31. You have about 10 weeks to build, test, pass Zapier review and promote.
- Zapier review of a promoted public version can take weeks. Start the OAuth2 work immediately.

### 🟠 5. "Delete the 1.x versions" is the wrong end state

- **Verify** that Zapier blocks deleting a version that still has users or Zaps. Deprecation with a date is the supported route.
- Deleting early removes your rollback target.
- What security review needs is server-side: stop accepting Zapier's basic-auth traffic on a set date. Do that with brownouts first, then a hard cutoff.
- After cutoff, tell users to rotate any password that was stored in Zapier.

### 🟠 6. OAuth2 server readiness is unstated

Confirm each of these exists before the 2.0.0 build starts:
- Authorization and token endpoints, refresh tokens, and revocation.
- Redirect URI registration for Zapier.
- Scopes limited to what employee data the triggers need.
- PKCE if you choose it.
- Behavior for SSO-only accounts that have no password.

In 2.0.0, configure OAuth2 refresh and test connection, and handle 401 by refreshing the token.

## Corrected sequence

| # | When | What | Done when |
|---|---|---|---|
| 1 | This week | Check `id` parity, pagination and sort order, and `hired_on` format against `/v2`. | Written findings. |
| 2 | Week 1–2 | Build 1.7.0: `/v2` calls, `name` and date compatibility, new fields added. Run `zapier test` and `zapier validate`. Test all 6 templates. | Contract tests pass for v1 and v2 fixtures. |
| 3 | Week 2–3 | Promote 1.7.0. Migrate users gradually. | 100% migrated at least 2 weeks before `/v1` sunset. |
| 4 | In parallel, now | Build 2.0.0 with OAuth2. Confirm the OAuth2 server is ready. | Private-version test with internal accounts. |
| 5 | By about 2026-12-31 | Promote 2.0.0, publish the reconnect guide, notify admins. Set the deprecation date for 1.x (at least the Zapier minimum, ideally 90 days). | Per-account reconnect tracker live. |
| 6 | Before Q1 end | Brownouts of basic auth for Zapier traffic. Hard cutoff on the deprecation date. | No Zapier basic-auth requests in logs. |
| 7 | After cutoff | Rotate exposed passwords. Update templates to 2.0.0. | Security review closed. |

**Command check:** the Zapier CLI command is `zapier migrate <old> <new> [percent]`. **Verify** that `zapier-platform migrate` is a valid alias in your CLI version with `zapier --version`.

**Two decisions for you:**
1. Confirm the Q1 end date and the Zapier minimum deprecation notice. They set whether step 5 fits.
2. Confirm the OAuth2 server owner and ETA. Without it, steps 4–6 have no date.