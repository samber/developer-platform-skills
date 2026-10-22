# Call: conditional GO. Ship date holds if the reliability section is fixed first.

I judged this from your description alone. I haven't seen the page or run anything.

Four of your five parts look ship-ready. The fifth is the gap: "We retry failed deliveries with exponential backoff" is not a reliability policy.

## Why the one sentence blocks

The sentence leaves out everything a consumer needs to build a correct receiver:

- Which responses count as failure: any non-2xx, timeouts, or connection errors.
- How many attempts there are, the backoff schedule, and the total retry window.
- Your per-request timeout.
- Whether delivery is at-least-once, which means duplicates.
- Whether ordering is guaranteed. With retries it almost certainly isn't.
- What happens after retries run out: dropped, dead-lettered, or the endpoint disabled.
- How to recover missed events: manual redelivery, replay API, or a dashboard button.

Your troubleshooting and failure-recovery page also has nothing solid to stand on if the policy isn't written down. Either it contradicts the one-liner, or it documents recovery for behavior the main page never promises. Receivers who guess wrong lose events silently, and that is the failure you will get support tickets for.

## Fix before ship

Target: done by Oct 15, which leaves 4 days of buffer.

1. **Replace the sentence with a "Delivery guarantees" section.** Fill in the real numbers from the code or config, not from memory. Template:
   - Delivery is at-least-once. Dedupe on `<event id field>`.
   - A delivery succeeds on a `2xx` response within `<N>` seconds. Anything else is a failure.
   - Failed deliveries retry up to `<N>` times over `<window>`, at intervals of `<schedule>`, with `<jitter yes/no>`.
   - Events may arrive out of order. Use `<timestamp/sequence field>` to order them.
   - After the final attempt, `<what happens>`. You can recover with `<redelivery/replay mechanism>`.
2. **Make the troubleshooting page link to that section.** Its numbers must match. Add the failure modes it implies: endpoint disabled, repeated 4xx, slow responses, duplicate events.
3. **Add one idempotency example** to the Node and Python snippets, or right after them.

## Check that "reviewed" covers these

Review and writer sign-off usually check prose. They don't check whether the page is true. Spend about half a day on each:

- **Signature snippets.** Run them against a real signed payload from the shipping build.
  - They must verify against the raw request body, not re-serialized JSON.
  - The comparison must be constant-time.
  - They need a timestamp tolerance check if you sign timestamps.
  - Test a tampered payload, and test body-parser middleware that mangles the raw body. That is the most common copy-paste failure.
- **Event catalog.** Diff every example payload and schema against what the production code actually emits. Check field names, nullability, and any event type that exists in code but not in the catalog.
- **CLI testing section.** Run every command verbatim on a clean machine with the release candidate of the CLI. Confirm the install step and the version it names.

## When this flips to NO-GO

- **Oct 15:** the delivery-guarantees section isn't filled in with confirmed values.
- **Any time:** a signature snippet fails against a real signed payload, or the catalog is found to be out of sync with production.

If any of those happens, slip the docs, not the product. A wrong verification snippet is worse than a late page, because people paste it into production.

## Not blockers

Polish, extra languages beyond Node and Python, and a longer catalog narrative can all follow after ship.