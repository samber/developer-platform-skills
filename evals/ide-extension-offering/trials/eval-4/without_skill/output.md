Change the plugin ID to `com.pinewick.plugin` now, before first upload. Six more parts of the plan break, ranked below by damage.

I wrote this from memory of the JetBrains platform and did not check current docs. Items marked **verify** are the ones to confirm first.

## Breaks, worst first

**1. Plugin ID rename: beta users orphaned.**
- The ID is the plugin's identity on Marketplace. Changing `com.pinewick.beta` to `com.pinewick.plugin` creates a new plugin.
- Beta users get no upgrade. Ratings, download count and settings stay behind. Both plugins can end up installed and fight over `.pinewick` files.
- Fix: publish as `com.pinewick.plugin` from day one. Run beta through a Marketplace release channel (for example `beta`), not a separate ID.

**2. LSP API: "same diagnostics in Android Studio" is not guaranteed.** (**verify**)
- The IntelliJ LSP API was Ultimate-only when introduced in 2023.2. As I remember, it opened to Community builds around 2025.1.
- Android Studio ships on an IntelliJ Community base that lags JetBrains releases by months. Android Studio versions on an older base have no LSP API. Android Studio is one of your named targets.
- The API also covers only a subset of LSP features, and the subset varies by platform version.
- Fix: check which Android Studio versions your users run and what platform build each uses. Compare that with when the LSP API reached Community. If the gap is large, use LSP4IJ (Red Hat's open-source LSP client plugin). It works on Community and older builds, but it adds a plugin dependency.
- Syntax highlighting is not part of LSP. You need a TextMate bundle or a native lexer, plus a registered `.pinewick` file type.

**3. Gradle defaults break compatibility.** (**verify**)
- The IntelliJ Platform Gradle Plugin derives `sinceBuild` from the platform version you compile against. If you compile against the newest IDE, the plugin refuses to install on every older IDE, including Android Studio.
- `untilBuild` is open-ended by default, so a future IDE release can break you silently.
- The JDK requirement tracks the platform too (JDK 21 for recent builds).
- Fix: set `sinceBuild` to the oldest build you will support. Set `untilBuild` on purpose. Depend only on `com.intellij.modules.platform` so the plugin loads in IDEA Community and Ultimate, Android Studio, and the other JetBrains IDEs. Run `verifyPlugin` (Plugin Verifier) in CI against IDEA Community, IDEA Ultimate and Android Studio, on the oldest and newest builds.

**4. Telemetry consent does not transfer.**
- The IDE's data-sharing consent covers JetBrains' own statistics. It does not cover your plugin sending data to your servers.
- Android Studio has its own Google-side consent, which is different again.
- Marketplace expects third-party data collection to be disclosed in the listing and privacy policy. GDPR applies too.
- Your contract files may hold sensitive endpoints and payloads, which raises the stakes.
- Fix: add a plugin-level opt-in, off by default. Document exactly what is sent. Link a privacy policy from the listing. The VS Code extension's consent flow is a model, but the code is new.

**5. Same-day hotfix is not possible on Marketplace.** (**verify review time**)
- JetBrains reviews plugin updates before they go live. As I remember, this takes up to a couple of business days. VS Code's `vsce` publish is instant.
- Users also pull updates on the IDE's own cadence.
- Fix options:
  - Ship a kill switch or feature flag read from your server, so you can disable a bad feature without a new build.
  - Host a custom plugin repository (an `updatePlugins.xml`). Offer it to beta and enterprise users for faster delivery. Stable users still wait on Marketplace.
  - Make the plugin dynamic (no restart on update).
  - Check the Marketplace policy before you consider downloading server binaries at runtime. Bundling the server is the safe path.
- Set expectations: JetBrains hotfix SLA is 1 to 3 business days.

**6. Staffing: 55% of users get half of one developer.**
- Half-time on one person gives you a bus factor of one. That person also still carries the VS Code extension.
- Scope is bigger than LSP. If the VS Code extension has anything beyond language features (mock server start/stop, tree views, webviews, status bar), each needs native work. That means Kotlin, Swing or the Kotlin UI DSL, JCEF for webviews, and run configurations.
- Your VS Code developers know TypeScript. The JetBrains platform is Kotlin or Java, with a different API and a steep learning curve.
- Fix: scope the MVP as LSP diagnostics plus file type plus highlighting. Add the rest in later releases. Either add a second person part-time or accept that the plugin ships slowly.

## Also check

- **Language server runtime.** VS Code ships Node inside Electron. JetBrains IDEs do not guarantee Node. If your server is Node, bundle a self-contained binary per OS and architecture (macOS arm64 and x64, Windows x64 and arm64, Linux). Otherwise the server fails to start on some users' machines.
- **Test matrix.** IDEA Community, IDEA Ultimate and Android Studio, each on at least two versions, on macOS, Windows and Linux. Android Studio also has Canary and Beta channels.
- **"Rest elsewhere" (the 10%).** A platform-only dependency (item 3) also covers WebStorm, PyCharm, GoLand and Rider at no extra cost.

## Next action

Rename the plugin ID in `plugin.xml` and `build.gradle.kts` to `com.pinewick.plugin` (2 minutes). Then check which platform build your users' Android Studio versions run on, to settle item 2.