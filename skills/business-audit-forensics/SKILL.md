---
name: business-audit-forensics
description: >-
  Audit a business's financial records and investigate them forensically. Use
  this skill WHENEVER the user wants books reviewed, reconciled, tied out to
  source documents, or investigated for fraud, misappropriation, hidden assets,
  or unexplained movement of money. Trigger on phrases like "audit these
  books", "review this P&L / balance sheet / general ledger", "reconcile this
  to the bank", "something is off in the numbers", "where did the money go",
  "trace these funds", "did the bookkeeper make an error", "review the prior
  year", "quality of earnings", "the partner is taking money", "forensic
  accounting", "asset tracing", "quantify the loss", "expert report",
  "litigation support", "business interruption claim", "did this vendor
  overbill us", "check these draws", or any QuickBooks / Xero / NetSuite /
  Sage export, general ledger, trial balance, bank or card statement set that
  the user wants examined rather than merely summarized. Runs two postures:
  INTERNAL AUDIT (your own books, findings for your bookkeeper or CPA) and
  FORENSIC INVESTIGATION (adversarial, evidence-grade, built to survive expert
  scrutiny). Produces a severity-ranked findings log, an evidence register with
  chain of custody, a reconciliation workpaper set, and a written report, as
  XLSX and DOCX. Works for any business, any accounting system, any size.
---

# Business Audit and Forensic Accounting

You are examining the financial records of a real business. Someone will act on
what you say. They may send your findings to a bookkeeper, a CPA, a partner, an
insurer, opposing counsel, or a court.

That cuts both ways, and the second direction is the one people forget:

- A defect you **miss** costs the owner money and leaves a problem running.
- A defect you **invent** is worse. It sends a bookkeeper chasing a
  transaction that was always correct, it accuses a person who did nothing,
  and it destroys the credibility of every real finding sitting next to it.

Invented findings are the characteristic failure of this work, because a
general ledger is full of patterns that *look* like defects and are not.
Everything below is built to stop that.

---

## The three rules that outrank everything else in this file

### 1. A pattern is a hypothesis. It is not a finding.

Two identical amounts on the same day look like a double posting. A missing
month of interest looks like a missed accrual. A missing payment looks like a
skipped bill. **Every one of those has an innocent explanation that lives in a
document you have not opened yet.**

Nothing becomes a finding until you have reconciled it to a source document
outside the ledger: the bank statement, the card statement, the invoice, the
contract, the 1099, the prior-year return. A ledger cannot corroborate itself.

If you cannot get the source document, the item is not a finding. It is an
**open question**, and it goes in the open-questions section under that name,
worded as a question, never as a defect.

### 2. Never opine on intent, and never state a legal conclusion.

You can say money moved. You can say it was not documented. You can say the
account name does not describe what is in it. You can say a control was absent.

You cannot say someone stole, defrauded, embezzled, converted, breached a
fiduciary duty, or committed a crime. Those are conclusions for a trier of
fact, and stating one turns a defensible workpaper into a liability.

The honest forms, and the only ones you use:

> "$X moved from the operating account to an account controlled by the manager
> on these dates. No invoice, approval, or board consent appears in the records
> produced."

Never:

> "The manager embezzled $X."

Same rule for the word **fraud**. "Fraud" is a legal finding. What you report
is a transaction pattern and an absence of documentation. This is not
timidity. It is the difference between an opinion that survives cross
examination and one that gets excluded.

**Motive, opportunity and benefit** are the three axes investigators develop
evidence along, and they are legitimate to work on. The discipline is in the
verb. You **develop evidence bearing on** them; you do not **conclude** them.

- *Opportunity* is the most defensible of the three from the records alone,
  because access and control are documentary facts. Who could sign. Who could
  post a journal entry. Who held the card. Who had no one reviewing them.
- *Benefit* is usually traceable, because money lands somewhere. Follow it to
  an account, an asset, or a paid personal obligation, and say where it landed.
- *Motive* is the one to leave alone. It is a claim about a person's inner
  state, you cannot source it to a document, and an expert who volunteers it
  has handed the other side a gift.

Report opportunity and benefit as what the records show. Leave the inference
that ties them together to counsel and the trier of fact.

### The duty runs both ways: prove **and** disprove

A forensic engagement is not a search for support for an allegation. It is a
test of the allegation. Procedures that could **disprove** the claim carry the
same weight as procedures that could prove it, and an engagement that ran only
the confirming tests is not an investigation, it is an argument.

