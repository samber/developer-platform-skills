# Stack Overflow Q&A, tag excerpt and wiki for the `larkq` handshake error

**Read this first.** Stack Overflow bans any post "crafted, in part or in whole" by an LLM. The penalty is deletion with the reputation lost, then suspension on repeat. I'm an LLM, so I can't write the technical body for you to post.

Below, everything you told me is filled in verbatim. Every other technical claim is a `<slot>` for you or engineering to write in your own words. That is also why I can't promise engineering won't need to touch it. Slots 3 to 5 need their input.

I assumed your account is your own and personal, you're the only poster, and the posture is **Curate**: about 30 tickets a month is a strong signal for a canonical. Correct me if any of that is wrong.

## 1. Self-answered canonical

Tick "Answer your own question" on the Ask page. It needs 15 rep and you have 230. Post the question and the answer together.

**Question**

Title (the literal error string, which is what searchers type):

```
larkq-go 2.x fails on startup with "larkq: handshake rejected: protocol version 4 not supported by broker (max 3)"
```

Body:

```
I upgraded larkq-go to <2.x version you saw> and my consumer now crashes on startup against our Larkmoor broker <older version>, with:

    larkq: handshake rejected: protocol version 4 not supported by broker (max 3)

Expected: the consumer connects as it did on 1.x.
What I tried: <one or two things that don't work, e.g. restarting the consumer, re-running go mod tidy>.

Disclosure: I work at Larkmoor, which maintains Larkmoor and larkq-go; I'm posting this Q&A to document a common fix.
```

Tags: `larkq`, `go`. Add `message-queue` only if it fits the tag's usage.

**Answer** (write it from this outline)

```
Cause: <1 sentence: larkq-go 2.x negotiates protocol 4; brokers older than 1.14 accept at most protocol 3, so the handshake is refused.>

Fix: pin the protocol in the client until the broker is upgraded.

    <your real, compiling snippet, with the actual constructor and import path,
     passing larkq.WithProtocol(3)>

Verify: <command or log line that shows a successful connect, and the protocol it negotiated>.

Applies to larkq-go <first 2.x version> and later against brokers older than 1.14.
Proper fix: upgrade the broker to 1.14 or later, then remove WithProtocol(3). <upgrade doc link>

Disclosure: I work at Larkmoor, which maintains larkq-go.
```

### Slots engineering must supply

1. **The exact first larkq-go version** that negotiates protocol 4. This sets the "applies to" range.
2. **A tested snippet.** I can't invent the constructor or import path.
3. **How to read the broker version.** An operator needs to know whether they're on 1.14 or later.
4. **Side effects of protocol 3.** Say whether any 2.x features are disabled, and whether `WithProtocol(3)` is safe in production.
5. **Upgrade order.** State whether to upgrade broker first or SDK first, and whether removing the option later is safe.
6. **Whether `WithProtocol` exists in every 2.x release.** If it doesn't, say what to do instead.

Slots 3 to 5 are what make the answer complete, and your ticket history likely already holds them.

### After posting

- Mirror the answer on your docs error page, using `developer-troubleshooting-docs`. Link the canonical from your support macro for this ticket.
- Flag future repeats as duplicates of the canonical. You can flag at 15 rep, but a duplicate close vote needs 3,000 rep.
- Do not ask colleagues to upvote, accept or bounty it. Coordinated votes are reversed and can suspend every account involved.
- Check wording against the real question text in 30 days. Titles that quote the error string rank best, but that is unconfirmed practitioner evidence.

## 2. Tag excerpt (replace the marketing line)

The current text breaks the excerpt's purpose: it's usage guidance shown in the tag picker, not an ad. Superlatives and "Get started free" invite a rollback.

```
Larkmoor is an open-source message queue. Use for questions about using Larkmoor's larkq-go SDK and broker. For bugs, feature requests or account issues, use Larkmoor's own channels.
```

Edits at 230 rep go to peer review. Check that "open-source message queue" is accurate and neutral before submitting.

## 3. Tag wiki

```
## About
Larkmoor is an open-source message queue. This tag covers the larkq-go SDK, currently <2.x>, and the broker, currently <version>.

## Before asking
Include the Larkmoor broker version, larkq-go version, Go version and the full error output. Common problems: <link to the handshake canonical>, <other canonical links as you write them>.

## Where else to ask
Bugs: <issue URL>. Feature requests: <URL>. Account and billing: <support URL>.
```

Submit it as one batched edit. Each edit bumps the thread to the Active tab.

## 4. Reusing the broker TLS answer on your docs site

**Yes, but not as a plain copy-paste.** Stack Overflow content is licensed CC BY-SA 4.0, so reuse is allowed with conditions:

- **Attribute.** Name the author, link to the original post, and name the license with a link.
- **Check the license version.** Posts from before 2018-05-02 are CC BY-SA 3.0. Look at the post date and cite the right version.
- **Share-alike.** If you adapt the text, the adapted passage must stay under the same license. Mark it as a separate licensed quote on the page, not blended into your own docs text. Ask your legal contact whether the rest of the docs license is affected.
- **Verify it first.** Test the answer against your current broker, since it's older.
- **Don't edit the original** to fit your docs. Rewrites of others' answers get rolled back. If it's outdated, post a new answer with a disclosure line.
- **Optional courtesy.** Comment to tell the author you're reusing it.

If you want your own wording rather than a licensed quote, write it yourself from the docs and link to the thread.

## 5. Order of work, about 3 hours total

| # | Action | Owner | Time | Rep gate |
| --- | --- | --- | --- | --- |
| 1 | Fill slots 1 to 6 | Engineering | 30 min | n/a |
| 2 | Post the canonical Q&A | You | 45 min | 15 |
| 3 | Submit the excerpt and wiki edits | You | 30 min | any, peer-reviewed |
| 4 | Mirror on the docs page, update the support macro | Docs/support | 45 min | n/a |
| 5 | Add the TLS answer to the docs with attribution | Docs | 30 min | n/a |

**Metrics to track.** Views on the canonical, how many of the roughly 30 monthly tickets drop after the macro change, and hygiene counts. Spam flags, AI deletions and rejected edits should all be zero.