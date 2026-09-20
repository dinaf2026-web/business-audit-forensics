# The Internal Audit Program

Load for internal-posture work: testing controls, vouching entries, verifying
assets, and checking authorization. This is the "are the records right and is
the business protected" half of the skill.

---

## Vouching, and why direction matters

The single most common testing mistake is running the test in one direction and
believing it covered both.

**Vouching (entry to document).** Start with a ledger entry, find the document
behind it. Tests whether recorded transactions are **real and accurate**.
Catches: fictitious entries, wrong amounts, wrong dates, wrong accounts,
personal expenses booked as business.

**Tracing (document to entry).** Start with a source document, find it in the
ledger. Tests whether real transactions were **recorded at all**. Catches:
unrecorded revenue, omitted liabilities, diverted receipts, off-book activity.

**These find different problems and neither substitutes for the other.** A
skimming scheme is invisible to vouching, because money that never entered the
books produces no entry to vouch. It shows up in tracing, and in the bank
reconciliation, which is tracing by another name.

Run both. Say in the workpaper which direction each test ran.

### What to vouch to

Not just "an invoice." A complete vouch usually wants:

- The **source document** (invoice, receipt, contract, statement)
- Evidence of **authorization** by someone with authority to authorize it
- Evidence of **receipt** of the goods or service
- The **payment** record, matched to the bank
- Correct **account, period, and amount**

Missing authorization on an otherwise valid transaction is a control finding,
not an accuracy finding. Keep them separate.

---

## Controls: design versus operation

Two separate questions, and passing one says nothing about the other.

**Design.** If this control worked exactly as described, would it prevent or
detect the thing it exists for? A monthly review that never compares against
anything is well-intentioned and useless.

**Operating effectiveness.** Did it actually happen, every period, by the
person supposed to do it, with evidence? A well-designed control that stopped
operating in March is not a control from March onward.

Test design by walking the process. Test operation by taking a sample of
periods or transactions and looking for the evidence. **A control with no
evidence that it ran did not run, for audit purposes.** "We always do that" is
not evidence.

### Segregation of duties

The four incompatible functions:

1. **Authorization** (approving a transaction)
2. **Custody** (having access to the asset or the money)
3. **Recording** (making the accounting entry)
4. **Reconciliation** (independently checking)

One person holding two of these is a risk. One person holding three or four is
the condition under which almost every small-business loss happens.

**In a small business, segregation is frequently impossible**, and saying "hire
more people" is not useful advice. Say so, and recommend the compensating
controls that actually work at that size:

- The owner opens the bank statement **before** the bookkeeper sees it, or
  receives it at an address the bookkeeper does not control
- The owner reviews and signs off the bank reconciliation monthly
- Dual signatures or approval above a stated dollar threshold
- Someone other than the preparer approves new vendors and new payees
- Periodic review of the accounting system's **audit trail** for edits and
  deletions of prior-period transactions
- Mandatory time off for whoever handles money, because ongoing concealment
  usually requires continuous access

### Writing a control finding that is useful

Four parts, in this order, and never a fifth part naming a person as a
wrongdoer:

1. **Condition.** What is, factually. "Bank reconciliations for the period were
   prepared by the same person who posts cash entries, with no documented
   review."
2. **Criteria.** What should be. The policy, the agreement, or plain standard
   practice. Name it.
3. **Cause.** Why the gap exists. Usually structural (one person does
   everything) rather than personal.
4. **Effect.** What could happen or did. Quantify where you can.

Then the **recommendation**, which is specific, assigned, and dated. "Improve
controls" is not a recommendation.

**Keep the tone on the process.** A finding that reads as an accusation gets
argued with instead of fixed, and if the matter ever does turn adversarial, an
accusatory internal memo written before the facts were in is an unhelpful
document to have authored.

---

## Asset verification

The classic four questions, and most reviews only ask the first.

