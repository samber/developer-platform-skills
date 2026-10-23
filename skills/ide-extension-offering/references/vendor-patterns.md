# Vendor patterns

Public examples of each pattern from step 1 and step 9. Read when choosing a pattern or writing a deprecation plan. Install counts are order of magnitude and change.

## Thin shell over the vendor CLI

- **Stripe:** webhook forwarding, test-event triggers, a live API-log stream, snippets and an API-key linter, all through the Stripe CLI, which must be installed (a `stripe.cliInstallPath` setting points at it). Webhook forwarding runs as a `launch.json` configuration (`"type": "stripe"`), so F5 starts the listener. Its own telemetry setting still yields to VS Code's.
- **Supabase:** inspects tables and functions and guides migrations through the locally running Supabase CLI.
- **MongoDB:** data browser and playgrounds, needs `mongosh` on `PATH`; the extension also bundles an MCP server for agent mode.
- **Salesforce:** an extension pack over the Salesforce CLI plus an Apex language server; asks users to stay within two months of the latest VS Code, a sign of tight host coupling.

## Shared core across editors

- **HashiCorp Terraform:** `terraform-ls` is the official language server for any LSP editor; the VS Code extension bundles it and adds UI. Other editors get the language features with no plugin.
- **Snyk:** the extension downloads the Snyk CLI, which embeds the language server shared by its other IDE plugins. It lists VS Code web and remote development as unsupported, the cost of a native binary.
- **Prisma:** a language server for `.prisma` schema files (completion, formatting, rename), later extended with database management UI.

## No extension needed

- **SchemaStore:** one pull request adds a schema that JetBrains IDEs, Visual Studio, Neovim, Emacs and Sublime Text pick up for matching file names. VS Code reads the catalog for JSON natively; for YAML it needs the Red Hat YAML extension, which reads SchemaStore by default, and for TOML a TOML extension.

## Rich extensions and their cost

- **AWS Toolkit** and **Google Cloud Code:** resource explorers, debugging, local emulation, millions of installs, and ratings well below what those installs suggest. Breadth without upkeep shows in the reviews.
- VS Code's own guidance on webviews: resource-heavy, separate context, high memory when retained, must be themed and sanitized; use them only when native UI cannot do the job.

## Deprecations

- **Azure Account (Microsoft):** deprecated January 2025 once VS Code's built-in Microsoft authentication provider did its job. Public issue with a deadline for dependent extensions, an npm package to ease migration, named reference migrations, the Marketplace deprecated flag, then the repository archived about five months later.
- **Docker:** the original extension became an extension pack; a renamed "Container Tools" extension replaced it with broader runtime support, so the old ID kept working for its tens of millions of installs.
- **GitHub Copilot Extensions (GitHub Apps):** a server-side integration type, not an editor extension, retired in favour of MCP servers. New creation blocked, brownouts in the final week, then shutdown on a published date. Copy the ladder: freeze, brownout, off, with a named replacement.
- Pattern across all three: the host or a standard protocol absorbed the job, and the vendor said so with a date and a replacement.