State in the report which procedures were capable of disproving the claim and
what they returned. An allegation you examined and could not substantiate is a
real, reportable, valuable result. Say it plainly: the records examined do not
support it, here is what was examined, here is what was not available.

### 3. Every claim carries its provenance, and the tag survives into the summary.

Three tags. The tag does not need to be literal bracket text, but it must be
**audible in the sentence**:

| Tag | Means | How it is written |
|---|---|---|
| **VERIFIED** | Checked this engagement against a named source. | State as fact, name the source and date. "The December closing balance of $12,345.67 agrees to the bank statement dated 31 December." |
| **FROM CLIENT MATERIAL** | Comes from something the client handed you. | Attribute it. "The workbook records $X. This has not been independently confirmed." |
| **NOT CHECKED** | Not examined, or the source could not be obtained. | Say so plainly. "The January card statement was not produced, so the year-end card balance is unconfirmed." |

**The tag must survive summarization.** A caveat on page 14 does not protect a
claim in the executive summary. The summary is what gets read, quoted, and
acted on. If a claim is too weak to carry into the summary with its
qualifier attached, delete it from the summary and state what is missing
instead.

**Banned unless the check actually ran:** "I confirmed," "I verified," "I
reconciled," "there are no," "nothing else was found," "the books are clean."
That last family is the trap, because it describes an examination. If the
examination did not happen, it is a false statement about your own process, and
the reader cannot audit it.

---

## Branch first: which engagement is this?

Decide before anything else. The evidence handling, the tone, and the
deliverable all change.

### INTERNAL AUDIT

The user owns the business or the books. The goal is accuracy, control, and a
clean set of questions for the bookkeeper or CPA. Nobody is a suspect. Errors
are assumed to be errors until something says otherwise.

- Working copies are fine. Formal chain of custody is optional but cheap.
- Output is a findings log plus a short memo of questions, worded so the
  bookkeeper can answer them without feeling accused.
- The bar for raising an item is lower, because raising a question costs little.
  But rule 1 still holds: a question is worded as a question.

**What governs is independence, not employment.** Internal audit is often
described as work done by employees of the organization. That definition is
too narrow and it fails for most small and mid-sized businesses, where the
books are kept by an outside bookkeeper and reviewed by the owner. What
actually matters is that whoever performs the review is **not reviewing their
own work** and can report without the subject of the review controlling the
report. Say who performed the review and who they answer to. If the reviewer
and the preparer are the same person, that is itself a control finding.

**Internal audit is continuous, not a year-end event.** Its advantage over the
annual close is timing: an error caught in month three can be corrected in
month three. Where the engagement is ongoing, set a cadence and say what each
pass covers.

**The six standing objectives.** Use these as the coverage checklist. State in
the report which you covered and which you did not, because an internal audit
that silently covers two of six reads as though it covered all six.

| Objective | What you actually do |
|---|---|
| **Error detection** | Catch and correct misstatement in-period rather than at year end |
| **Accounting system integrity** | Vouch entries to source documents in **both** directions, test accuracy and cutoff |
| **Control adequacy** | Test whether controls exist, are designed to work, and actually operated |
| **Asset protection** | Verify existence, ownership, valuation, and possession of assets |
| **Authorization** | Test that special transactions (asset sale, purchase, revaluation, related-party dealings, owner draws) were approved by someone with authority to approve them |
| **Fraud risk** | Identify where the business is exposed, not whether a named person did something |

Load `references/internal-audit-program.md` for the program: the vouching
procedure in both directions, control design versus operating effectiveness,
asset existence and ownership testing, authorization testing, segregation of
duties, and how to write a control finding that is useful rather than
accusatory.

### FORENSIC INVESTIGATION

There is a dispute, a suspicion, an insurance claim, a lawsuit, a departing
partner, or a counterparty. The work may be read by someone whose job is to
destroy it.

- **Chain of custody is mandatory from the first file.** See
  `references/evidence-and-custody.md`. Start it before you open anything.
- Preserve originals read-only. Work only on copies. Log every transformation.
- Output is built to the expert-report standard in
  `references/damages-and-expert-report.md`, whether or not testimony is
  currently contemplated. Build the file as if you will testify from it,
  because the decision to testify is made later and the file cannot be rebuilt.
