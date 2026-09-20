# Liabilities, Hidden Debt, and Amounts Owed

Load when the question involves what a business **owes**: undisclosed debt,
unrecorded liabilities, obligations concealed before a transaction, or the
collectability of what is owed **to** it.

---

## Why unrecorded liabilities are structurally invisible

An omitted liability leaves **no entry to test**. Every procedure that starts
from the ledger, including every exception test in this skill, is blind to it.
You cannot vouch an entry that does not exist.

This is the **completeness** assertion, and it is tested by working **from the
outside in**: from source documents, third parties, and subsequent events, into
the books. Never the other way round.

It is also the direction of error that matters most commercially. An overstated
expense embarrasses a bookkeeper. An unrecorded liability misstates equity,
misleads a lender, and can make a sale price or a buyout figure wrong by the
whole amount.

---

## The single most productive procedure: search for unrecorded liabilities

Cheap, standard, and skipped constantly.

**Take the disbursements made AFTER period end and ask, of each one, what
period the underlying obligation belongs to.** A payment made in January for
services delivered in December is a December liability. If it is not on the
December balance sheet, it is unrecorded.

The mechanics:

1. Pull all disbursements for a window after period end. Long enough to catch
   the normal payment cycle, which for most small businesses means at least
   sixty to ninety days.
2. For each above a threshold, find the invoice and read the **service or
   delivery date**, not the invoice date and not the payment date.
3. Compare against the recorded payables and accruals at period end.
4. Anything relating to the period and not recorded is a candidate.

`scripts/search_unrecorded_liabilities.py` automates the comparison and flags
post-period payments with no matching recorded liability.

**Supporting procedures in the same family:**

- **Vendor statement reconciliation.** Get the statement from the *vendor*, not
  from the client's ledger, and reconcile. The vendor knows what it is owed.
  This catches invoices the business never entered, and it is the only routine
  procedure that does.
- **Open purchase orders and unmatched receiving records.** Goods received and
  not invoiced are a liability whether or not an invoice has arrived.
- **Attorney letters.** Counsel knows about claims, threatened litigation, and
  contingencies before the accounting does.
- **Bank confirmations.** Confirm directly with the institution: all accounts,
  all loans, all lines, **and all guarantees**. A confirmation catches accounts
  and borrowings the ledger has never heard of.
- **Read the minutes and consents.** Borrowings, guarantees, and pledges are
  usually authorized somewhere before they are booked anywhere.
- **Subsequent-period bank activity.** A recurring payment appearing after
  period end that has no corresponding liability is a loan nobody recorded.

---

## Where hidden debt actually hides

### Obligations that do not look like debt

- **Merchant cash advances and receivables factoring.** Extremely common in
  small business, frequently characterized as a "sale of future receivables"
  rather than a loan, and often not on the balance sheet at all. The tell is in
  the bank statements: **daily or weekly fixed debits**, often to a funder with
  a generic name. Effective cost can be very high. Find them by scanning bank
  activity for regular same-amount debits, not by looking at the loan account.
- **Equipment leases and financing agreements** treated as pure expense.
- **Deferred purchase price, earn-outs, and seller notes** from a prior
  acquisition.
- **Customer deposits and unearned revenue** recorded as income on receipt.
  Money received for work not yet done is a liability, not a sale.
- **Gift cards, credits, and loyalty balances.**
- **Accrued vacation, commissions, and bonuses** never accrued.
- **Warranty, return, and rework obligations.**

### Obligations concealed deliberately

- **Personal guarantees.** The entity's balance sheet may be clean while the
  owner has personally guaranteed everything. This changes the picture entirely
  in a divorce, a buyout, an estate, or a credit decision, and it appears
  nowhere in the books. **Ask for the loan documents and read the signature
  pages.**
- **Related-party payables moved between entities.** A liability that lives
  wherever it is least inconvenient this year. Catch it with the intercompany
  matrix in `reconciliation-and-rollforward.md`: both sides should agree, and
  they frequently do not.
- **Owner loans reclassified as equity**, which is the roll-forward catch. It
  makes debt disappear without a payment.
- **Liabilities settled personally by the owner** and never recorded, so the
  business looks more profitable than it is.
- **Debt parked in a period after the one being examined**, with the invoice
  held in a drawer until the statements are issued.

### Statutory and trust obligations

