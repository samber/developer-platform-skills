# Board slide: Pellham MCP server

**Don't use the opener or the proof point as drafted.** The skill's evidence rules rule out both claims.

| Your draft | Why it fails | Source |
|---|---|---|
| "Over 31,000 organizations run agents against Pellham" | 31,400 is npm downloads. Downloads count installs, not organizations. They include CI re-installs and private mirrors, and they can't be read as execution counts. Only in-server telemetry measures usage. | Step 7 and the do-not-cite list |
| Registry listing as the security proof | The official registry is a metadata catalog with DNS namespace-ownership proof and community moderation. It "certifies nothing about security." | Step 6 |
| #4 rank as proof of trust | Rank on directories measures discovery and popularity, not security. A security-minded board member will see this. | Step 6 |

If someone on the board asks "how many orgs?" and the answer is "downloads," the whole deck loses credibility. The gateway gap makes this more urgent, because you can't back the number with logs.

## Slide (draft)

**Title:** Pellham is now a discoverable, agent-ready surface, and we're measuring real usage

**Left column: Reach (install interest)**
- 31,400 npm downloads *(install interest, not active usage)*
- Listed on the official MCP registry (DNS-verified namespace)
- #4 in category on two MCP directories

**Middle column: Active usage (in-server telemetry, last 30 days)**
- [N] distinct authenticated orgs (OAuth client or tenant ID)
- [N] tool calls per week, [x]% error rate
- Top 3 customers: usage seen only partially, because they front us with their own AI gateway. We are correlating gateway logs with our request IDs.

**Right column: Security posture (what we enforce, not where we're listed)**
Include only the items you can verify today:
- OAuth 2.1 resource server, with protected-resource metadata (RFC 9728)
- Token audience validated per server (RFC 8707). Bearer tokens are never forwarded upstream.
- Scoped credentials and a tested read-only mode
- Writes gated server-side, with attribution and audit logs
- [Pen test or SOC 2 scope, if it covers the MCP endpoint]

**Footer (small):** Registry listing = namespace verification, not a security certification. Downloads = install interest, not usage.

## Speaker notes

1. Open with the real number: "[N] organizations authenticated against our server last month." If you can't get N by Friday, open with "31,400 installs. Here's how we're converting that into measured usage." That is honest, and it's still a good story.
2. Present the registry and directory rank as discoverability. Then say: "Security is what we enforce, and here's the list." Security-conscious members will trust you more for drawing that line yourself.
3. Gateway gap: "Our three largest customers route through their own gateways, so our logs are partial. Our count is a floor, not a ceiling. We've made our tool names and request IDs correlatable and asked them for gateway-side counts."
4. Don't extrapolate. Don't multiply their traffic into an estimated org count on the slide.

## To do before Friday

1. **Pull N.** Count distinct OAuth client or tenant IDs with at least one successful tool call in 30 days, from your own server logs. Label it "orgs seen (lower bound)."
2. **Ask the three gateway customers** for their gateway-side call counts or a confirmation of active use. Your CSM can send a one-line email. Add their numbers only with their consent.
3. **Verify each security bullet** against the actual server: audience validation, no token passthrough, a tested read-only lockdown (a vendor shipped writes despite the flag), and server-side enforcement. Delete any bullet you can't confirm.
4. **Check the stage.** If tool-error rate is under 2% and volume is sustained from real agent clients, say you're at Stage 1 (read-only launch). Don't imply write-safety maturity you haven't shipped.
5. **Optional backup slide:** one line from Stacklok's Dec 2025 survey (n=300), where about 41% of software organizations are in limited-to-broad MCP production. It is the citable market baseline. Don't use the "78% of enterprises" figure.

## Open questions

- Do you have per-org telemetry today (OAuth client IDs in logs)? If not, the opener above has to change.
- Is the server remote with OAuth, or local stdio? That decides which security bullets are true.
- Has MCP appeared in any RFP or security questionnaire? If so, that is a stronger proof point than rank, and the skill says to cite it qualitatively.