| Question | What it means | How you test |
|---|---|---|
| **Existence** | Does it actually exist? | Physically observe it, or obtain third-party confirmation |
| **Ownership** | Does the entity own it, and free of what? | Title, deed, registration, lien and UCC search, loan documents |
| **Valuation** | Is the carrying amount supportable? | Cost records, depreciation schedule, impairment indicators, appraisal |
| **Possession** | Who actually has it? | Location, custody records, who holds the keys or credentials |

**Existence and ownership are different, and the gap between them is where
problems live.** An asset on the books that exists but is titled to an owner
personally, or pledged as collateral for a loan nobody recorded, is a real
finding that a physical count would never surface.

For any material asset, run a **lien and UCC search**. It is cheap, it is
public, and an undisclosed security interest changes what the balance sheet
means.

---

## Authorization testing for special transactions

Routine transactions get sampled. These get **examined individually, every
one**, because they are where value leaves a business and where the
documentation is most often absent.

- **Owner and related-party transactions**: draws, distributions, loans to or
  from owners, expense reimbursements, salary changes, personal use of assets
- **Asset acquisitions and disposals**, especially to or from a related party
- **Revaluations and write-offs**: inventory, receivables, fixed assets
- **New or changed banking**: accounts opened, signature authority changed,
  wire instructions changed
- **New vendors**, particularly ones added shortly before their first payment
- **Journal entries that are manual, round-numbered, period-end, or posted by
  someone who does not normally post entries**
- **Intercompany transfers** between entities under common control

For each: who approved it, did they have authority to approve it under the
operating agreement or delegated authority, and is the approval documented
contemporaneously or reconstructed after the fact?

**Check the governing document, not custom.** Operating agreements and
partnership agreements routinely require consent for distributions, owner
loans, or asset sales above a threshold, and those provisions are routinely
ignored by the people they bind. That is a finding, and it is one with real
consequences in a dispute or on a sale.

---

## Compliance testing

Against **external** requirements (law, regulation, licence, contract, loan
covenant) and **internal** ones (policy, operating agreement, delegated
authority).

Name the specific requirement, by section. "Not compliant with tax rules" is
unusable. "Distributions in 2025 exceeded the amount permitted under section
4.3 of the operating agreement without the written consent that section
requires" is a finding someone can act on.

**Loan covenants are the most commonly missed.** They sit in a document nobody
has read since closing, they frequently require financial ratios, reporting
deadlines, or an annual audit, and breaching one can accelerate the loan.
Read the loan agreement.

---

## Value-for-money review

Economy, efficiency, effectiveness. Largely non-financial, most often skipped,
and often where the money actually is.

- **Economy**: are inputs bought at reasonable cost? Vendor concentration,
  pricing against alternatives, unused subscriptions and services, duplicate
  insurance, auto-renewing contracts nobody reviewed.
- **Efficiency**: is the output reasonable for the input? Rework, manual steps
  that a system already does, time spent on low-value process.
- **Effectiveness**: is the intended result being achieved? A department, a
  program, or a spend that is running as designed and not producing what it was
  bought for.

Recurring charges are the highest-yield place to start in a small business,
because nothing stops them and nobody reviews them. Pull twelve months of card
and bank activity, group by merchant, and look at everything that repeats.

---

## Reporting and follow-up

**Rank every finding.** A list where everything is important is a list nobody
acts on. See `deliverables.md` for the severity scale.

**Separate the fix from the finding.** Recommendations are advice. The business
decides whether to take them, what the risk appetite is, and who does the work.
Advising and challenging is the role; deciding is not. If the reviewer designs
and implements the fix, the reviewer is auditing their own work next cycle, and
that has to be disclosed.

**Track open items across cycles.** The single most useful artifact in a
standing engagement is a list of prior findings with their current status.
Findings that recur cycle after cycle are themselves a finding, and usually a
more important one than anything new: it means the reporting channel is not
producing action.