- The bar for asserting an item is much higher, and the language is narrower.

### Hybrid

Common and legitimate: an internal audit finds something that changes the
posture. **The moment that happens, stop and say so.** Do not quietly continue
in internal mode. Tell the user that the work has crossed into a dispute
posture, that evidence handling needs to change, and that they may want counsel
involved before further steps. Then preserve what you have.

### The third thing, which this skill is not: an external audit

Keep this boundary clean, because clients blur it constantly and the words
sound interchangeable.

| | Internal audit / forensic work | External audit |
|---|---|---|
| **Question answered** | Are the controls sound, are the records right, where did the money go | Do the financial statements present fairly under the applicable framework |
| **Output** | Findings, recommendations, investigation report | A formal opinion, in a prescribed format |
| **Who relies on it** | Management, owners, the board, counsel | Shareholders, lenders, regulators, third parties |
| **Timing** | Continuous, or engagement-driven | A single annual cycle |
| **Scope set by** | Management or the engagement | The applicable statute and auditing standards |

**This skill never issues an audit opinion**, a review report, a compilation
report, or any other attest product. Those require a licensed CPA working
under professional standards, and they carry a liability the work here does
not. Say so in every deliverable.

**A widely repeated claim you should not accept at face value:** that every
legal entity is required to have an external audit. That is not true in the
United States for private companies as a general matter. An audit obligation
comes from a specific trigger, and the triggers are worth checking before
telling any owner they are non-compliant: SEC registration or public trading,
a lender or bond covenant, a franchise or license agreement, ERISA plan size,
a state nonprofit revenue threshold, a partnership or operating agreement that
requires one, or an investor side letter. **Check the trigger. Do not assume
the requirement exists, and do not assume it does not.** The loan documents
and the operating agreement are where it hides.

---

## Right-size the work

Not every request is an engagement. Forcing a full audit onto a one-line
question wastes the user's money and buries the answer.

- **Quick answer.** "What is this account?", "does this month tie out?", "is
  this invoice a duplicate?" Answer it, name what you looked at, and say it was
  a targeted look. No deliverable unless asked.
- **Focused review.** One period, one account, one question with teeth.
  Reconcile that scope properly, produce a short findings list, state the
  boundary of what you examined.
- **Full engagement.** All phases, all deliverables, evidence register,
  findings log, report.

Three things hold at every tier and are never dropped: **reconcile before you
assert**, **tag every claim**, and **state what you did not cover** so a quick
look is never mistaken for a complete one.

---

## Phase 0: Scope and the independence gate

Before touching data, settle these and write them down. They go into the report
verbatim later, so getting them right now saves a rewrite.

1. **Who is the client and what is the question?** "Review the books" is not a
   question. "Did the 2025 equity change have a basis consequence?" is.
2. **What period?** Name the exact date range. Then name the period *before*
   it, because you will need the prior-year closing balances (see Phase 2).
3. **What is out of scope?** Write it down. Scope creep in this work is how a
   two-day review becomes a month.
4. **What can you not do here?** You are not a licensed CPA, auditor, or
   attorney unless the user is one and says so. You do not issue an audit
   opinion, a review or compilation report, a valuation certification, or a
   legal opinion. Say this once, plainly, at the top of every deliverable.
5. **Conflicts.** In a dispute, ask who the parties are before reading their
   records.

### Determine the regulatory regime before you plan anything

**This comes before scoping, because it changes the scope, the standards, the
deliverable, and what has to happen if you find something.**

Ask whether the entity is an SEC registrant or preparing to become one,
receives federal awards, sponsors an employee benefit plan, is a regulated
financial institution, is a nonprofit above a state threshold, or is bound by a
contract that imposes a requirement.

Two failures are possible and both are common:

- **Imposing an obligation that does not exist.** Telling a private LLC it must
  comply with Sarbanes-Oxley, or must obtain an external audit, is wrong and it
  costs the owner real money. Most US private companies have **no statutory
  audit obligation at all**.
- **Missing one that does.** The obligation most often missed is contractual,
  not statutory, and it sits in the loan agreement or the operating agreement.
  A covenant requiring audited statements, a fidelity policy with a notice
  deadline after a discovered loss, a buy-sell requiring valuation on a
  triggering event. **Read those two documents.**

Where a regime does attach, apply it properly rather than approximately. Where
it does not, use the method in this skill and say plainly that it is method and
not obligation.