These deserve separate attention because **they can attach to individuals
personally**, not only to the entity:

- **Payroll taxes withheld from employees and not remitted.** These are trust
  funds. Responsible persons can be personally liable for the trust-fund
  portion, and that exposure generally survives the entity's dissolution and is
  difficult to discharge. If withholding is being taken from employees and not
  paid over, **this is the most urgent thing in the file.** Say so immediately,
  and route it to a CPA and counsel the same day.
- **Sales and use tax collected and not remitted.** The same trust logic in
  many states.
- **Unpaid employment taxes, benefit plan contributions withheld and not
  deposited.**

**Verify the current rules, thresholds, and personal-liability tests against
primary sources.** Do not state the standard or the exposure from memory. Say
what the records show, say that personal exposure may exist, and get a
professional in.

---

## Public records: what the business will not tell you

Independent of the books, and mostly cheap or free:

| Source | Finds |
|---|---|
| **UCC filings** (state) | Security interests in business assets. A filing with no corresponding loan on the books is a finding. |
| **County recorder** | Mortgages, deeds of trust, mechanics liens, judgment liens |
| **Tax lien records** | Federal and state liens, which also reveal unpaid amounts |
| **Court records** (federal and state) | Judgments, pending suits, collection actions, bankruptcies |
| **Secretary of State** | Entity status, registered agent, good standing. A suspended or forfeited entity is itself a finding. |
| **Business credit reports** | Trade lines, collections, and filings the owner may not volunteer |

**Run a UCC and lien search on any engagement where debt is the question.** It
is inexpensive, it is public, and an undisclosed security interest changes what
every asset on the balance sheet is actually worth.

**Watch the timing.** A lien or filing dated shortly before a sale, a loan
application, or a partner's exit is worth putting on the timeline, whatever the
explanation turns out to be.

---

## Covenants and what a breach triggers

If there is a loan, read the agreement. Then test it.

- **Financial covenants.** Ratios, minimum balances, coverage tests. Compute
  them from the books and state whether each is met **as of each test date**,
  not just at year end.
- **Affirmative covenants.** Delivery of statements by a deadline, insurance,
  tax compliance, notice of material events.
- **Negative covenants.** Limits on additional debt, liens, distributions,
  asset sales, and change of control. **Distributions to owners in excess of a
  permitted amount are a common and quiet breach.**
- **Cross-default.** A breach on one facility can trigger others.

A breach can permit acceleration. **Whether a given fact constitutes a breach,
and what follows, is a legal question.** Compute the ratio, state the covenant,
state whether the number meets it, and route the consequence to counsel.

---

## Amounts owed TO the business

The mirror problem, and usually overstated rather than hidden.

- **Receivables aging.** Old balances that will not collect. Test whether the
  allowance is supportable rather than a plug.
- **Receivables with no underlying invoice**, or invoices never sent.
- **Owner and related-party loans receivable** with no note, no rate, no
  repayment schedule, and no repayments. Ask whether this is a receivable at
  all, or a distribution that was never characterized as one. **That question
  has tax consequences and goes to a CPA.**
- **Employee advances** that were never repaid or deducted.
- **Credits and deposits held by vendors** that nobody is tracking.
- **Insurance claims** receivable but never filed. See the notice deadlines in
  `regulatory-regimes.md`: a discovered loss frequently starts a clock.

---

## When debt is the whole question

Certain engagements are about the liability picture specifically. Each changes
what "complete" means:

- **Before a sale or a raise.** A buyer's diligence will find what you do not.
  Undisclosed debt discovered after signing becomes an indemnity claim.
- **Before or during a divorce.** Both the entity's debt and personal
  guarantees matter, and the incentive to overstate liabilities runs the
  opposite direction from the incentive in a lending context. Test both ways.
- **A partner or member exit.** The buyout figure depends on the liability
  schedule being complete.
- **Lending or credit decisions.** The statements were prepared for this
  audience. Test what the audience would be misled by.
- **Insolvency or distress.** Solvency, the timing of transfers, and payments
  to insiders before a filing carry specific legal consequences. **Stop and get
  counsel involved.** Do not characterize a transfer.

In every one of these, note **who the statements were prepared for** and
whether the same numbers were given to a different audience. Two versions of
one balance sheet, given to a lender and to a spouse, is a finding you report
factually and characterize not at all.
