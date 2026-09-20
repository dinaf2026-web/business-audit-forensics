# Exception Tests and Fraud Schemes

Load when running analytics over a transaction population, and when you need to
know what a given scheme actually leaves behind in the records.

---

## Read this before running any test

**Every test produces exceptions. Exceptions are not findings.** They go to the
corroboration gate in Phase 4. Nothing in this file produces a conclusion.

**Every test needs a positive control.** Before a test's zero means anything,
feed it an item you know it should catch and confirm it fires. A duplicate test
that reports no duplicates is telling you about the test until you have proven
it can see one.

This matters most for **negative results**, because a false negative has no
downstream catch. If you report a finding that is wrong, someone may correct
you. If you fail to look, nobody will ever know there was something to find.

**Run the control through any filter you applied.** A filter added to reduce
noise is part of the instrument. If you excluded a file type, a date range, or
a dollar threshold to cut clutter, your control has to survive that exclusion,
or the filter will hide the one real item and report it as absent.

**Keep "not screened" separate from "screened and clear."** If a source was
unavailable, a file would not parse, or a query was blocked, those items were
never examined. They must never share an output column with items that were
examined and cleared. Collapsing the two produces a report that claims a
population was tested when it was not. Say "N items not screened, re-run when
the source is available."

**Thresholds are assumptions.** Record every one. A test run at a $5,000
threshold covered nothing below $5,000, and that sentence belongs in the
workpaper.

---

## The standard battery

`scripts/exception_tests.py` runs most of these.

### Duplicates and near-duplicates

- Identical amount, date, and payee
- Identical invoice number, any vendor
- Same invoice number with a different amount, or the reverse
- Near-duplicates: same payee and amount within a short window
- Transposition-adjacent amounts (1,729 and 1,792)

**The trap.** Genuine duplicates are common and innocent. Two identical
deposits on one day are usually two real payments from two different people.
Two identical charges are often a legitimate recurring charge. **Never report a
duplicate without pulling the statement line or the invoice for both.**

### Round numbers

Round-dollar and round-hundred amounts above a threshold. Real commercial
transactions carry odd cents; invented ones frequently do not.

**The trap.** Transfers, loan payments, rent, payroll draws, and owner
distributions are legitimately round. Exclude or segregate known-round
categories before this test means anything.

### Timing anomalies

- Weekend and holiday postings
- Transactions outside business hours, where the system records entry time
- Entries posted on or immediately after period end
- Entry date materially later than transaction date
- Activity clustered just before a review, a closing, a departure, or a loan
  application

### Threshold proximity

Amounts sitting just below an approval limit. Payments of $4,950 against a
$5,000 approval threshold, repeatedly, is a pattern with one obvious reading.
You need to know the actual limits to run this, so ask for the delegated
authority policy.

### Vendor and payee tests

- Vendors added shortly before their first payment
- Vendors with no tax identification number on file
- Vendor address or bank details matching an employee's
- Vendor names one character apart from a legitimate vendor
- PO boxes and mail-drop addresses
- Single-payment vendors above a threshold
- Vendor bank detail **changed** during the period, and what was paid after

Vendor bank-detail changes deserve individual review every time. A change
followed by a payment is the whole mechanism of payment-diversion fraud.

### Sequence and gap analysis

Gaps in cheque numbers, invoice numbers, receipt numbers. Also duplicated
numbers, and numbers out of chronological sequence.

### Benford's Law

Compares the distribution of leading digits against the expected logarithmic
distribution. Naturally occurring financial figures tend to follow it;
fabricated ones often do not.

**Treat a Benford deviation as one of the weakest signals in this file.** It is
a direction to look, never evidence. It fails legitimately on populations with
assigned numbers, price points, thresholds, small samples, or bounded ranges.
Never put a Benford result in a report as support for a conclusion about a
person. It is a screening tool.

### Journal entry testing

The highest-yield population in most engagements, because journal entries
bypass the normal transaction cycle and its controls.

- Manual entries, as distinct from system-generated
- Entries posted by someone who does not normally post entries
- Entries to unusual account pairs
- Entries with blank, vague, or copy-pasted descriptions
- Round-dollar entries
- Entries at period end, especially those reversed early next period
- Entries touching suspense, clearing, or "ask my accountant" accounts
- Entries to equity, owner accounts, or intercompany accounts
- Entries posted into a **closed** prior period

Ask the accounting system for its **audit trail**: who created, who last
modified, when, and what changed. Most systems keep it and most users have
never exported it.

### Account-level tests

- Any account with a balance that has no supporting detail
- Suspense and clearing accounts with non-zero period-end balances
- Accounts that appear or disappear mid-period
- Accounts whose name does not match their contents
- Unusually large or unusually few transactions in an account relative to prior
  periods

