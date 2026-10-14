# Recommendation

**Commit to 12 months of maintenance for v2, counted from the v3 general-availability date.** Publish the policy publicly, with a calendar date for each release.

I haven't checked AWS's current wording, so confirm it before you reply. As I recall, AWS's SDK maintenance policy gives maintenance mode a floor of at least 12 months. The exact terms matter because procurement will compare the two documents line by line.

## Decisions to make before publishing

Engineering and legal should sign off on these. The page is only as strong as they are.

1. **Define "maintenance" narrowly.** Promise only what you can staff: critical bug fixes and security fixes. Say explicitly that there are no new features and no support for new API capabilities.
2. **Start the clock at v3 GA, not at the announcement.** An announcement-based clock is ambiguous. A GA-based clock gives a date procurement can put in a calendar.
3. **Check the backend.** A client library is only supported if the service it talks to still accepts it. The page must say that the v2 wire protocol and endpoints keep working for the same window. If your backend can't promise that, the library promise is empty.
4. **Don't promise more than 12 months publicly.** If Verity Cloud needs more, put it in their contract as a customer-specific commitment. A public page you later shorten is worse than a contract clause you extend.
5. **Name an owner.** Someone must be accountable for the date, the security-fix SLA, and the end-of-support notice.
6. **Check the v3 release date.** The page can't go live until v3 has a GA date, or at least a committed target.

## Published page

> # Client Library Support Policy
>
> *Last updated: [DATE]. Applies to all official [Company] client libraries: [list: Node, Python, Go, Java, …].*
>
> ## Summary
>
> When we release a new major version of a client library, we continue to maintain the previous major version for **at least 12 months** from the new version's general-availability date. We announce the end-of-support date at least **6 months** before it takes effect.
>
> ## Support phases
>
> | Phase | What we provide | Duration |
> |---|---|---|
> | **Active** | New features, bug fixes, security fixes, support for new API capabilities | Until the next major version reaches general availability |
> | **Maintenance** | Security fixes and fixes for critical defects. No new features. No support for API capabilities introduced after the phase begins. | At least 12 months from the next major version's general-availability date |
> | **End of support** | No releases, fixes, or support. Prior releases remain available in package registries. | After the maintenance phase ends |
>
> A *critical defect* is one that causes data loss or corruption, incorrect results, or loss of the library's core functionality, and has no reasonable workaround.
>
> ## Current schedule
>
> | Version | Phase | General availability | Maintenance begins | End of support |
> |---|---|---|---|---|
> | v3 | Active | [DATE] | n/a | n/a |
> | v2 | Maintenance from [DATE] | [DATE] | [v3 GA DATE] | **No earlier than [v3 GA DATE + 12 months]** |
> | v1 | End of support | [DATE] | [DATE] | [DATE] |
>
> ## Service compatibility
>
> During a version's maintenance phase, the [Company] API continues to accept requests from that version of the library. We will not remove API endpoints or behavior that a supported library version depends on without the notice described below.
>
> ## Notice of end of support
>
> We publish the end-of-support date for each version at least 6 months in advance, on this page, in the changelog, and by email to account owners. We do not shorten a published end-of-support date, except as described below.
>
> ## Exceptions
>
> - **Security.** If a vulnerability cannot be fixed without a breaking change, we may ship the fix in the supported version with that change and document it prominently. If it cannot be fixed in a maintenance-phase version at all, we will tell you, and we will help you migrate.
> - **Third-party runtimes.** When a language runtime or a critical dependency reaches its own end of life, we may stop supporting that runtime in maintenance-phase versions. We follow the same 6-month notice wherever possible.
>
> ## Migrating
>
> The v2 → v3 migration guide is at [URL]. For questions, contact [support channel].

## Reply to procurement

> We commit to a minimum of 12 months of maintenance for v2 after v3 reaches general availability, covering security fixes and critical defect fixes, with the API remaining compatible with v2 for that period. We'll give at least 6 months' notice of the end-of-support date. The policy is published at [URL], with calendar dates for each version. [If agreed: Our agreement with Verity Cloud will additionally commit to X.]

## Open points

- **Security-only tail.** Offering 12 months of maintenance plus 6 months of security-only fixes costs little and reads as stronger than AWS. Do it only if you're willing to staff it.
- **Contract language.** Legal should decide whether the public page is incorporated into the contract by reference. If it is, its wording becomes binding and later edits become a negotiation.
- **Migration guide.** A support policy without a migration guide looks like a deadline with no help. Ship the guide with the page, or the "migrating" link will be dead.