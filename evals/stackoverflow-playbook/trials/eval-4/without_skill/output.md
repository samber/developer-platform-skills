# Stack Overflow package for the `larkq: handshake rejected` error

Three things need your attention before you post:

1. **Disclose your affiliation in the answer.** Stack Overflow requires it. The text is already in the answer below.
2. **The Go snippet uses a placeholder constructor.** I don't have the larkq-go API, so I wrote `larkq.Dial(...)`. Swap in the real call. Everything else comes from your description.
3. **You can't edit the tag wiki directly at 230 rep.** As I understand the current rules, direct tag-wiki edits need much more reputation. You can submit the excerpt and wiki as a suggested edit, and reviewers will approve it. The existing excerpt is a sales pitch, so expect scrutiny and keep the replacement neutral.

---

## 1. Question

**Title:**
`larkq: handshake rejected: protocol version 4 not supported by broker (max 3) after upgrading larkq-go to 2.x`

**Tags:** `go` `larkq` `message-queue`

**Body:**

I upgraded the Go SDK `larkq-go` from 1.x to 2.x. Now my consumers crash immediately on startup with:

```
larkq: handshake rejected: protocol version 4 not supported by broker (max 3)
```

Nothing else changed. The consumer code is the same, and it worked before the upgrade. The broker is an older Larkmoor release that I haven't upgraded.

- Why does the handshake fail?
- How do I get the consumers running again without upgrading the broker right now?

---

## 2. Answer

*Disclosure: I work for Larkmoor, the company behind larkq and larkq-go.*

### Cause

`larkq-go` 2.x speaks wire protocol version 4 by default. Brokers older than 1.14 only support protocol versions up to 3. During the handshake, the SDK offers version 4. The broker rejects it and reports its own maximum, so you get `(max 3)` in the message. The SDK does not fall back automatically, so the consumer exits at startup.

The failure is not in your code, your credentials or your network. It is a version mismatch between SDK and broker.

### Fix: pin the SDK to protocol 3

Pass `larkq.WithProtocol(3)` when you create the client:

```go
client, err := larkq.Dial(
    addr,
    // Keep your existing options, and add this one:
    larkq.WithProtocol(3), // broker < 1.14 supports protocol 3 at most
)
if err != nil {
    return fmt.Errorf("connect to larkq: %w", err)
}
```

Apply this to every client that connects to the old broker, producers included. A producer on the 2.x default fails the same way when it connects.

### Permanent fix: upgrade the broker

1. Upgrade the broker to **1.14 or later**.
2. Remove `larkq.WithProtocol(3)` so the SDK negotiates protocol 4.
3. Redeploy the consumers.

Upgrade the broker before you remove the option. If you remove it first, the original error returns.

### Verifying

- **Fixed:** the consumer starts and the handshake error is gone.
- **Still failing, with a different max:** the message reports the broker's real limit. If it says `(max 2)` or lower, the broker is older than this answer assumes. Pin to that number instead of 3 if the SDK supports it, or upgrade the broker.
- **Still failing, with `(max 3)`:** some client is still on the default. Check every service, cron job and test fixture that connects to this broker.

### Notes

- Pinning is a stopgap. While pinned, you don't get features that require protocol 4. Check the larkq-go 2.x release notes for what that covers.
- Don't pin the SDK back to 1.x as the fix. It works, but it leaves you on an old SDK, and the same mismatch returns at the next upgrade.

---

## 3. Tag excerpt (replacement)

```
Larkmoor is an open-source message queue. Use this tag for questions about the larkq broker and its client SDKs, such as larkq-go. Include the broker and SDK versions in your question.
```

## 4. Tag wiki (replacement)

```
Larkmoor ("larkq") is an open-source message queue. The project consists of a broker and client SDKs, including the Go SDK, larkq-go.

## Use this tag for

- Questions about running, configuring or troubleshooting the larkq broker.
- Questions about using the larkq client SDKs, for example larkq-go.

Combine it with a language tag such as [go] when the question is about an SDK.

## Include in your question

- Broker version and SDK version. Many problems come from a mismatch between the two.
- The exact error message, copied as text.
- A minimal code snippet or configuration.

## Common problem: protocol version mismatch

Upgrading larkq-go to 2.x against a broker older than 1.14 fails at startup with `larkq: handshake rejected: protocol version 4 not supported by broker (max 3)`. See the canonical answer: [link to your Q&A].

## Links

- Documentation: [docs URL]
- Source: [repository URL]
- Go SDK: [larkq-go repository URL]
```

Fill in the three URLs and the Q&A link after you post. Remove any placeholder that doesn't apply.

---

## 5. Can you copy the TLS answer into your docs site?

**Not by simply copying it.** You can reuse it, but only if you meet the licence terms. Stack Overflow content is licensed under Creative Commons BY-SA. The version depends on when the answer was posted: 2.5, 3.0 or 4.0. Check the answer's date and the licence shown on it.

**Attribution (BY)**

- Name the author, link to the original answer and link to the licence.
- State any changes you made.

**ShareAlike (SA)**

- Anything derived from the answer must be published under the same or a compatible CC BY-SA licence.
- If your docs are under a different licence, the copied section is under CC BY-SA, not yours. Put a clear notice on that page.
- Check this with your legal team before you copy anything. It is the main risk.

**Safer options, in order of preference**

1. **Ask the author.** Message them and ask for permission to reuse the answer under your docs licence, or whether they'd like to write it for you. Get this in writing. Their agreement is separate from the Stack Overflow licence.
2. **Write your own TLS setup guide.** Use the answer as a source for what to cover, not for wording. Engineering should verify the steps against current broker versions anyway. An old answer may be out of date.
3. **Link to the answer** from your docs and leave it on Stack Overflow.

Do not strip the author's name or present the text as Larkmoor's own. That breaks the licence and the community's trust, and it is the kind of thing that gets noticed.

---

## Not covered

- **I can't verify the technical claims.** The cause, the 1.14 boundary and `WithProtocol(3)` come from your description. If engineering wants to check anything, it should be the "what you lose on protocol 3" note and the `(max 2)` guidance.
- **Self-answering is allowed, but it needs the right setup.** Post the question with "Answer your own question" ticked, and post the answer right away.