### Ratio and trend analysis

Compare period over period and against the business's own history:

- Gross margin by line, month over month
- Expense categories as a percentage of revenue
- Payroll against headcount
- Cost of goods against units
- Days sales outstanding, days payable outstanding, inventory turns

**An unexplained step change is the signal**, not the level. A margin that
drops three points in one month and stays down has a cause, and the cause is
either commercial or it is not.

---

## Scheme typologies and what each leaves behind

You do not need to name the scheme to report the facts. Knowing the typology
tells you **where to look next** when a pattern appears. Naming it in a report
about an identified person is a legal characterization. Do not.

### Money taken before it is recorded (skimming)

Receipts diverted before entering the books. **Invisible to any test that runs
against the ledger**, because there is no entry.

Where it shows: bank deposits lower than sales records; a widening gap between
point-of-sale or shipping records and recorded revenue; customer balances that
do not agree to customer statements; unusual voids, refunds, or discounts;
declining margin with no cost explanation.

**Tracing, not vouching, is the test.**

### Money taken after it is recorded

Cash or receipts removed after entry, needing concealment in the books.

Where it shows: unexplained write-offs of receivables; refunds and credit memos
to accounts that never requested them; **lapping**, where a later customer's
payment covers an earlier one, showing up as chronically late posting of
receipts; deposits in transit that never clear.

### Fictitious or inflated vendors

Payments to an entity that does not deliver, or delivers less than billed.

Where it shows: the vendor tests above; invoices with no purchase order or
receiving evidence; round amounts; sequential invoice numbers from a vendor
that should not be sequential if it has other customers; invoices just under an
approval threshold; a vendor whose address or bank matches an employee.

### Payroll

Ghost employees, inflated hours, unauthorized rate changes, duplicate direct
deposits.

Where it shows: employees with no tax withholding; two employees sharing a bank
account or address; headcount that does not reconcile to the payroll register;
rate changes with no authorization; terminated employees still being paid.

### Expense reimbursement

Personal expenses claimed, amounts inflated, items claimed twice, fictitious
receipts.

Where it shows: duplicate claims across periods or across card and
reimbursement; round amounts; claims just under a receipt-required threshold;
weekend and vacation-period travel; the same receipt submitted to two entities.

### Misuse of owner and related-party accounts

Often the largest dollar movements in a small business, and usually the least
documented.

Where it shows: draws and distributions with no authorization; loans to owners
with no note, no rate, and no repayment; reclassification between loan and
equity with no entry, which is the roll-forward catch; personal expenses paid
by the business and coded to operating accounts; intercompany transfers that do
not reconcile.

### Financial statement manipulation

Not theft of assets but misstatement of results, usually to satisfy a lender, a
buyer, a partner, or a covenant.

Where it shows: cutoff problems at period end; reserves and accruals moving
without a change in underlying facts; capitalizing what was previously
expensed; revenue recognized early; related-party revenue; entries reversed
early in the following period.

**Motive is usually visible in the calendar.** Look at what was due around the
period end: a loan renewal, a covenant test, a valuation, a buy-sell, a tax
filing.

---

## Turning exceptions into a picture

A list of exceptions explains nothing. Four analysis modes make it legible.

**Temporal.** Timelines and flow diagrams. When did things happen relative to
each other and to external events? Sequence is frequently the entire finding,
and a timeline is the most persuasive exhibit available because it needs no
accounting knowledge to read.

**Relational.** Who is connected to whom, and how. Common ownership, shared
addresses, shared signatories, a vendor bank account matching an employee's.
Label links in plain words.

**Inferential.** Lay out the reasoning from evidence to proposition, link by
link, marking which links are **documented** and which are **inferred**. This
is where the discipline lives. An argument that does not separate the two is
the shape that gets excluded.

**Computational.** The queries, scripts, and statistics that got you there.
Versioned, with parameters recorded, re-runnable by someone else.

---

## The competing-interpretation discipline

**A transaction rarely has one available reading.** Before settling on one,
write down the others and say why yours fits business reality better.

The readings that are technically available and commercially absurd are not
answers, and the reading you never considered is the one the other side will
lead with. Writing this out costs ten minutes and it is the difference between
an analysis and an argument.

The innocent explanations that most often defeat a proposed finding:

- A promotional or zero-rate arrangement explaining absent interest
- A first billing cycle explaining an absent first payment
- Two genuine payments from two payers explaining identical amounts
- A same-day round trip between related entities explaining a matching pair
- A rounding difference against a third-party form, where the books are right
  on a cash basis and adjusting would create a receivable that never collects
- A timing difference at period end that reverses cleanly next period
- A system conversion explaining a balance that appears from nowhere

Go looking for these **before** you write the finding, not after someone else
raises them.
