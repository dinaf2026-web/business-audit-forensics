# Reconciliation and the Roll-Forward

Load before any tie-out work. This is the phase that produces real findings,
and the roll-forward in particular is the highest-yield procedure in the skill.

---

## Why this phase matters more than exception testing

Exception tests find patterns. Reconciliation finds **facts**. A pattern is
arguable; a ledger balance that does not agree to a bank statement is not.

It is also the phase that protects you. Almost every false finding is a
pattern that was never reconciled to a source. Doing this first means the
exception tests run against data you already trust.

---

## Normalize first, and keep a data dictionary

Before matching anything:

- **Dates** to one format. Watch for day-first versus month-first, which are
  indistinguishable for the first twelve days of any month and silently wrong
  for the rest.
- **Amounts** to one sign convention. Decide whether a debit is positive and
  hold it everywhere. Parentheses for negatives survive extraction badly.
- **Counterparty names** to a canonical form, with the raw value retained.
  Never overwrite the original string.
- **Bank descriptors** parsed into merchant, method, and reference.
- **Account codes** mapped where the chart changed mid-period.

Keep a **data dictionary**: every field, what it means, where it came from, and
every transformation applied. It is a workpaper. Without it, nobody, including
you next month, can re-derive your numbers.

**Reconcile the extracted data to the document before using it.** If your
extracted deposits do not sum to the total the statement itself states for the
month, the extraction is wrong and everything downstream is wrong with it.
Check this per statement, not once.

---

## Bank and card reconciliation

Do the whole period. Not a sample, not the summary totals.

### The two-directional test

1. **Every ledger entry matches a statement line.** Failures here are entries
   that exist in the books and not in reality: duplicates, fictitious entries,
   wrong amounts, timing errors.
2. **Every statement line appears in the ledger.** Failures here are the more
   serious direction: real money moved and the books do not know. Unrecorded
   deposits, unrecorded withdrawals, off-book activity.

### Matching

Match on date, amount, and where available a reference number. Expect and
allow a small date window for clearing lag, and **record the window you
allowed** rather than eyeballing it.

Rank candidate matches and flag anything ambiguous rather than auto-matching
it. A one-to-many or many-to-one match is a finding to investigate, not a
nuisance to resolve quietly. `scripts/reconcile.py` implements this and keeps
ambiguous matches in their own bucket.

### Timing differences are not exceptions

Outstanding cheques and deposits in transit are normal. Prove them rather than
assuming them: they should clear in the following period. **An outstanding item
that never clears is a finding**, and stale outstanding cheques are a classic
place for concealment to sit.

### When a period reconciles fully, record it

Write down the accounts, the statements used, the ending balance, and the date
you did it. A clean reconciliation is a positive finding, it is reportable, and
it stops a future session spending days redoing it.

### Record what you could not reconcile

A missing statement is a boundary on your conclusions. If the last card
statement in the period closes before period end, then the period-end card
balance is **not confirmed**, and that sentence goes in the report. Do not let
a near-complete reconciliation be described as complete.

---

## The roll-forward: prior close against current open

**Run this on every engagement. It is the procedure most often skipped and it
has the highest hit rate.**

### The idea

A set of books can tie internally, balance perfectly, and pass every
within-period test, while the balances it *starts* with silently contradict how
the prior period *ended*. The workbook you were handed cannot show you this,
because the discrepancy is outside it.

Get the prior period's closing balance sheet and trial balance. Compare
account by account against the current period's opening balances. Every
difference needs a documented entry explaining it.

`scripts/rollforward_diff.py` does the comparison and flags undocumented moves.

### What you are hunting

**A liability that became equity, or the reverse.** An owner loan that closed
one year as a long-term liability and opens the next inside an equity account.
This is the highest-value catch in the whole skill, because it is invisible
inside either year's books and it has consequences that compound:

- It changes the owner's **basis**
- It changes whether later payments to the owner are **repayment of debt or
  taxable distributions**
- It changes what the balance sheet tells a **lender**
- It may require consent under the **operating agreement** that was never
  obtained

Flag it, quantify it, and say plainly that the tax and legal consequences need
a CPA and possibly counsel. **Do not state the tax treatment yourself.**

**An expense that became an asset.** Something written off in one year
reappearing as inventory or a capitalized asset at the start of the next.
Watch for the arithmetic tell: an equity swing that equals the sum of two
separate reclassifications exactly.

**An opening balance with no entry behind it.** Any account whose opening
figure cannot be traced to a closing figure plus a documented entry.

**An account whose name no longer describes its contents.** A "Draws" account
holding a credit balance that *increases* equity is not a draw account. A
"Suspense" or "Ask my accountant" account with a material balance is an open
question by definition. Misnamed accounts are what make a section unreadable,
and they are what a lender or tax preparer will misread.

### Reconstructing when the prior year is unavailable

If the prior-year statements cannot be obtained, say so and stop short of
asserting anything about the opening balances. Partial substitutes, in
descending order of strength: the prior-year tax return, the prior-year
lender-submitted statements, the accounting system's own prior-period reports
re-run today (weaker, because they reflect any subsequent edits), and the
audit trail.

**Re-running a prior-period report today is not the same as the report as
issued**, because entries may have been posted into a closed period since.
Comparing the two is itself a useful test, and a difference between them is a
finding.

---

## Intercompany and related-party reconciliation

Where more than one entity is under common control, reconcile **across** them,
not just within each.

Every intercompany transaction has two legs. Both should exist, in opposite
directions, for the same amount, on or near the same date. Build a matrix:
what each entity says it owes and is owed by each other entity. The cells
should agree in pairs.

**Disagreements between the two sides are among the most productive findings
available**, and they are invisible to any single-entity review. A transfer
recorded as a loan by one entity and a capital contribution by the other, or
recorded by one and not the other at all, changes the balance sheet of both.

**Watch for round trips.** Money that leaves an account and returns the same
day, or moves out and back through a related entity, can net to nothing in the
ledger while both legs are booked to an account that makes them cancel. The
net effect is zero and the transaction disappears. Test on **gross** movement,
not net.

Also cross-check against any **standalone schedule** the business keeps outside
the accounting system: a spreadsheet of contributions, a loan register, a list
of deposits to an affiliate. These frequently contradict the ledger, and the
contradiction is the finding.

---

## Cutoff testing

Transactions recorded in the wrong period. Look at the days either side of
period end:

- Revenue recorded before it was earned, or held back into the next period
- Expenses pushed forward or pulled back
- Deposits in transit that are unusually large or unusually numerous
- Cheques dated in the period and not released until after it
- Journal entries dated period-end and posted weeks later

The accounting system's **entry date** versus the **transaction date** is the
decisive field here, and it lives in the audit trail. Ask for it.

---

## The reconciliation workpaper

Whatever tool produced it, the workpaper must show:

- The period, the accounts, and the source documents by name
- Opening balance, per books and per statement
- Each reconciling item, with an explanation, not just an amount
- Closing balance, per books and per statement, and whether they agree
- Items that could not be resolved, listed individually
- What was not covered and why

Anyone should be able to re-perform it from the workpaper alone. If they
cannot, it is notes, not a workpaper.