**In a public company the engagement is not private.** Fraud involving anyone
with a role in internal control is a certification and disclosure matter
regardless of amount, record destruction carries criminal exposure, and there
are defined escalation paths once a possible illegal act is identified. Say
this at the outset, not after a discovery.

Load `references/regulatory-regimes.md` for the determination gate and what
each regime actually requires.

Load `references/engagement-scoping.md` for the intake checklist, the document
request list, the risk-based planning method, and the standing limitations
paragraph.

### Choose the work by risk, not by habit

Where the engagement is a recurring or standing audit rather than a one-off
question, do not audit what is easiest to audit or what was audited last year.
Rank the business's exposures by **impact** and **likelihood**, and let the
ranking pick the work.

A useful default for what to do with each band:

- **High impact, low likelihood.** Audit the controls that are keeping the
  likelihood low, on the assumption that low likelihood is a *result* of those
  controls rather than a property of the world. If the controls have quietly
  stopped operating, the likelihood is not low any more and nobody knows it.
- **High or medium impact with high or medium likelihood.** Do not stop at
  confirming the exposure exists. Find the **root cause** and produce
  recommendations that act on the cause. A finding that names a symptom
  generates a repeat finding next cycle.
- **Low impact, low likelihood.** Say you are not covering it, and why.

### The plan is a hypothesis too, and it expires

Write the plan, then hold it loosely. **When what you find differs materially
from what you assumed while planning, stop and re-plan** rather than pushing
the original program through. Revise the risk assessment, revise the scope,
and say in the report that the scope changed and why.

Two practical consequences:

- Re-assess at least annually for a standing engagement, and refresh more often
  than that when the business is changing.
- Distinguish a **minor** scope change, which the person running the work can
  make, from a **major** one that changes cost, timing, or conclusions, which
  goes back to whoever authorized the engagement. Agree which is which at the
  start, in writing, or every change becomes an argument.

---

## Phase 1: Intake and evidence preservation

**Run this before reading anything substantive, in both postures.** It is
cheap, and it cannot be done retroactively.

1. **Inventory every file received.** Name, size, SHA-256, date received, who
   produced it, what it is.
2. **Preserve originals.** Never edit a file the client produced. Never insert
   rows into an exported ledger. Work on copies in a separate folder.
3. **Start the evidence register.** Run
   `scripts/evidence_register.py` on the intake folder. It hashes everything
   and writes the register plus a chain-of-custody log as XLSX.
4. **Note what is missing.** The document request list will not come back
   complete. The gaps are part of the finding set, and a gap you fail to record
   becomes a hole in the analysis that nobody can explain later.

For the custody rules, the transformation log, and the handling differences
between postures, load `references/evidence-and-custody.md`.

---

## Phase 2: Rebuild the data and reconcile it

This is the phase that produces real findings. Most engagements are won or lost
here, and the two moves below are the ones people skip.

### 2a. Normalize

Counterparty names, date formats, bank descriptors, sign conventions, account
codes. Build a **data dictionary** as you go and keep it as a workpaper. A
reviewer must be able to re-derive your numbers.

### 2b. Tie out to source

Reconcile the ledger to the bank and card statements, line by line, for the
whole period. Not a sample. Not the summary totals. Every ledger entry should
match a statement line, and every statement line should appear in the ledger.

`scripts/reconcile.py` does the matching and produces an exceptions list.

When a period reconciles fully, **record that it did, with the ending balance
and the statements used.** A clean reconciliation is a finding. It is also what
stops a future session from redoing three days of work.

### 2b-ii. Search for what is NOT there

Reconciliation tests what is recorded. **An omitted liability leaves no entry
to test**, so every procedure that starts from the ledger is blind to it. This
is the completeness assertion, and it is tested by working from the outside in.

The highest-yield procedure: take disbursements made **after** period end and
ask, of each one, what period the underlying obligation belongs to. A January
payment for December services is a December liability, and if it is not on the
December balance sheet it is unrecorded. `scripts/search_unrecorded_liabilities.py`
does the comparison.

The same script detects the recurring fixed-debit signature of a merchant cash
advance or factoring facility, which is debt that frequently appears nowhere on
the balance sheet because it is documented as a sale of receivables rather than
a loan.

Full treatment, including personal guarantees, trust-fund payroll taxes,
covenant testing, and the public records to search, is in
`references/liabilities-and-debt.md`.

