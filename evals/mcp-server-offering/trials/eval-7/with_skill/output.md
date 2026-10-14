# MCP server decision for Ferrolane: size and sequence

I read the `mcp-server-offering` skill and its three references. The skill normally asks clarifying questions first. I can't get answers here, so I've listed them with the assumption I used and what would change my answer.

## Short answer

- **Size:** this is two decisions. The smaller one is "ship an MCP server." The larger one is "ship Ferrolane's first machine-readable interface," which reverses the deliberate no-integrations stance.
- **Why it matters:** you have no public API, so there is no stable contract to derive tools from. The skill's usual advice assumes one exists. Your effort sits in the backend and auth work under the server, not in the MCP layer.
- **January:** a read-only, OAuth-protected server is plausible but not guaranteed. Writes by January are not realistic and not safe.
- **Evidence:** two competitors announcing MCP servers is not demand evidence. Get demand evidence before you commit past stage 1.

## 1. Size of the decision

**What the evidence supports**
- For most B2B SaaS, an MCP server is defensive positioning that is becoming a procurement checkbox. The competitive question is now "supports MCP well," not "supports MCP."
- Forrester predicts 30% of enterprise app vendors will launch their own MCP servers. Stacklok's December 2025 survey of 300 technical leaders puts about 41% of software organizations in limited-to-broad MCP production. These are the citable baselines.
- Don't use the "78% of enterprises" or "28% of Fortune 500" figures in internal slides. They are debunked, and one bad number discredits the whole case.

**What is different for you**
- Roughly half of companies shipping MCP servers had no public REST API. That is a directional single-source analysis (Bloomberry), not an industry fact.
- For those vendors, MCP is the first machine-readable interface they ever shipped, which makes it a possible new acquisition channel and not only a defensive copy.
- It also means the work below the server is new for you: a tenant-scoped service layer, token validation, and audit.

**Cost, as orders of magnitude**
- A demo server takes a weekend. A production server takes months plus a standing maintenance commitment.
- The 150-250 hour figure is for a simple hand-built server over an existing API. It is an analyst estimate, not audited. Treat it as a floor for you, because you have no API underneath.
- Maintenance is ongoing. The protocol shipped four backward-incompatible revisions in its first twenty months, and tool descriptions are an interface you have to version.

**Risks specific to compliance-document review (my inference, not from the skill)**
- Customers' construction compliance documents would flow into third-party assistants. Their security teams will ask where that data goes.
- Review decisions such as approve or flag carry liability. That makes write tools high-stakes for you, not just convenient.
- You can ship a read-only server with no document upload and no write tools. That keeps most of this risk out of the first release.

## 2. Order of work

Timeline assumes today is 2026-10-09, about 12 weeks to January. The week ranges are my estimates, not from the skill.

### Step 0: Weeks 1-2, find out whether anyone is asking
1. Ask sales for MCP in actual RFPs and security questionnaires. Ask support for customers who requested agent access.
2. Read the two competitors' servers. Are they read-only or do they write? How many tools? Do they use OAuth?
3. Check whether a community-built Ferrolane server already exists. If so, a first-party server also displaces it.
4. Interview two or three customers you'd want as design partners. Ask whether their security teams would allow Ferrolane data in an AI assistant.
5. **Decision rule:** if MCP is a hard requirement in real RFPs, accelerate. If there is no RFP pressure and no customer pull, build only stage 1 and park it as maintained table stakes.

### Step 1: Weeks 1-3, settle the foundation
1. Does the web app already talk to a backend API you could expose, or is it tightly coupled? This decides whether the backend work takes weeks or months.
2. Do you run an OAuth 2.1 authorization server? If not, MCP would be your first OAuth consumer. That is the likeliest thing to break January.
3. The MCP server must be an OAuth 2.1 resource server. It validates tokens and never mints them.
4. It must never forward the caller's bearer token to your backend. Get your own upstream token by token exchange.
5. Design tenant isolation first. Every tool call must resolve to exactly one customer's data.
6. Get leadership to accept that this creates a supported integration surface. Name an owner.

