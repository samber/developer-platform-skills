**Bottom line:** the full wish list is about 210-250 hours, or 7-8 quarters of Lena. This quarter's 30 hours ship Node and Python everywhere, Java and Go for the quickstart only, and nothing for tier 2.

The PM's doc can't be met. Here are the mismatches I found:

1. **"Every sample, every language" against 30 hours.** The matrix is 9 languages × 6 scenarios = 54 distinct samples, about 100 hours. Send-SMS doubles as the quickstart. The four apps add 106-146 hours on top.
2. **Tiers against traffic.** Kotlin is tier 1 but sits under 2% of traffic. I ranked by traffic, not tier. See question 1 below.
3. **The sandbox can't simulate inbound voice.** That affects the voice-callback sample and the contact center app. Neither can be verified end to end in the sandbox.

## Ships this quarter (30 hours)

| Item | Languages | Hours |
|---|---|---|
| Quickstart (send SMS) | Node, Python, Java, Go | 7 |
| verify-OTP | Node, Python | 2.5 |
| Webhooks, with signature check and fixture tests | Node, Python | 3 |
| Number lookup | Node, Python | 2 |
| Conversations | Node, Python | 4 |
| Inbound voice callback | Node only | 4 |
| **Committed** | | **22.5** |
| Vercel deploy template (Next.js, reuses the Node samples) | Node/TypeScript | 6 |
| **Total if nothing overruns** | | **28.5** |

- **Buffer:** 7.5 hours (25%), which is thin for one person. Solo work and a product only six weeks old usually overrun, so build the committed rows first. The Vercel template takes whatever buffer is left. If the buffer runs out, drop the template, not the buffer.
- **Languages:** Node plus Python cover 79% of traffic. Adding Java and Go for the quickstart brings it to 95%. Java and Go scenario samples wait for next quarter.
- **Conversations:** it is in the plan despite being new. Pin the SDK version, because the API may still change.
- **Voice callback:** unit-test the handler against fixture payloads. Then run it once against a real number and tunnel. Put "last verified on <date>" in the README. This needs a voice-capable number outside the sandbox.
- **Vercel template:** it gets a head start from the Node samples and reaches the 48% Node audience. It also covers most of what the playground would do, for a fraction of the cost.
- **What each sample includes:** sandbox verification, a README, and a CI smoke test. Docs-site integration is not included.

## Not this quarter

| Item | Estimate | Verdict |
|---|---|---|
| Java and Go scenario samples, plus Python voice | 14-16 h | Next quarter. Port from the Node originals. |
| Contact center app | 40-60 h | Don't build it as scoped. It needs voice, which the sandbox can't test, and it spans three products, one of them new. A thin Node-only version could fit in Q+2 or Q+3 (~25 h). |
| Android sample app | 30-40 h | Q+3 at the earliest. Kotlin traffic is under 2%. A secret key can't ship in an app, so it also needs a small backend, which adds scope. |
| Browser playground | 30-40 h, plus hosting | Defer. It needs a key proxy, abuse limits and ongoing upkeep. The Vercel template is the cheap substitute. |
| Tier 2 (Ruby, PHP, .NET, Swift) | 28 samples, ~56 h | Never promise the full matrix. Offer a quickstart only, or accept community contributions. |

A cheap fix for the second-class concern is a curl or raw-HTTP snippet per scenario for languages without a sample, at about 0.5 hour each. It is not in this quarter's budget. A public coverage matrix would also set expectations honestly.

## Assumptions

- Lena is fluent in Node and Python, and moderately fluent in Java and Go.
- Hours are for Lena alone, with no AI assist counted.
- I know nothing of your API surface beyond what you wrote.

## Questions for you

1. Does tier 1 mean "gets samples", or only "gets a maintained SDK"? If samples, Kotlin has no home outside the Android app.
2. Do you have a voice-capable number on a non-sandbox account, and a budget for test traffic?
3. Does the Android SDK call the API with a client token, or does it need your backend?

**Next:** answer question 2. Without a real number, the voice sample moves out of this quarter and frees 4 hours.