# Archive and redirect playbook

Load this file during step 6, when writing archive rules, and whenever a triage verdict says "archive with redirect".

## Contents

- Vendor precedents
- Archive sequence
- README banner template
- Redirect registry format
- Community hand-off label

## Vendor precedents

| Organization | Trigger | Mechanism | Signal to developers |
| --- | --- | --- | --- |
| Microsoft GitHub orgs (Azure-Samples, Azure, microsoft, OfficeDev) | No activity for over 2 years | Bot issue with a named owner, auto-archive after 30 days without action | GitHub archived banner |
| aws-samples | Owner decision | GitHub archive | README "archived and no longer maintained" |
| AWS SDK examples | SDK major deprecated | Old folder kept, unmaintained | README lists deprecated folders |
| Square | SDK end of life, in waves by language | Archive with migration guide | "RETIRED" README with EOL date and before/after code |
| Okta | Consolidation after acquisition | Security-patch-only mode, then archive | README notice |
| SAP | Samples moved to a new org | Archive old repo | README pointer to the new home |
| Expo | Example superseded | Removed from tree, kept in a `meta.json` deprecated and aliases list | Redirect message naming the modern example |

- Microsoft's bot states that archiving "will not prevent users from viewing or forking the code". Closing its issue counts as activity, so an untested sample can survive indefinitely: prefer CI-state triggers.
- Square shows two steps: retire (status and migration in the README) first, archive later. Okta shows a third posture between kept and archived: security patches only.

## Archive sequence

1. Confirm the trigger and the successor (or record "none").
2. Final commit: README banner, successor link, removal of deploy buttons and template-repository flag.
3. Remove from the canonical index's current list; add a redirect entry.
4. Remove from docs links, gallery, CLI sample list and agent index; point each at the successor.
5. Disable the dependency bot and scheduled CI; run one last secret scan.
6. Archive the repository read-only. Never delete.
7. Announce in the changelog when the sample was on the adoption path.
8. For a deploy template, say in the banner that copies already deployed keep running on their own keys, and tell owners to rotate any key the template ever printed or stored.

## README banner template

```markdown
> **Archived <YYYY-MM-DD>. This sample is no longer maintained or tested.**
> Reason: <superseded | SDK vX end of life | merged into <repo> | no longer supported>.
> Use instead: <successor link>. Migration notes: <link or "none needed">.
> The code stays readable and forkable; it may not work against the current API.
```

## Redirect registry format

Keep redirects in the same canonical index that drives docs, gallery, CLI and agents:

```json
{
  "samples": [
    { "id": "payments-quickstart", "type": "flagship-quickstart", "status": "current", "languages": ["node", "python", "java", "go", "ruby"] }
  ],
  "aliases": { "checkout-node-legacy": "payments-quickstart" },
  "deprecated": {
    "subscriptions-php-v2": { "status": "archived", "successor": "subscriptions-scenario", "message": "Use the subscriptions scenario; PHP is community-supported." }
  }
}
```

The `aliases` and `deprecated` split mirrors Expo's `meta.json`: old names keep resolving, and anything reading the index learns what replaced them.

## Community hand-off label

When archiving is vetoed, or a community maintainer wants to keep a sample alive, relabel instead:

```markdown
> **Community-maintained.** Not created, reviewed, or supported by <Platform>. Report issues in this repository.
> <If CI is red: **Currently failing CI** against the current API.>
```

Plaid labels its .NET quickstart this way; Workday labels its DevRel examples repo "not an officially supported" product. The label moves the row out of the capacity sum without breaking anyone.
