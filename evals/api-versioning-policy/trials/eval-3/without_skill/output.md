# Trackpole API Deprecation Policy (v1.0)

I changed your draft substantially instead of polishing the line. Three problems made it unsafe to publish, and the policy below fixes them.

1. **The two consumer groups can't share one window.** Third-party mobile apps ship through app-store review. Their users update slowly, and old app builds stay in the field for months. Internal services have named owners you can contact and coordinate with, so they don't need the same terms.
2. **The start date matters a great deal.** If sales is told it doesn't matter, they may promise the wrong thing to a customer. "6 months from release" could leave a consumer with 2 weeks of notice if you deprecate a version that is already old. Only "from the deprecation notice" gives a guaranteed minimum, so the policy uses that.
3. **The competitor comparison is a weak basis.** Their 3 months only shows what they chose. What matters is how long your mobile consumers need to migrate, and I'd verify that against your own traffic data.

## Policy text

**1. Definitions**

- **Deprecated:** The version still works and receives security and critical-bug fixes only. It gets no new features, and we recommend that consumers migrate.
- **Sunset:** The version stops serving requests. After the sunset date, requests return `410 Gone`.
- **Notice date:** The date we first send the deprecation notice (see §4). The support window is measured from the notice date, never from the version's release date.
- **Supported:** During the window, the version keeps its published behavior, availability target and security fixes. We make no breaking changes to it.

**2. Support windows**

| Consumer group | Minimum window, notice date to sunset |
|---|---|
| Third-party apps (public API keys) | **12 months** |
| Internal services | **6 months**, and sunset requires owner sign-off (see §3) |

**3. Sunset gates**

- **Third-party:** At the end of the window we may sunset the version. Before we do, we will send a final notice 30 days ahead, and we will brownout the version with short scheduled outages 60 and 30 days ahead.
- **Internal:** We won't sunset while any internal service still calls the version, unless its owning team has signed off. Platform tracks each service's usage per version. Teams that can't migrate in time must file an exception with a date, and exceptions are reviewed quarterly.
- **Extensions:** The window can be lengthened but never shortened. We announce any extension in the same channels as the original notice.

**4. How we notify**

1. We email the registered contact for every API key that called the version in the last 90 days.
2. We post to the developer changelog and the status page.
3. We add `Deprecation` and `Sunset` response headers to the affected version, with a link to the migration guide.
4. We show a banner in the developer dashboard.
5. For internal services, we post to the owning team's channel and open a tracking ticket assigned to its owner.

Every notice states the notice date, the sunset date, the replacement version and the migration guide link. Developers must keep a valid contact email on their account. Emailing that address counts as notice.

**5. Exceptions**

We may shorten the window in these cases only:

- an unpatchable security vulnerability
- a legal or regulatory requirement
- a third-party dependency that ends support for us

In these cases we give as much notice as we can and describe the reason in the notice. We expect to use this rarely and will report each use publicly.

**6. Scope and non-breaking changes**

Additive changes don't count as breaking and need no deprecation. Examples are new fields, new endpoints and new optional parameters. Consumers must tolerate unknown fields in responses. Removing or renaming a field, changing a type, changing semantics, or tightening validation does count as breaking. Any breaking change ships as a new version.

**7. Migration support**

Each new version ships a migration guide before the deprecation notice goes out. We publish version adoption figures and we respond to third-party migration questions through the usual support channel.

## Answer for sales

The window starts on the day we send the deprecation notice. It never starts at release. They can say: "Any version you build on gets at least 12 months' notice before it is turned off."

## What I need you to confirm

I chose the numbers below from judgment, not from your data. Check them before you publish.

- **12 months for third-party apps.** Pull the version-adoption curve from past API changes if you have one. If 90% of traffic moves within 6 months and the tail is small, 9 months may be enough. If not, 12 months is the safer choice.
- **6 months for internal services.** The sign-off gate in §3 is what protects the internal teams, so the number itself is less critical.
- **Brownouts.** They need engineering effort. Drop them from §3 if you can't build the tooling yet.
- **Legal and engineering.** Get both to look at the 12-month commitment and the §5 exceptions before this goes public. A public SLA-style promise is hard to retract.