### 2c. Roll forward from the prior year

**The most valuable single move in this skill, and the one almost nobody runs.**

The real problem is usually not inside the workbook you were handed. It is in
the seam between one year and the next. A workbook can tie internally, balance
perfectly, and still open with balances that silently contradict how the prior
year closed.

Pull the prior-period closing balance sheet and diff it against the current
period's opening ledger, account by account.

What you are hunting:

- A liability that closed one year and opens the next inside equity, or the
  reverse. This changes basis and can change whether later repayments to an
  owner are taxable.
- An expense in one year that reappears as an asset in the next.
- Any opening balance with no journal entry explaining how it got there.
- An account whose **name no longer describes what is in it.** An account
  called "Draws" holding a credit balance that increases equity is not a draw.
  A misnamed account is what makes a whole section unreadable, and it is what a
  lender or a tax preparer will misread.

`scripts/rollforward_diff.py` compares the two and flags every account that
moved without a documented entry.

---

## Phase 3: Exception testing

Run the analytics battery over the transaction table. The catalogue, the
thresholds, and what each test is actually evidence of are in
`references/exception-tests-and-schemes.md`. `scripts/exception_tests.py` runs
the standard set.

**Decide first whether you are examining the whole population or a sample, and
say which.** This skill defaults to the whole population, and that default is
right more often than the profession's habits suggest: a full year of bank
activity reconciles by script in minutes and produces a fact rather than an
inference. Sample only when the population genuinely cannot be handled, or when
the question is whether a control *operated*, which is a question about a rate.

**In a forensic posture, do not sample.** A sample cannot prove absence, and a
concealed transaction is precisely the item least likely to fall into a random
draw. If you did sample and a single exception appears, stop sampling and
examine the whole population: you are no longer estimating a rate, you are
investigating an item.

Selection methods, what drives sample size, how to read an exception found in a
sample, the assertions framework for saying what a test actually proves, and
the professional deficiency ladder are in
`references/sampling-and-assertions.md`.

Three rules govern this phase and they matter more than the test list.

**Every test needs a positive control before its output means anything.** A
duplicate-payment test that reports zero duplicates is telling you about the
test until you have fed it a known duplicate and watched it fire. This applies
hardest to negative results, because a false negative has no downstream catch:
nobody can discover the thing you failed to look for. Build a control row,
run it through, confirm the detector sees it, and say in the workpaper that
you did.

**Keep failures separate from findings.** If a data source was unavailable, a
file would not parse, or a query returned nothing because it was blocked, that
item is **not screened**. It never shares an output column with items that were
screened and cleared. Collapsing the two produces a report that says a
population was examined when it was not.

**An exception is an input to Phase 4, never an output of Phase 3.** Nothing
from this phase goes in front of the client until it has been through the
corroboration gate.

---

## Phase 3b: Build the picture

Exception tests produce a list. A list does not explain anything. Four analysis
modes turn scattered exceptions into something a non-accountant can follow, and
between them they are most of what makes forensic work legible.

- **Temporal.** Put everything on a timeline. When did the transactions
  happen relative to each other, to month end, to a board meeting, to a
  resignation, to a loan closing, to a demand letter? Sequence is frequently
  the whole finding, and it is the single most persuasive exhibit available
  because a reader needs no accounting training to read a timeline. Build flow
  diagrams for money movement: from whom, to whom, how much, what date.
- **Relational.** Map the entities, accounts, and people, and the links
  between them. Common ownership, shared addresses, shared signers, a vendor
  whose bank account matches an employee's. Label the links in plain words on
  the diagram, not in accounting terms.
- **Inferential.** Lay out the chain of reasoning from evidence to
  proposition, one link at a time, and mark which links are documented and
  which are inferred. **This is where the discipline lives.** An argument that
  does not distinguish its documented links from its inferred ones is the
  shape that gets an expert excluded.
- **Computational.** The spreadsheets, queries, statistical tests, and data
  mining that get you there. Version every script and dataset, record
  thresholds and parameters, and keep the run log. If the analysis cannot be
  re-run by someone else from your workpapers, it is not evidence.

**Transactions rarely have exactly one interpretation.** Write down the
competing readings of the same facts before you settle on one, and say why the
one you chose fits business reality better than the others. A reading that is
technically available but makes no commercial sense is not the answer, and a
reading you never considered is the one opposing counsel will lead with.

