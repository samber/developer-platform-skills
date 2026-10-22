# Stack Overflow templates

Replace every `<...>`. Staff write the technical body; no generative AI.

## Disclosure lines

✓ Good - names the relationship and the product, in the post:

```
Disclosure: I work at <Vendor>, which maintains <product>.
```

✗ Bad - disclosure only in the profile, or hidden in a link title:

```
See our guide: <link>
```

## Answer naming your own product

```
<One-sentence direct answer to the question as asked.>

<Code or steps that solve it, runnable as written, with the version it was tested on.>

Why it works: <the mechanism>.
If you use <product>, <how the same thing is done there, shown, not claimed>.
Disclosure: I work at <Vendor>, which maintains <product>.

Reference: <link to the docs page that this answer summarizes>
```

## Canonical self-answered Q&A

Tick "Answer your own question" on the Ask page (15 rep). Both posts must meet normal quality rules.

Question:

```
Title: <tool> fails with "<literal error string>" when <condition>

I run <command or code> with <product> <version> on <environment>.
It fails with:
    <full error output>
Expected: <what should happen>.
What I tried: <one or two things that do not work>.
Disclosure: I work at <Vendor>, which maintains <product>; I'm posting this Q&A to document a common fix.
```

Answer:

```
Cause: <one sentence>.
Fix:
    <code or config>
Verify: <command and expected output>.
Applies to versions <range>; for <older range>, <alternative>.
Disclosure: I work at <Vendor>, which maintains <product>.
```

## Redirect comments

Bug report:

```
Thanks, this looks like a bug rather than a usage question. Please file it at <public issue URL> with the output above; I've posted the workaround below. (I work at <Vendor>.)
```

Feature request:

```
<product> doesn't support this today. Feature requests are tracked at <URL>, where the team replies. (I work at <Vendor>.)
```

Account, billing or private data:

```
This needs access to your account, which nobody here has. Please contact <support route>. Flagging to close as not about programming. (I work at <Vendor>.)
```

Duplicate: flag or vote as duplicate of the canonical; the site posts the link comment itself. Add your own comment only to point at the version-specific part:

```
The <version> fix is in the second code block of the linked answer. (I work at <Vendor>.)
```

## Tag excerpt

The excerpt is usage guidance shown in the tag picker, not marketing.

✓ Good:

```
<Product> is <one-line neutral definition>. Use for questions about using <product>'s <SDK/CLI/API>. For bugs, feature requests or account issues, use <Vendor>'s own channels.
```

✗ Bad:

```
<Product> is the fastest, most loved <category> platform. Try it free at <link>!
```

## Tag wiki

```
## About
<Two-sentence neutral description, current major version.>
## Before asking
Include <product>, language and SDK versions and full error output. Common problems: <canonical links>.
## Where else to ask
Bugs: <issue URL>. Feature requests: <URL>. Account and billing: <support URL>.
```

## Data Explorer backlog query

Run on data.stackexchange.com (Stack Overflow database, refreshed weekly). Lists open questions in the tag with no upvoted or accepted answer, highest views first.

```sql
SELECT q.Id AS [Post Link], q.ViewCount, q.Score, q.CreationDate
FROM Posts q
JOIN PostTags pt ON pt.PostId = q.Id
JOIN Tags t ON t.Id = pt.TagId
WHERE t.TagName = ##TagName:string##
  AND q.PostTypeId = 1
  AND q.ClosedDate IS NULL
  AND q.AcceptedAnswerId IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM Posts a
    WHERE a.ParentId = q.Id AND a.PostTypeId = 2 AND a.Score > 0)
ORDER BY q.ViewCount DESC
```

For the answer-rate metric, add `AND q.CreationDate > DATEADD(day, -30, GETDATE())` and compare the row count with all open questions in the tag over the same window, keeping the same `ClosedDate IS NULL` filter on both sides.
