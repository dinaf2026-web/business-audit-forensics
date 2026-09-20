# Sampling, Assertions, and Deficiency Severity

Load when the population is too large to examine in full, when you need to say
precisely **what a test proves**, or when you need to rank a control failure in
the vocabulary an accountant or a lender will recognize.

---

## First: should you sample at all?

This skill's default is to examine **whole populations**, and that default is
correct more often than the profession's habits suggest. A full reconciliation
of twelve months of bank activity is achievable by script in minutes, and it
produces a fact rather than an inference.

**Examine the whole population when:**

- The population is small enough to handle (most small-business bank, card, and
  journal-entry populations are)
- You are hunting for a specific item rather than estimating a rate
- The engagement is **forensic**. A sample cannot prove absence, and a
  fraudulent transaction is precisely the item most likely to fall outside a
  random draw. In an investigation, sampling answers the wrong question.
- Any single item could be material on its own

**Sample when:**

- The population genuinely cannot be examined in full within the engagement
- You are testing whether a **control operated**, which is a question about a
  rate of compliance rather than about any particular transaction
- The purpose is assurance about the population as a whole, not discovery

**State which you did.** "We examined all 1,247 disbursements" and "we examined
25 of 1,247 disbursements" support very different sentences, and readers will
assume the first unless you say otherwise.

---

## Selection methods

### Random

Every item has an equal chance of selection. The default for testing a control
over a large, listable population.

Requires a complete population listing, and getting that listing is itself a
test: if the business cannot produce one, you have found something.

Statistically defensible and free of selection bias. Its weakness is that it is
blind to risk, so a random sample of 25 from 1,200 payments will usually miss
the one unusual payment entirely.

### Targeted (judgmental)

Deliberately selecting items with risk characteristics: above a dollar
threshold, non-standard, dated at period end, related-party, manually posted,
overriding a system control, or involving a payee seen for the first time.

Efficient and risk-focused. **Not statistically representative**, so results
cannot be projected to the population. Document the criterion for every item
selected, or the selection looks arbitrary later.

**This is the right primary method in most small-business and forensic work**,
and it is what the exception battery in this skill effectively performs.

### Systematic

Every Nth item from a random start, with the interval set by population divided
by sample size. Gives even coverage across the period, which matters when you
suspect a problem concentrated in one part of it.

Its failure mode is a population with a repeating cycle. If the interval lands
on the same weekday, the same batch position, or the same approver every time,
the sample is biased in a way that is invisible from the output.

### Haphazard

Selection with no deliberate pattern, used where no sequential listing exists.

Not statistically valid, and genuinely hard to do without unconscious bias:
people reach for round numbers, items at the top of a page, and names they
recognize. Treat it as the last resort and say in the workpaper that it was
used.

---

## How large a sample

There is no universal number, and any table presenting one is a convention
rather than a rule. **Confirm the expected size against whatever framework
actually governs the engagement** before quoting a figure to anyone.

What genuinely drives the size:

- **How often the control operates.** An annual control gives you one instance
  to test. A daily control gives you hundreds.
- **Risk.** Higher inherent risk in the account or process means more items.
- **Redundancy.** A control that is the only thing addressing a significant
  risk needs more testing than one with a second control behind it.
- **History.** A control that failed last period, or has never been tested,
  needs more.
- **Reliance.** If anyone else intends to rely on your testing, the bar rises.

The shape to expect: an annual control is tested once; a quarterly or monthly
control needs only a handful of instances; a weekly control needs perhaps five
to fifteen; a daily or per-transaction control runs to several dozen, rising
with risk. Those are orders of magnitude, not authority.

**Record the number and the reasoning.** A sample size with no stated basis is
the first thing a reviewer questions.

---

## When a sample turns up an exception

This is where sampling most often goes wrong, and the error is always in the
same direction: treating one exception as one problem.

- **One exception in a sample implies a rate in the population.** If you found
  one failure in 25, the population rate is not "one". Say what the sample
  implies and what it does not.
- **Investigate the cause before extrapolating.** An exception caused by a
  one-off system change is not the same as one caused by a control nobody
  performs. The second projects; the first may not.
- **An exception may mean the sample was too small**, not that the control
  mostly works.
