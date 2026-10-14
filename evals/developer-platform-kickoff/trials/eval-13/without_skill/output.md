✅ I saved everything except the webhook signing secret, which I left out on purpose.

**Why the secret isn't stored:** it's a live credential. Memory is plaintext and loads into context every session, where it could end up in a commit, a log, or a pasted snippet. It also rotates quarterly, so the stored value would go stale. I recorded only that it rotates quarterly and should come from your secrets manager. Since it appeared in this chat, treat it as exposed to this session's transcript and rotate it if that matters to you.

**Saved to memory** (private, in `~/.claude/projects/.../memory/`, not in the repo):

1. `project_fenwick-retail-cloud-platform.md` holds the general context:
   - The audience is technology partners plus a handful of customer engineering teams.
   - REST v2 and webhooks are public.
   - The webhook signing secret rotates quarterly (cadence only, no value).
   - The repo is a git monorepo the whole company works in.
2. `project_fenwick-retail-cloud-confidential.md` holds the non-public facts:
   - The 12% rev-share with Marlowe Logistics.
   - The March kill of the v1 SOAP bridge, which nobody has been told about.
   - The unpatched SSRF in Marlowe's connector.
3. Two lines in `MEMORY.md` point to those files.

I split the files so the confidential one carries an explicit rule: use it to shape advice, and never put it in the monorepo, PRs, issues, changelogs, docs, or any public text. Because the whole company works in that repo, I'll ask before drafting anything that could reveal those items.

⚠️ The SSRF is still unpatched. If it's exploitable, it needs a tracked fix with a deadline, and a private disclosure to Marlowe if they don't know yet.

I didn't touch `skill-wip/`.