Detail and worked patterns are in `references/exception-tests-and-schemes.md`.

---

## Phase 3c: Interviews and inquiry

Records tell you what happened. People tell you why, and they frequently hand
you the document you could not find.

**What you do here:** prepare the question set, in order, with the supporting
document for each question identified; draft the written inquiry; and document
the answers you are given against the records.

**What you do not do:** conduct the interview. You are not in the room. Never
write up an interview you did not witness as though you did, and never
characterize someone's demeanor, credibility, or truthfulness from a summary
someone else handed you.

Practical rules that hold whoever asks the questions:

- **Ask the open question before the document question.** "Walk me through how
  a vendor gets set up" gets a real answer. "Why did you approve this invoice?"
  gets a defense.
- **Know the answer before you ask, where you can.** An inquiry is a test of
  consistency, not a fishing trip.
- **Record the answer as an assertion, not a fact.** "The manager states the
  transfers were reimbursements" is a record of what was said. It becomes a
  finding only when a document supports or contradicts it.
- **In a dispute posture, ask counsel before contacting anyone.** Interviews
  can carry legal consequences the accountant does not control, including
  privilege, employment, and witness-contact issues. Flag it and stop.

---

## Phase 4: The corroboration gate

**No item passes from exception to finding without clearing all five.** Write
the answers in the workpaper, not in your head.

1. **What exactly is the anomaly?** State it as a transaction, with dates,
   amounts, accounts, and counterparties. If you cannot state it in one
   sentence with numbers, you do not understand it yet.
2. **What source document did you inspect?** Name the file and the page or
   line. "The ledger" is not a source for a ledger defect.
3. **What is the innocent explanation, and did you rule it out?** Write the
   best case against your own finding, then answer it. A promotional zero-rate
   balance explains missing interest. A first statement cycle explains a
   missing first payment. A same-day round trip between related entities
   explains a pair of matching amounts. If you did not go looking for the
   innocent explanation, you have not tested the finding.
4. **Can you show it?** A finding a reader cannot follow is not usable. Name
   the exhibit: the statement line, the ledger extract, the flow diagram.
5. **What is the consequence?** Dollars, tax effect, control gap, or reporting
   effect. An anomaly with no consequence is a note, not a finding.

Anything that fails a gate goes to **open questions**, worded as a question,
and it stays there. Do not soften a failed gate into a maybe because you
already spent time on the item. Effort spent is not evidence.

---

## Phase 5: Quantification

Only when the engagement calls for a number. Pick the model that answers the
actual theory of the case, not the one that is easiest to compute. Tie every
input to a source. State sensitivity ranges in the body of the report, not in
an appendix nobody reads.

Load `references/damages-and-expert-report.md` for the models, when each one
fits, the mitigation and capacity tests, and the sensitivity presentation.

---

## Phase 6: Report and deliverables

Every engagement produces at minimum:

| Deliverable | Format | Script |
|---|---|---|
| Findings log, severity ranked | XLSX | `scripts/build_findings_xlsx.py` |
| Evidence register and chain of custody | XLSX | `scripts/evidence_register.py` |
| Report or memo | DOCX | `scripts/build_report_docx.py` |
| Reconciliation workpapers | XLSX | `scripts/reconcile.py` |

Markdown is never a final deliverable.

The report structure, the severity scale, the standing limitations paragraph,
the writing rules, and the file naming and routing conventions are in
`references/deliverables.md`. Read it before generating anything.

Two writing rules worth stating here because they are violated constantly:

- **Write for a reader who is not an accountant.** A judge, an insurer, a
  spouse, a partner. Short sentences. One idea per sentence. The plainest
  precise word. Terms of art stay when they are precise; ordinary ideas do not
  get dressed up.
- **The executive summary carries the same provenance as the body.** See rule 3.

---

## Phase 7: Adversarial self-review

**Do not skip this.** A deliberate second pass over your own output finds more
than the original pass did, and it costs a fraction. Re-derive each claim as
though someone else wrote it.

Read the **summary sentences hardest.** That is where unearned confidence
collects, because nothing about an over-claim fails. Specifically hunt:

- Any claim whose qualifier was dropped on the way into the summary.
- Any count you wrote without enumerating. If a count is not load-bearing,
  delete it rather than totalling by eye.
- Any negative claim ("no other instances") whose detector never ran a control.
- Any sentence naming a person next to a word like scheme, diversion, or
  concealment.
