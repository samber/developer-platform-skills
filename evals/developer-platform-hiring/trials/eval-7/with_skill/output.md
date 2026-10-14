**This is a DevRel hire, so I used `devrel-hiring` instead of `developer-platform-hiring`.**

`developer-platform-hiring` excludes this role. Discord, tutorials and sample apps, conference talks and integrator feedback are developer advocate and community work. Its own hand-off line sends that to `samber/developer-relations-skills@devrel-hiring`. "Developer Platform Engineer" would also attract the wrong candidates: the term mostly means internal-platform (Backstage, CI/CD) engineers.

⚠️ I couldn't read the `devrel-hiring` reference files (permission denied). Everything below comes from its `SKILL.md` plus my own working assumptions, which I mark as such. Its question bank and posting template are not used.

## Assumptions

I couldn't ask the skill's interview questions one at a time, so I assumed these. Correct any that are wrong and I'll redo the affected parts.

- **Company:** early or growth startup, Series A, and this is the first DevRel hire.
- **Role:** developer advocate, product-focused, with a strong educator lean. It is not a pure community manager and not a pure DX engineer.
- **Funding driver:** developer adoption plus product input.
- **Go-to-market:** product-led, API-first.
- **Coding depth:** high. Samples must be shippable and the candidate must be able to critique API design.
- **Hiring jurisdiction and comp range:** unknown.
- **Interviewer-hours per candidate:** about 6 to 8, no recruiter.

## Posting self-audit: pit-trap risk

The brief is close to the skill's **pit trap**: one person covering community, content, speaking and product feedback with no stated resources or goal. Each skill is holdable by one person, but the volume across all four is a lot.

Before you publish, do three things:

1. State the 12-month goal.
2. State the budget: travel and conference fees, and who covers Discord moderation outside the hire's hours.
3. State the reporting line and the ladder.

Without these, the posting fails the audit.

## Artefact 1: scorecard

**Mission:** Make Okabe Cloud's API the easiest one for external developers to adopt. The metric is time-to-first-successful-API-call, plus integrator feedback shipped into the product roadmap.

**Outcomes, ranked.** The targets are placeholders; set them against your baselines.

1. Cut median time-to-first-call by 30% by day 180. The route is a friction log, then fixes shipped with the product team.
2. Ship 6 tutorials and 3 sample apps in year one, each with a tracked completion or fork rate.
3. Have at least 12 integrator-sourced insights adopted into the product backlog, with at least 4 shipped, by month 12.
4. Get at least 3 conference talks accepted per year, at least one from the community-sourced pipeline.
5. Reach a median Discord first-response time under 4 hours on weekdays, with at least 70% of questions answered or resolved.
6. Build a moderation system and a volunteer or champion layer, so Discord doesn't depend on one person.

**Competency weights.** These are my own working assumption; adjust them before use.

| Competency | Weight |
|---|---|
| Technical depth (code, API design critique) | 25% |
| Teaching and written content | 25% |
| Developer empathy and feedback synthesis | 20% |
| Community and moderation | 15% |
| Public speaking | 10% |
| Self-direction (first hire, no incumbent) | 5% |

**Level and pay.** Set level and pay together, using your general engineering ladder. Publish a range. If you don't, say why, after checking your jurisdiction's pay-transparency rules. I can't confirm these for you.

## Artefact 2: interview loop

The skill says there is no standard DevRel loop, so choose 3 to 5 formats. Mine is 5 stages, about 6.5 interviewer-hours.

1. **Portfolio review (1h, async, two reviewers).** Score public writing, speaking, code in public, community evidence, teaching artefact and developer-voice artefact. Name negative signals explicitly: followers with no substance, only self-promotion, no shipped code, can't name a developer they helped. Do this first, before asking the candidate for any new work.
2. **Conversational round with the hiring manager (1h).** Cover motivation, the first-hire mindset, and the DevRel-opinion question below.
3. **Technical and teaching round (1.5h).** The candidate gets a 20-minute heads-up and a small API doc. They explain it live to a mock new integrator, then review a flawed sample for misuse-prone design. This tests the technical and teaching pillars directly.
4. **Product and feedback round with a product or engineering lead (1h).** Give the candidate 5 anonymised raw integrator complaints. They triage them and write a short product-facing summary.
5. **Founder or exec round (45 min).** Cover the 12-month goal, resourcing and the trade-offs of being a team of one.

**Presentation and work sample.**
- If the portfolio shows public talks, review those and skip a live presentation.
- If the portfolio is thin, offer a **paid** working session, such as a 15-minute lightning talk or a documentation-edit exercise. Never ask for unpaid spec work when a public portfolio exists.

**Questions.** Write 2 or 3 per competency and ask them to every candidate. Examples:

- **DevRel-opinion question:** "What would make you recommend we *not* do a conference this year?" The skill says candidates find this the hardest round because there is no memorised answer.
- **Feedback synthesis:** "Describe a time developer feedback changed a roadmap. What was the evidence, and who did you convince?"
- **Community:** "A long-time member is hostile in a public thread. Walk me through your first 10 minutes."
- **Scope:** "You're one person. Rank Discord, tutorials, talks and feedback for your first 90 days, and justify the order."

**Scoring mechanics.**
- Each interviewer submits an independent, evidence-noted score before any debrief.
- Combine the scores mechanically against the weights above.
- Do not give a holistic gut score after a group discussion.

## Artefact 3: portfolio evaluation

Score the six signals, weighted for a product-focused advocate with an educator lean:

| Signal | Weight |
|---|---|
| Code in public | 25% |
| Teaching artefact | 25% |
| Developer-voice artefact | 20% |
| Community evidence | 15% |
| Public writing | 10% |
| Public speaking | 5% |

Since talks are only about three a year, speaking carries the least weight. I assumed these weights, since I couldn't read the rubric file.

## Artefact 4: 30/60/90 ramp

- **Day 30:** Use Okabe's API as a new developer would. Ship a friction log, plus a Discord health baseline: response times, top repeat questions, and the moderation gaps.
- **Day 60:** Ship the first tutorial plus one sample app, paired with an engineer. Submit the first CFPs.
- **Day 90:** Own the Discord and content programme end to end. Deliver a documented plan for the time-to-first-call metric and the feedback pipeline into product.

## Sourcing

I couldn't read the sourcing file, so this is my own suggestion, not the skill's.

- Look in developer-community networks, DevRel-focused communities, and conference speaker lists in your API's domain.
- Check your own Discord and GitHub for active integrators. Candidates who already use the API are strong.
- Treat open-source contribution history as a screen.
- Don't post on PlatformCon or Backstage channels.

## Quality-gate status

- ✅ Outcomes are ranked and quantified, and tied to a funding driver.
- ✅ Every question maps to a scorecard competency.
- ✅ The loop tests the pillars the role is measured on.
- ✅ No unpaid spec work is requested.
- ✅ Scores are independent and combined mechanically.
- ⚠️ **Compensation:** you haven't given a range or a jurisdiction.
- ⚠️ **Pit-trap audit:** it passes only once the goal, budget and reporting line are written into the posting.
- ⚠️ **Sources:** the competency weights are my assumptions, not sourced.

## Questions for you

1. Is Okabe's API sold sales-led or product-led?
2. Who handles Discord moderation outside this person's hours?
3. What is your comp range and hiring location?
4. Do you have a baseline for time-to-first-call?

Answers to 1 and 3 change the loop and the posting the most.