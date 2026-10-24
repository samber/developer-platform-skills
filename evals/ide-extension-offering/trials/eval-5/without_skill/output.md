# Larkspur: telemetry, bank proxy, exec number

**Do first (10 min):** pull the next release now. Remove `workspace folder path` and `git user email` from the event payload. Gate sending on `vscode.env.isTelemetryEnabled`. Everything below follows from these two changes.

I did not see your code, and I did not read anything under `skill-wip/`. The VS Code behavior below is from memory. Verify each point on your minimum supported VS Code version.

---

## 0. Plan, ranked

1. Telemetry fix and release. About 1 day of code plus review. Ships first.
2. Data purge and legal check. Start in parallel, owned by legal or your DPO.
3. Public reply to the customer. Send after step 1 ships, not before.
4. Bank pack: network doc, diagnostics command, offline VSIX. About 3 to 5 days.
5. Fix the exec slide. 30 min. Do this before next week.

---

## 1. Telemetry: the customer is right

**Verdict:** "phones home with telemetry off" is accurate. VS Code has a global setting, `telemetry.telemetryLevel`. Extensions must honor it. A plain `fetch` ignores it. Your own `larkspur.telemetry.enabled` is a second switch and does not replace the global one. A user who set VS Code telemetry to `off` still gets your events.

**Worse than the bypass:** you send the workspace path and the git email.
- The email is personal data under GDPR. It is not needed to dedupe.
- Paths often contain the OS username, the client name, and the repo name. At a bank, that is confidential.
- Non-essential analytics on personal data needs consent in the EU. Default-on in your own setting is not consent.
- Marketplace policy also expects extensions to respect the telemetry setting. Check the current publisher terms.

### Code fix (TypeScript)

Use `vscode.env.createTelemetryLogger`. It honors the global setting, and it re-checks the setting live. Your own setting stays as an extra opt-out.

```ts
import * as vscode from 'vscode';

// Same endpoint as today. Move it to config; never hardcode.
const ANALYTICS_ENDPOINT = process.env.LARKSPUR_ANALYTICS_URL ?? 'https://<your-analytics-host>/v1/events';
// Abort slow sends so a blocked proxy never stalls the extension host.
const SEND_TIMEOUT_MS = 5_000;
const OWN_SETTING_SECTION = 'larkspur';
const OWN_SETTING_KEY = 'telemetry.enabled';

// Payload allowlist. Anything not listed is dropped before sending.
const ALLOWED_KEYS = new Set(['event', 'extVersion', 'vscodeVersion', 'os', 'durationMs']);

const sender: vscode.TelemetrySender = {
  async sendEventData(eventName, data) {
    const own = vscode.workspace
      .getConfiguration(OWN_SETTING_SECTION)
      .get<boolean>(OWN_SETTING_KEY, true);
    if (!own) { return; }
    const body: Record<string, unknown> = { event: eventName };
    for (const [k, v] of Object.entries(data ?? {})) {
      if (ALLOWED_KEYS.has(k)) { body[k] = v; }
    }
    try {
      const res = await fetch(ANALYTICS_ENDPOINT, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(SEND_TIMEOUT_MS),
      });
      if (!res.ok) { console.warn(`larkspur telemetry: HTTP ${res.status}`); }
    } catch (err) {
      console.warn('larkspur telemetry send failed', err); // never throw into the host
    }
  },
  sendErrorData() { /* no error telemetry */ },
};

export const telemetry = vscode.env.createTelemetryLogger(sender);
```

Rules:
- Call `telemetry.logUsage(...)` only. Never call `fetch` for analytics anywhere else. Grep the repo for other `fetch(` calls that carry data.
- Dedupe by the machine-level ID that VS Code already adds to events (`common.machineid`, a hashed value). Do not collect an email, a path, or a hash of either.
- The logger already attaches VS Code's common properties. Review what lands on your server and drop the rest.
- Ship a test. With `isTelemetryEnabled` false, assert zero network calls. With it true, assert the payload has only allowlisted keys. Break the gate on purpose once, and confirm the test fails.
- Keep `larkspur.telemetry.enabled`. Document it as "Larkspur events are sent only if both VS Code telemetry and this setting are on."

**Metric consequence:** you lose "unique people". You get "unique active installations". That is fine, and you must say it that way (section 3).

### Data cleanup (legal or DPO leads)

1. List every system that holds the old events: analytics vendor, warehouse, backups, BI exports.
2. Delete or null the path and email fields. Confirm in writing with the vendor.
3. Ask counsel two questions: do you need to notify anyone, and what must you tell customers? Do not decide this in engineering.
4. Check bank contracts and the DPA. The bank's developers' emails and repo paths went to you. Tell the bank before they find out.
5. Update the privacy policy and the README telemetry section with the exact fields sent.

### Public reply (draft, normal prose)