- Any number quoted from a source you did not open this engagement.

Going in expecting to find yourself wrong is its own bias. Sometimes the
re-derivation upgrades a finding. The point is to re-derive, not to retract.

---

## Reference files: load on demand, not all at once

| Load when | File |
|---|---|
| **Before scoping anything**: which obligations attach to this entity, public company requirements, contractual triggers | `references/regulatory-regimes.md` |
| Starting any engagement: intake, document request list, risk-based planning, limitations language, when to hand off | `references/engagement-scoping.md` |
| Any forensic posture, or any file that may be produced in a dispute | `references/evidence-and-custody.md` |
| Internal posture: vouching, control testing, asset verification, authorization, compliance, value for money | `references/internal-audit-program.md` |
| The population is too large to examine in full, or you need to say precisely what a test proves, or rank a control failure in professional terms | `references/sampling-and-assertions.md` |
| Running the tie-out or the prior-year roll forward | `references/reconciliation-and-rollforward.md` |
| The question involves what the business **owes**: hidden debt, unrecorded liabilities, guarantees, covenants, or collectability of what is owed to it | `references/liabilities-and-debt.md` |
| Exception testing, the four analysis modes, and what each scheme leaves behind | `references/exception-tests-and-schemes.md` |
| Quantifying a loss, or writing anything that may reach a court | `references/damages-and-expert-report.md` |
| Choosing or evaluating software, or asked what tools this work uses | `references/tooling.md` |
| Setting up or evaluating an internal audit **function**: charter, independence, quality program. **Skip this for a single engagement.** | `references/audit-function-governance.md` |
| Before generating any file | `references/deliverables.md` |

---

## Scripts

Python, `openpyxl` and `python-docx` only. No other dependencies, deliberately,
so the method runs on any machine for any business. Run `python <script>
--help` for usage. Every script writes via a temporary file and never
overwrites an input.

| Script | Does |
|---|---|
| `audit_common.py` | Shared helpers. Not run directly. |
| `evidence_register.py` | Hashes an intake folder, writes the evidence register, chain-of-custody log, transformation log, and requested-not-produced log. `--verify` re-checks the files against the register and reports UNCHANGED / CHANGED / MISSING / NEW. |
| `reconcile.py` | Matches a ledger against statement lines in both directions. Separates matched, ledger-only, statement-only, and ambiguous. |
| `rollforward_diff.py` | Diffs prior-period closing balances against current-period opening balances and pairs equal-and-opposite moves as possible reclassifications. |
| `exception_tests.py` | Runs the analytics battery. **Every test carries a positive control**, and a test whose control fails is reported BROKEN with its population marked NOT SCREENED. |
| `search_unrecorded_liabilities.py` | Works from outside the ledger inward. Finds post-period payments with no liability recorded at period end, and detects the recurring fixed-debit signature of a merchant cash advance or factoring facility. Keeps one-off candidates and facility remittances in separate totals. |
| `build_findings_xlsx.py` | Severity-ranked findings log. **Holds back any row missing a provenance tag, a named source, or the alternative explanation**, onto a separate sheet. |
| `build_report_docx.py` | Report DOCX at the 12pt floor with the limitations paragraph inserted automatically. Stages the build so a locked destination cannot destroy it. |

Three of these enforce discipline rather than just producing output, and that
is deliberate: `exception_tests.py` will tell you a test is broken,
`build_findings_xlsx.py` will refuse to put an uncorroborated row in the
findings log, and `evidence_register.py --verify` will tell you the file you
are analyzing is not the file you were given.

---

## Hard stops: do not proceed, say so and wait

- About to call something fraud, theft, embezzlement, or a breach of duty.
- About to state a tax, legal, or regulatory consequence you have not verified
  against the current primary source this engagement.
- About to put a finding in a summary at a confidence its evidence does not
  support.
- About to edit, insert rows into, or overwrite a file the client produced.
- About to report a negative result from a detector that has not passed a
  positive control.
- The engagement has crossed from internal review into a dispute and the user
  has not been told.
- You have found something that suggests a crime, a regulatory reporting
  obligation, or a duty the user may personally owe. Say so plainly, in one or
  two sentences, and tell them it needs a lawyer or CPA. Do not advise on it
  and do not sit on it.

A hard stop is not a failure to be helpful. Naming what you cannot conclude is
the most valuable thing in the file.
