# Copy templates: steps, Zap templates, help article

Source: docs.zapier.com integrations/publish/integration-build-guidelines and zap-templates.

## Step names and descriptions

```
// ✓ Good - title-cased name, product noun, standard opening, period, no app name
Trigger  New Paid Invoice   key: new_paid_invoice   noun: Invoice
         "Triggers when an invoice is marked as paid."
Action   Create Customer    key: create_customer    noun: Customer
         "Creates a new customer."
Search   Find Invoice       key: find_invoice       noun: Invoice
         "Finds an invoice by number or customer email."

// ✗ Bad - generic key, "Get" instead of "Find", app name in copy, generic update trigger
Trigger  Updated invoice    key: trigger_1
         "Triggers when an Invoice is updated in Acme Billing"
Search   Get Invoice        key: search_2
```

## Zap template title and description

Rules: title starts with an action verb, sentence case; present tense, active voice; name both apps; say "new" or "updated" when the trigger event is one; never "sync" or "automatic"; no you/we/I. The description opens with the user's goal, is unique to this template, and ends with an italic note for any setup step or limitation. No links and no Zapier vocabulary (Zap, trigger, action) in the description. Descriptions that only swap app names, or repeat the title, are rejected.

```
Title: Create Acme Billing invoices from new won deals in HubSpot

Description: Bill customers the moment a deal closes. When a HubSpot deal
moves to Closed Won, this workflow creates a draft invoice in Acme Billing
with the deal amount and the contact's billing details.
*Note: Map your HubSpot line items to Acme Billing products during setup.*
```

```
// ✗ Rejected - "sync", "automatically", second person, description repeats title
Title: Automatically sync your HubSpot deals to Acme Billing
Description: Sync HubSpot deals to Acme Billing.
```

Pre-fill every required field with the best mapping. Add filters only when the template is useless without one.

## Help-center article per job

```
# <Job, in the user's words>, with <Product> and Zapier

1. What this does: one sentence, the job and the result.
2. Before you start: plan or permission needed in <Product>; where the API key or OAuth connection lives.
3. Embedded template(s) for this job.
4. Field mapping notes: the 3-5 fields people get wrong.
5. Troubleshooting: the error messages your integration raises, each with its fix.
```
