# Verity Cloud: v2 client library support commitment

I followed `sdk-portfolio-strategy`, steps 5 and 6 (versioning split, deprecation and EOL playbook), plus its tier and EOL references. I couldn't run the interview, so the assumptions are listed at the end. Please confirm them before legal publishes anything.

## Recommendation

**Commit to 18 months from v3 GA, in two phases: 6 months of full support, then 12 months of maintenance.** A floor of 12 months of maintenance is what procurement is asking for, and this gives them that. Don't offer "12 months total".

- AWS's 12 months is the maintenance phase only. Its core SDKs-and-Tools policy sets that default at 12 months.
- AWS announces maintenance at least 6 months ahead, normally alongside the next major's GA.
- So the real AWS gap between v3 GA and end of support is about 18 months.
- Matching "12 months from v3 GA" would give them less than AWS gives, and procurement will notice.
- AWS's own policies disagree: Powertools defaults to 6 months of maintenance.
- AWS also flexes the default. JS v2 got 12 months, and .NET v3 got 3.

Cite the AWS core policy by name, and never write "AWS's policy" as if it were one number.

Why 18 and not 24 or more:

- Each extra month means two supported majors in every language.
- The skill treats maintenance as a standing cost. It does not recommend open-ended promises.
- Make the number a floor ("at least"), not a ceiling.

## Policy page text (draft for legal)

> **Verity Cloud Client Library Support Policy**
>
> *Applies to official Verity Cloud client libraries in every language we maintain. It does not apply to community-built libraries, which Verity does not support. Last updated: [date].*
>
> **Versioning.** Each client library uses Semantic Versioning. We release a new major version only when the library's own interface changes in a breaking way. A new Verity API version does not by itself require a new library major. The table below lists which API versions each library major supports.
>
> **Support phases for each major version**
>
> | Phase | What you get | Minimum duration |
> |---|---|---|
> | **General Availability** | New features, bug fixes, security fixes | Until the next major version is released, plus 6 months |
> | **Maintenance** | Critical bug fixes and security fixes only. No new features or new API coverage | At least 12 months |
> | **End of support** | No further releases. Packages stay on their registries and are marked deprecated | n/a |
>
> **Commitment.** When we release a new major version, we publish a maintenance announcement the same day. The previous major stays in General Availability for at least 6 months after that announcement. It then moves to Maintenance for at least 12 months. **That is at least 18 months of support from the release of a new major version.**
>
> **Announcement.** We announce through a pinned deprecation issue in each library's repository, the changelog, our documentation, and the package registry deprecation marker. Each announcement names the reason, the successor version, the migration guide, and the dates.
>
> **API compatibility.** Verity will keep serving every API version a supported library major depends on until that major reaches end of support.
>
> **Host language versions.** This is a separate policy. Each library supports the language runtime versions listed in its README. When a runtime reaches upstream end of life, we may drop it from the library after at least [6] months' notice. This does not shorten the support period of the library major.
>
> **Exceptions.** Maintenance does not apply to a library running on an unsupported runtime or against an API version we retired under our API deprecation policy. Security fixes may require a minor-version bump.
>
> **Changes to this policy.** We will not shorten the support period of a major version that has already been announced. Changes to this page take effect only for majors released after the change.
>
> *Version-to-API mapping table: [link]*

## Reply to procurement (draft)

> Verity commits to supporting each previous major version of our client libraries for at least 18 months after a new major is released. That is 6 months of full support, then at least 12 months of maintenance with critical bug and security fixes. It is published at [URL] and we will not shorten it for a major we have already announced. This matches the structure of AWS's core SDK maintenance policy, and in practice goes beyond its 12-month maintenance default. The policy covers our official libraries, not community-built ones.

## Decisions needed before it goes live

1. **Contract wording.** The "will not shorten announced periods" line carries the weight. Legal decides whether the contract references the page or copies the numbers. A policy page that can change freely is not what a seven-figure buyer is asking for.
2. **The API-compatibility sentence.** It binds the API team. Without it, the library commitment can be hollow. I assumed the API-versioning policy allows it, but I haven't checked.
3. **The 6-month runtime notice** is a placeholder I picked. The skill says to tie runtime windows to upstream language lifecycles plus a stated grace window. No vendor publishes a universal number for this.
4. **Every number here is a self-set policy choice.** The 6, 12 and 18 months are not an industry standard.

## Assumptions I made without asking

- v3 is real and scheduled, and it ships with a migration guide.
- Every official language SDK gets the same schedule. No language is being retired.
- We can afford to maintain two majors per language for 18 months.
- Verity Cloud's own contract doesn't already promise something different.
- Procurement's AWS claim is accurate enough. I haven't re-checked AWS's current pages.

If any of these is wrong, tell me which and I'll redo the numbers.