# What to do about Pipeworks CRM Sync

**Verdict:** Don't do any of the growth lead's three ideas. Each one breaks a WordPress.org rule, and the first two can get the plugin closed. The causes of the page-4 ranking are the stale release, the stale "Tested up to", the unanswered forum threads and the tag list. All four are fixable this month.

## Assumptions

I couldn't ask, so these are assumptions. Tell me if any is wrong, because #1 and #2 change the plan.

1. Your paid plan is enforced by your service, and the plugin only displays it. If the plugin locks features locally, fix that first: every release gets reviewed again for trialware (Guideline 5).
2. The plugin was submitted from a company account, and the brand is yours. If it came from an agency's personal account, move it to a company account.
3. You have fewer than 10,000† installs, so no written closure or transfer request is needed.
4. "hubspot" and "salesforce" are competitors of your service, not integration targets.

## The three suggestions

| Idea | Verdict | Why | Do this instead |
|---|---|---|---|
| Commit to SVN daily to look fresh | ❌ No | Rapid-fire commits to look recent break Guideline 14. SVN is a release channel, not your working repo. Ranking decays after about 6 months† without a real update, so a real release fixes the problem. | One real release this month, then real releases afterward. |
| 20% discount for 5-star reviews | ❌ No | Never ask for, pay for or seed reviews. An employee's conduct can close every plugin the owner has. | Earn reviews by solving forum threads. A discount that isn't tied to reviews is a pricing decision on your own site, not a review lever. |
| Answer paid-plan billing questions in the forum | ❌ No | Only the free plugin gets support in the forums. | Reply with one pointer to your own paid-support channel and keep billing details out of the thread. Email the Plugins Team to opt into the Commercial label, which adds a support URL to the listing. |

## What is actually hurting you, most urgent first

### 1. Support contact auto-replies 🔴

- Auto-replies that continue after warnings can close every plugin the account owns. Rule 6 requires every committer to have 2FA and an email a person reads.
- **Today:** Change each committer's WordPress.org email to a mailbox a person reads. Exclude `wordpress.org` senders from the helpdesk auto-reply as well. Confirm 2FA on every committer.
- Add your support staff as Support Representatives, not committers.

### 2. 60% of forum threads unanswered 🟠

- The resolved-thread share is a ranking multiplier, and it is also the only legitimate way to earn reviews.
- **Week 1:** Triage every open thread. Answer it, or send paid-plan questions to your own channel, then mark it resolved.
- **Ongoing:** Set a support routine of one named owner, checked daily at first, then twice a week. Track the resolved share.

### 3. Stale release and "Tested up to 6.2" 🟠

- Ranking drops after about 6 months† without an update, and also when "Tested up to" is stale. You are 14 months out and several majors behind.
- **Week 2:** Test against the current WordPress major. Then ship a real release with these steps:
  1. Run Plugin Check, Security category included. It also runs on every update you ship.
  2. Bump `Version` in the main file, set `Stable tag` to a real tag (never `trunk`), and add a changelog entry.
  3. Commit `trunk/` and copy it to `tags/<version>`.
  4. Turn on Release Confirmation.
- Budget the 6-hour† cooldown before sites see the release. A high security score blocks that version while the listing stays up. If that happens, fix the findings and ship a new version rather than appealing by email.
- Include in the same release the readme work in #4 and a check that the readme has an "External services" section. It must name your API host, the data sent, the trigger, and links to your terms and privacy pages.

### 4. Readme tags (18) 🟠

- Only the first 5 tags count. More than 12† is spam under Guideline 12. A competitor's name in a tag is banned.
- **In the same release:** Cut to 5 tags and drop `hubspot` and `salesforce`. Put your strongest 5 first, for example `crm`, `crm sync`, `lead capture` and your category terms.
- Competitor names don't belong anywhere in the tags. If you do integrate with a named platform, say so in the description, and only if it is true.

### 5. The `crm` head term 🟢

- Head terms rarely move away from high-install plugins, and install count is a log-scale multiplier. Don't expect page 1 for `crm` at about 2k installs.
- Aim at long-tail phrases of the form "<their product> <your category>", where their product is what your plugin connects to. Examples are a form builder, a store or a membership plugin. Put those phrases in the title, excerpt and description.
- Text-match weight runs: title and slug first, then author and contributors, then excerpt, description and tags.

## Timeline

1. **Today:** fix the committer emails and the auto-reply, and confirm 2FA.
2. **Week 1:** clear the forum backlog and send the Commercial label opt-in email.
3. **Week 2:** test, ship the release (Plugin Check, tag cuts, readme), and wait out the 6-hour† cooldown.
4. **Weeks 3 to 8:** keep the support routine. Pick 2 or 3 long-tail phrases, rewrite the title and excerpt for them, and watch rank.

## What to watch

- Resolved-thread share. The target is above 90%, checked weekly.
- "Tested up to" matches the current WordPress major.
- Connected sites as a share of active installs.
- Rank for your 2 or 3 long-tail phrases, not for `crm`.
- Zero closure or warning emails.

† Verify against the current developer.wordpress.org handbook and make.wordpress.org/plugins; the release process changes often.