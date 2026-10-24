# Decision: build it, but not the way you proposed

**Go on the Plugin Framework rewrite with your own naming. Don't publish under your lead engineer's account.** Set up the org namespace first. It takes hours, not weeks.

I haven't inspected the community repo, the Registry, or HashiCorp's current partner terms, so I've marked the claims you should confirm.

## What changes in your plan

| Your plan | Verdict |
|---|---|
| Rewrite on Plugin Framework | ✅ Keep. SDKv2 is legacy, and a new provider should start on the Framework. |
| Own attribute naming (`interval_seconds`) | ✅ Keep. Do it now, because renaming after v1 means a major version bump. |
| Publish under the lead engineer's account, move later | ❌ Drop. |
| "70% of enterprise buyers require IaC" | ⚠️ Don't use it. I can't verify the stat, and you don't need it. Two deals asking is your evidence. |
| Wait for the maintainer | ⚠️ Don't block on them, but make one better attempt (step 1). |

## Why the personal account is the one real mistake

- **The namespace is part of the address.** Users write `source = "<namespace>/brightmoor"`. Moving from a personal namespace to the org later changes the address for every user. Each of them then has to run `terraform state replace-provider`, and you will have trained them on the wrong address.
- **Partner tier requires the org.** I believe Partner-tier providers must be published under the vendor's own verified org through HashiCorp's technology partner program. Confirm the current terms. A personal namespace likely can't qualify, so the plan would fail the requirement the deals are asking for.
- **A person owns the release key.** Registry publishing uses a GPG signing key. If it lives with one engineer, you have a bus-factor and IP-ownership problem.
- **The fix is cheap.** Create or verify the GitHub org, add the Registry namespace, and generate a release key owned by the company. This is about a day.

## What the deals probably need

Partner status takes HashiCorp review time, and I'd assume weeks. You have about 10 weeks until quarter end (today is 2026-10-24).

- **Ask both prospects for the exact questionnaire wording.** "HashiCorp Partner provider" may be satisfied by an official, signed, vendor-owned, documented, supported provider. That is reachable this quarter.
- **Never claim Partner status before you have it.** In the questionnaire, state the facts: vendor-published, signed, with acceptance tests, plus a partner application in progress with a date.

## About the community provider

- MIT license means you may fork it. You don't need to, because a rewrite under a new address shares nothing with it technically.
- Its 1.4M downloads stay attached to `jhalvorsen/brightmoor`. They won't transfer to you.
- It is still useful in two ways. Mine its 60 open issues for real user needs and gaps. Treat its resource coverage as your minimum scope.
- Two weeks of silence after one DM is thin outreach. Try once more, in a way that is easy to say yes to (step 1).

## Plan

**Week 0, this week**
1. Send the maintainer a short email plus a GitHub issue mention. Say that Brightmoor is launching an official provider. Offer credit and a pointer from the new README. Offer a role if they want one. Set a 10-day deadline. Silence is a fine answer.
2. Create or verify the GitHub org. Claim the Registry namespace. Generate the release GPG key and store it in your secrets manager.
3. Open the HashiCorp technology partner application. Record the stated requirements and timeline.
4. Get the exact wording from both deals.
5. Inventory your API and map issue themes to resources. Choose the v1 scope: the resources the two deals need first (likely monitors, alert contacts, status pages, maintenance windows).
6. Freeze the naming rules: API names verbatim, Terraform conventions for the rest, `Sensitive` where needed.

**Weeks 1–2, vertical slice**
- Scaffold from HashiCorp's Framework scaffolding template under the org repo `terraform-provider-brightmoor`.
- Ship one resource end to end with CRUD, import, and acceptance tests against staging.
- Set up goreleaser with signing. Publish `v0.1.0` as a prerelease to prove the pipeline.

**Weeks 3–6, breadth**
- Add the v1 resources and data sources.
- Generate docs with `tfplugindocs`. Add examples and acceptance tests per resource.
- Add import support everywhere. Handle API pagination, rate limits, and drift.
- Add the OpenTofu registry listing, which is cheap.

**Week 7, `v1.0.0`**
- Publish a migration guide from the community provider. Test the path on a real config before documenting it:
  - Attribute names differ, so I expect `state replace-provider` alone to fail on schema mismatch.
  - The likely working path is import blocks plus `-generate-config-out`. Verify this in a spike.
- Add an attribute-mapping table (`check_frequency_secs` → `interval_seconds`).

**Weeks 8–10**
- Pursue partner review and answer HashiCorp feedback.
- Send both deals the registry link and the partner status.
- Announce it. Post a courteous deprecation pointer on the community repo only if the maintainer agrees or stays silent past the deadline.

## What I need from you

1. The exact questionnaire wording from both deals.
2. Is the GitHub org ready, and who owns the release key?
3. Which resources does your API expose, and which do the two deals actually need?

Once you have answers, I can draft the maintainer email and the partner-application checklist.