- **In a forensic posture, a single exception ends the sampling.** Stop
  sampling and examine the whole population. You are no longer estimating a
  rate; you are investigating an item.

---

## Assertions: saying what a test actually proves

A test proves something specific. Naming which one stops the common failure of
running a procedure and then claiming more from it than it supports.

| Assertion | The question | What tests it |
|---|---|---|
| **Existence** | Does this recorded thing exist? | Vouching, physical observation, third-party confirmation |
| **Completeness** | Is everything that happened recorded? | **Tracing** from source documents into the ledger, bank-to-book |
| **Accuracy** | Is it recorded at the right amount? | Recalculation, agreeing to the invoice or statement |
| **Cut-off** | Is it in the right period? | Examining transactions either side of period end, entry date versus transaction date |
| **Valuation** | Is the carrying amount supportable? | Allowance and impairment review, appraisal, cost records |
| **Rights and obligations** | Does the entity own it, and owe it? | Title, deed, registration, lien and UCC search, loan documents |
| **Presentation and disclosure** | Is it classified and described correctly? | Account classification review, the roll-forward, misnamed-account check |

**The pairing that matters most in this work:** existence and completeness pull
in opposite directions and are tested in opposite directions.

- **Vouching** (entry to document) tests **existence**. It catches fictitious
  and inflated entries.
- **Tracing** (document to entry) tests **completeness**. It catches
  unrecorded activity, which is where skimming and off-book money live.

A procedure that only vouches has said nothing about completeness, and
completeness is the assertion most forensic engagements actually care about.

---

## Deficiency severity

This skill ranks findings **Critical / High / Medium / Low / Open question**,
which is right for an owner deciding what to do on Monday. But control failures
have a standard professional ladder, and using it makes a finding legible to a
CPA, a lender, or an incoming auditor.

| Standard term | Meaning | Maps to |
|---|---|---|
| **Deficiency** | The control, as designed or as operated, cannot prevent or detect a misstatement on a timely basis | Medium or Low |
| **Significant deficiency** | Less severe than a material weakness, but important enough to warrant the attention of those charged with governance | High |
| **Material weakness** | There is a reasonable possibility that a material misstatement will not be prevented or detected on a timely basis | Critical |

Three things that carry a deficiency up the ladder, worth knowing because they
apply directly to small businesses:

1. **Pervasiveness.** A failure in an entity-level control, or in general IT
   controls, affects every process beneath it and is rarely minor.
2. **Aggregation.** Individually small deficiencies in the same process
   combine. Three minor gaps that together mean no one ever independently
   checks cash is not three minor gaps.
3. **Fraud by anyone senior.** Where management is involved, magnitude stops
   being the test. A small amount taken by someone who can override controls
   says something about the control environment that the amount does not.

**Compensating controls** move a finding **down** the ladder, and they are the
reason a one-person bookkeeping operation is not automatically a material
weakness. If the owner opens the bank statement before the bookkeeper sees it
and signs the reconciliation, that mitigates. Say so, and say plainly when no
compensating control exists.

---

## A scope note on SOX

Much of the best-documented material on control testing comes from the Sarbanes
Oxley regime, and the vocabulary above is largely its vocabulary.

**Where the entity IS a public company, apply it properly.** Section 404(a),
management's assessment of internal control over financial reporting, applies
to **every** filer with no small-company exemption. Section 404(b), the auditor
attestation, is the part carrying exemptions for non-accelerated filers,
emerging growth companies, and smaller issuers. Confusing (a) with (b) is the
most common error in this area. The full requirements, the filer definitions,
the disclosure consequences of a material weakness, and the forensic-specific
provisions on record destruction and illegal-act escalation are in
`regulatory-regimes.md`.

**Where it is not, SOX imposes nothing.** Section 404 does not apply to a
private LLC, a family business, or a partnership as a matter of law. Do not
tell an owner they are required to do any of this, and never use the obligation
as a reason someone should hire anyone.

**The methodology transfers either way**, which is why it is here: scope to
what matters, identify the risk, identify the control, test design and
operation, classify what you find, and document it so someone else can
re-perform it. That sequence is good practice at any size. It is method, not
obligation, and the report should say which.

Use the professional vocabulary when the audience is professional. Use plain
words when the audience is the owner.