### Step 2: Weeks 3-5, design the tool surface
- Design 5-15 workflow-level tools from customer jobs, not from web-app screens or endpoints. Five to eight read-only tools is a reasonable first target.
- Use verb-first, prefixed snake_case names, for example `ferrolane_list_reviews`.
- Candidate jobs, to validate in your design-partner interviews: list projects and reviews, get a review's status, get findings for a document, search findings across a project, and summarize outstanding compliance gaps.
- Spend real time on tool descriptions. Description tuning is the highest-leverage design lever the skill cites. Test with golden prompts.
- Give every tool exactly one risk tier. Annotations like read-only are hints for clients, not security controls.

### Step 3: Weeks 4-10, build stage 1 (read-only)
- **Hosting:** use a remote managed platform. It absorbs protocol churn and the OAuth machinery, and it fits a deadline. Self-hosting only makes sense if the server becomes your product or you need a custom policy layer in your own infrastructure.
- **Auth:** publish protected-resource metadata (RFC 9728). Require resource indicators (RFC 8707) and reject tokens not issued for this server. Validate the issuer (RFC 9207).
- **Statelessness:** design for a stateless server, so any instance can serve any request.
- **Hardening:** schema-validate and bound every input, and never leak internal errors.
- **Telemetry:** instrument OpenTelemetry from the first call. Track call volume, error rate, per-tool usage, active users, and client mix.
- **Test lockdown:** if you add a read-only switch, verify that write tools are actually absent. A documented GitHub bug shipped write tools despite the flag.

### Step 4: Weeks 10-12, beta, then January launch
- Run a closed beta with the design partners. Verify the security review passes.
- Publish to the official MCP registry under a DNS-verified namespace, then to third-party directories. Registry listing certifies nothing about security, so don't present it as a trust claim.
- Let sales say "MCP in early access, read-only." Don't promise write actions or broad host support.

### Stage 2 (after January): writes
Move on only after stage 1 shows sustained tool-call volume from real agent clients, not demo spikes, with a tool-error rate under 2%. Treat that 2% as a default to recalibrate against your own first month. It is one vendor's practice, not a standard.

When you do add writes, apply these patterns:
- **Server-side risk tiers:** enforce them server-side so users can't bypass them by switching clients.
- **Approval:** require human approval on contained writes. Keep critical or irreversible tools disabled by default.
- **Credentials:** use scoped credentials.
- **Attribution and audit:** attribute every write to the agent and user, and log it for audit.
- **Idempotency and dry-run:** use idempotency keys, and dry-run where feasible.
- **Undo:** assume there is no reliable undo. The ecosystem substitutes audit trails for rollback.

An approve-or-flag decision on a compliance document is critical-tier for you. Keep it disabled or approval-gated for a long time.

### Stage 3 (later, optional): MCP Apps UI
Consider an interactive review UI only after two or three design partners confirm their security teams accept iframe-rendered third-party UI in their assistant. That is still an open question across the ecosystem. Your review workflow (stepping through findings) would fit the "queue item by item" use case, but don't build it for January.

## 3. What to tell the head of sales

- ✅ A read-only MCP server in early access by January is a real target, contingent on step 1's auth answer.
- ⚠️ Competitors announcing servers is not proof of buyer demand. Ask for actual RFP language first.
- ⚠️ A server with write actions, such as approve or flag, by January would be reckless. It would also carry your first real security review.
- ℹ️ It becomes a standing maintenance commitment. Someone owns it after launch.
- ℹ️ If two full quarters pass with flat usage and no RFP demand, park it at stage 1 and defer the bigger build.

## 4. Questions that would change this answer

1. Does the web app have a clean backend API you could expose, or not? A clean one takes weeks off step 3. If not, January slips.
2. Do you already run an OAuth 2.1 authorization server? If not, add its design to the critical path.
3. Are there real RFP or customer requests for MCP? If yes, accelerate. If not, build only stage 1.
4. Which write actions do customers genuinely need, and which are irreversible or consequential? Approve/flag decisions would be the first to gate.
5. Is January a procurement deadline or a competitive-optics date? A hard procurement deadline strengthens the case for managed hosting and a read-only launch.
6. What is your engineering ceiling in hours, and who maintains it afterwards?

I didn't verify competitor server details or any current spec revisions. The skill is written against the 2026-07-28 MCP spec revision, so re-check the latest one before building.