> You're right, and thank you for flagging it. Larkspur's usage events did not follow VS Code's global telemetry setting; they followed only our own setting, which defaults to on. They also included the workspace folder path and the git email, which we should not have collected. In version X.Y.Z we now honor `telemetry.telemetryLevel`, we send no path or email, and we publish the exact fields in the README. We are deleting the previously collected path and email data. If you were affected and want details, write to <address>.

Send it only after X.Y.Z is live. Do not claim deletion before the vendor confirms it. Do not argue that the setting was "documented".

---

## 2. Bank: proxy, internal CA, allowlist, private marketplace

### Likely cause of the connection failure

Your `fetch` runs in the extension host. Depending on VS Code, Electron, and Node version, global `fetch` may not use VS Code's proxy settings or the OS certificate store. The bank has a TLS-inspecting proxy with an internal CA. Typical failure is `SELF_SIGNED_CERT_IN_CHAIN` or `UNABLE_TO_VERIFY_LEAF_SIGNATURE`. **I have not reproduced this.** Test it:

1. Set up a local proxy that re-signs TLS with a private CA (mitmproxy works).
2. Trust that CA in the OS store only. Set `http.proxy` in VS Code.
3. Run the extension. Reproduce the error.
4. Try the same call through Node's `https` module, which VS Code patches. Check whether it succeeds.

### Fix

- Route Larkspur traffic through the path VS Code patches. If `fetch` fails but `https` works in step 4, switch to `https`, or to a client built on it.
- Honor `http.proxy`, `http.proxyStrictSSL`, `http.proxyAuthorization`, and `http.systemCertificates`. Do not add your own CA bundle setting unless step 4 proves it is needed.
- Never disable TLS verification as the fix. A bank will reject it, and rightly.
- Add a command **Larkspur: Show Connection Diagnostics**. It prints:
  - target host and port
  - resolved proxy (or none)
  - the exact TLS or network error code
  - VS Code and extension version
  - It must send nothing to us. The user pastes the output into a ticket.
- Make failures visible in the UI with the error code. A silent empty trace panel makes IT blame the proxy.
- Split the hosts. Functional traffic (traces) uses one hostname. Telemetry uses a different hostname. The bank can then block telemetry and keep the product working.

### "Something to allowlist"

Publish a versioned page, `docs/network-requirements`, plus a PDF copy. Fill this table. I do not know your hosts, so these are placeholders.

| Host | Port | Protocol | Purpose | Data sent | Required? |
|---|---|---|---|---|---|
| `<traces-api-host>` | 443 | HTTPS | Fetch trace data for inline display | Trace queries, auth token | Yes |
| `<telemetry-host>` | 443 | HTTPS | Usage events | Allowlisted fields only | No; off via policy |

Also state:
- No wildcard domains. No fixed IP promise unless you truly guarantee one.
- TLS 1.2+ and which endpoints need client certs, if any.
- That the extension makes no other outbound calls. Prove it: capture traffic on a clean install and list every host.
- Change policy: new hosts only in a minor release, announced in the changelog.
- Admin kill switch: VS Code group policy can set `telemetry.telemetryLevel` to `off` fleet-wide. Document it. With step 1 fixed, that also silences Larkspur.

### Private marketplace

1. Publish a signed `.vsix` per release on your site or a customer portal, with SHA-256 checksums.
2. State that the extension needs no marketplace access at runtime. Verify it. Remove any update check or remote code load.
3. Ship an SBOM and a short security note: network calls, data sent, no remote code.
4. Pin `engines.vscode` to the minimum supported version, and give the bank that version.
5. Be aware these installs bypass the public count. They also may block your telemetry. Neither the bank's 2,000 developers nor their usage is reflected in your numbers.

Next action for the bank: send them the fixed build and the diagnostics command after step 1 and the proxy test pass. Ask IT to run the diagnostics and paste the output.

---

## 3. Exec slide: "41k active developers" is wrong

- **41,000 installs** is a cumulative marketplace count. It includes people who uninstalled, installed on several machines, or never opened it.
- Installs are not people. "Developers" implies unique humans. You have no verified human count, and after the fix you will not collect one.
- Active needs a definition and a window, for example "installations with at least one trace viewed in the last 28 days".
- The measurement undercounts: opted-out users, bank installs, anyone blocking your endpoint.
- Execs will repeat this number. If a customer or journalist checks, it breaks, and it lands next to the Mastodon thread.

Slide wording that survives scrutiny:

> **41,000 installs** (VS Code Marketplace, cumulative, as of 2026-10-24). Active usage: <N> active installations in the last 28 days, measured from opted-in telemetry. This undercounts: opt-outs and private-marketplace installs such as enterprise deployments are not included.

Get N after the fix ships. Until then, present installs only, or present the old number labeled "estimate, old method, includes data we are removing". Prefer the first.

Also tell the execs about the telemetry issue before the meeting. They should hear it from you, with the fix date.

---

## Status and next action

Step 1 of 5 not started. Open the telemetry module and grep for every `fetch(` call. Paste the list here and I will check each against the allowlist.