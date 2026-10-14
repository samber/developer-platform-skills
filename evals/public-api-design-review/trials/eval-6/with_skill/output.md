# Unsticking the Quilsworth API PR and preventing a repeat

I applied the `public-api-design-review` skill. It buckets a block as Must-change only when it cites a written rule or precedent. Anything else is an Improvement.

## Verdict

None of the three comments qualifies as a block as written. Nothing here is a defect in the teammate's design. The PR is unstuck on the merits, and the remaining work is a conversation plus a paper trail.

| # | Staff engineer's comment | Cited rule? | Bucket | Why |
|---|---|---|---|---|
| 1 | "snake_case is dated, switch to camelCase" | None. Taste. | Not a finding | The only citable casing rule is "one casing everywhere, consistency of the choice is the check". The design passes it. |
| 2 | "Nest /refunds under /payments" | None. Taste. | Not a finding, or at most an Improvement | The checklist's nesting rule is a depth limit (2-3 levels). A top-level `/refunds` filtered by `payment_id` is the checklist's own fix for deep nesting. Both shapes pass. |
| 3 | "We settled pagination differently last year, going back to cursors" | Claimed, not shown | Not a block until the decision is produced | A written sign-off exists from 14 months ago. The skill defers to prior reviews and reopens one only if it was a significant mistake that matters now. |

The skill's own negative example is almost this comment word for word: a "BLOCKING" tag on a taste call, with "reads better" as the rationale. The format exists to prevent exactly this.

The review has been blocked for 8 days, which is already past the one-week benchmark for a small API.

## Checks before you act

Three facts could change the verdict. Check them first; this should take about 30 minutes.

1. **Is there a decision from the last year?**
   - Ask the staff engineer for the link to the "settled differently last year" decision.
   - If it exists and supersedes the 14-month-old sign-off, the teammate must either follow it or record a deviation with a rationale. That is a real finding, and a Must-change citing that precedent.
   - If it doesn't exist, comment 3 falls away.
2. **What casing do Quilsworth's other APIs use?**
   - If the rest of the public surface is camelCase, the staff engineer has a legitimate point. It is about cross-surface consistency, not about snake_case being dated.
   - It still isn't a block unless a written rule says so. It becomes an Improvement, or a Must-change if the corpus mandates it.
   - If the surface is mixed or snake_case, comment 1 is plain taste.
3. **Run a spec linter (Spectral class) over the spec.**
   - The skill runs mechanical checks first. "Internally consistent" is a claim to verify, not trust.
   - Check every query parameter, enum, and boolean, not only the response fields.

My assumptions are that this is an external-facing API at design or beta stage and that the teammate's pagination is not cursor-based (the comment says "going back to cursors"). If the API has already shipped, a casing switch is a breaking change and has to go through your versioning policy. That makes the staff engineer's demand even weaker.

## How to unstick it

1. **Talk to the staff engineer first, privately, before the PR thread.**
   - Don't overrule them in public.
   - Ask one question: "Which written rule or precedent does each point cite?"
   - Frame it as the review process, not as a challenge to their judgment.
2. **Offer a split.**
   - Pagination: they produce the decision link, or withdraw it.
   - Casing and nesting: they downgrade both to non-blocking suggestions.
   - If they believe Quilsworth should standardise on camelCase, that goes to a corpus change, applied to future APIs (see "Preventing a repeat").
3. **Set a deadline.** If there's no agreement in 2 business days, you act as the override authority, since two people already escalated to you. Record the decision in the PR: what was decided, which rule or precedent supports it, and who decided.
4. **Have the teammate add a "Design decisions" section to the PR.** It should cover casing, why `/refunds` is top-level, and pagination with a link to the 14-month-old review. This is the paper trail the next reviewer cites instead of re-litigating.
5. **Close out for the teammate.** Tell them the design stands, thank them for the 8 days, and don't ask them to re-justify the sign-off.

### Draft message to the staff engineer

> Hi, the refunds API PR has been blocked 8 days and two people have escalated to me. I want to unblock it fairly. Our process says a blocking comment cites a written rule or precedent; otherwise it's advisory.
>
> - Casing and nesting: I can't find a rule either way. The design is consistent and the checklist's nesting limit is about depth. Can we mark these non-blocking?
> - Pagination: there's a sign-off from 14 months ago. Can you link the later decision you mean? If it supersedes the old one, I'll ask the author to align or record a deviation. If not, I'll treat the old decision as binding.
>
> If you think we should standardise on camelCase, I'd like to take that to a corpus RFC for future APIs. Can we settle this by Wednesday?

### Draft PR comment

> Review status: no Must-change findings open. Casing, `/refunds` placement, and pagination are recorded as design decisions with their rationale and precedent in the "Design decisions" section. The previous BLOCKING comments are reclassified as non-blocking pending a cited rule. Decision by [name], [date].

## Preventing a repeat

The skill's default program for this situation is a linter plus two named reviewers (Zalando's shape). The design below is that default. Two inputs I don't have could change it:

- **One or two teams own all APIs:** step down to a linter-only CI gate.
- **Many teams, or median turnaround past ~2 weeks:** move toward a federated reviewer pool.

Steps, in order of effort:

1. **Make "cite a rule or it's advisory" explicit.**
   - Tag every review comment `Must-change [rule]` or `Improvement`.
   - A block with no citation is advisory by definition.
   - This is the single change that would have prevented this incident.
2. **Write the rule corpus.** Fork a public one (Zalando or Adidas) rather than starting blank. Use MUST/SHOULD/MAY keywords and adapt it before enforcing it. Put your own casing decision in it, one way or the other.
3. **Add a precedent log.**
   - Record settled decisions and accepted deviations in a versioned file in the repo.
   - Use a marker for deviations, like Google's `aip.dev/not-precedent`.
   - The deviator records a rationale, and the reviewer cannot block on taste.
   - The 14-month-old pagination sign-off would have lived here and settled comment 3 in one click.
4. **Wire a linter into CI and the editor** so mechanical findings never cost human review time.
5. **Name the override authority and an SLA up front.** For example: first response within 2 business days, decision within 5, and escalation to a named person. Publish it so disagreements resolve in days, not weeks.
6. **Trigger review by audience and lifecycle, not by habit.** Make review required for external APIs at beta (blocking) and at GA if the surface changed. Make it recommended at alpha and skipped for internal-only APIs.
7. **Review the spec, not the finished code.** That way feedback arrives before the code exists.
8. **Give the staff engineer a legitimate channel.** Their instinct is useful: consistency across the surface is the real goal. Invite them to propose corpus changes by RFC, applied prospectively, and consider making them one of the two named reviewers once the citation rule is in place.

### Health metrics

- Target median turnaround under 1 week for small APIs, and escalate any review that passes 2 weeks.
- If teams start shipping without review, the process is too heavy.
- If defects reach GA that a written rule would have caught, it's too light. Add the rule to the linter.

Treat these thresholds as Google-derived calibration points, not laws.

## Questions that would sharpen this

- Is the API shipped, in beta, or still a design?
- Who consumes it: internal teams, named partners, or the public?
- Does Quilsworth have a written API style guide or rule corpus?
- How many teams ship APIs?
- What casing do the other public Quilsworth APIs use?
- Can the staff engineer produce the "last year" pagination decision?