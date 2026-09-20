# Deliverables

Load before generating any file.

---

## Formats

| Deliverable | Format |
|---|---|
| Report, memo, letter | `.docx` |
| Findings log, evidence register, schedules, workpapers | `.xlsx` |
| Exhibits for a court or insurer | `.pdf`, generated from the source |

**Markdown is never a final deliverable.** It is fine as an intermediate.

---

## Formatting standards

Apply these explicitly. Do not accept library defaults, and this applies to
spreadsheets as much as documents.

- **Body text, table cells, bullets, notes, captions, sources: 12pt minimum.
  Never smaller.**
- Column headers and minor sub-headers: 12pt bold
- Sub-headers: 13 to 14pt bold
- Section headings: 15pt bold
- Title: 16 to 17pt bold
- Paragraph spacing: 8pt after
- Font: Arial unless the engagement specifies otherwise

**Never shrink below 12pt to make content fit.** Widen columns, go landscape,
or split the table. A schedule that has to be squinted at will not be read, and
a 9pt exhibit reads as though it is hiding something.

---

## Writing rules

- Short sentences. One idea per sentence.
- The plainest precise word. Terms of art stay where they are precise; ordinary
  ideas do not get dressed up.
- **No em dashes.** Use commas, periods, or restructure.
- **Dates in prose take a comma after the year, including attributive.** "the
  July 7, 2025, transfer", "On July 7, 2025, the funds moved." Drop the closing
  comma only where other punctuation ends the clause. No comma in month-year
  ("July 2025") or day-month-year ("7 July 2025").
- Define every term on first use.
- Numbers: consistent formatting, thousands separators, currency stated,
  and say whether figures are rounded and to what.

---

## Severity scale for findings

Rank everything. A log where every row is important is a log nobody acts on.

| Severity | Meaning |
|---|---|
| **Critical** | Material money at risk or already gone, an unrecorded obligation, a covenant breach, or a filing that is wrong. Needs action now. |
| **High** | Significant control failure, material misstatement, or an undocumented transaction of size. Action this cycle. |
| **Medium** | Control weakness or accuracy issue with a bounded effect. Action planned. |
| **Low** | Housekeeping, presentation, efficiency. |
| **Open question** | Could not be resolved from records produced. **Stated as a question, never as a defect.** |

**Open question is a real category and it is used a lot.** Anything that fails
the Phase 4 corroboration gate lands here. It is not a weaker finding; it is a
different thing.

---

## Findings log columns

Minimum set. `scripts/build_findings_xlsx.py` produces this.

| Column | Notes |
|---|---|
| ID | Stable reference, cited in the report |
| Severity | From the scale above |
| Category | Control, accuracy, documentation, authorization, compliance, valuation |
| Finding | One sentence, factual, no characterization of intent |
| Condition | What is, factually |
| Criteria | What should be, and the source of that expectation |
| Cause | Why the gap exists, usually structural |
| Effect | Consequence, quantified where possible |
| Amount | Dollars at issue, or blank |
| Evidence | Item IDs from the evidence register |
| Provenance | VERIFIED / FROM CLIENT MATERIAL / NOT CHECKED |
| Source examined | The actual document, named |
| Alternative explanation considered | What you ruled out, and how |
| Recommendation | Specific, assigned, dated |
| Status | Open, in progress, resolved, accepted risk |

The **Provenance** and **Alternative explanation considered** columns are what
separate this from a list of suspicions. Do not drop them to save width.

---

## Report structure

For a full report, use the structure in `damages-and-expert-report.md`.

For a short internal memo, the minimum is:

1. What you were asked and what you examined, with the period
2. **Scope and limitations**, near the front
3. What reconciled cleanly, stated positively
4. Findings, ranked
5. Open questions, as questions
6. Recommendations
7. The standing limitations paragraph from `engagement-scoping.md`

**Report what reconciled.** A report containing only problems misrepresents the
state of the records and denies the bookkeeper credit for what is right. It
also tells the reader what was actually covered.

---

## Questions for a bookkeeper or accountant

When output goes to the person who prepared the records, the wording decides
whether you get an answer or a defense.

- **Ask, do not assert.** "The 2024 balance sheet shows this as a liability and
  the 2025 ledger opens with it in equity. Can you point me to the entry behind
  that, so I can follow it?"
- **Give them the reference.** Account, date, amount, and which document you
  are looking at. Making them hunt wastes their time and yours.
- **Lead with what tied out.** It is true, and it establishes that you actually
  looked rather than skimmed for problems.
- **Say what you need and by when**, and say which items are blocking.
- **Separate errors from questions.** An arithmetic error and an undocumented
  reclassification are different conversations.
- **Never put a characterization of motive in writing to a preparer.** If the
  matter ever turns adversarial, that memo is discoverable and it was written
  before the facts were in.

---

## Marking up someone else's workbook

Sometimes the cleanest delivery is their own file with your annotations.

- **Never insert rows into exported data.** It makes the export look like the
  accounting system produced something it did not, and it breaks running-balance
  formulas. Put proposed adjustments in a clearly labelled block **below** the
  export, marked "ADJUSTMENT NOT YET IN THE ACCOUNTING SYSTEM."
- Small controlled statements (a summary P&L or balance sheet) can take an
  in-place adjustment, but then **rewrite the affected sum ranges by hand** and
  verify the totals.
- Use a distinct colour and a legend explaining it.
- **Prove the formulas still compute.** Most spreadsheet libraries write
  formulas without calculating them, so a saved file can contain correct
  formulas and no values. Convert the saved file with a headless spreadsheet
  application and read it back with cached values to confirm the real computed
  numbers. "It saved without error" is not proof the sheet is right.

---

## Building and delivering files

- **Build to a staging folder, then copy to the destination.** Do not write
  directly to the final path. A revision almost always follows delivery, and a
  document opened in a word processor is locked against rewriting.
- **Open the file for the user only once, when the work has settled.** Opening
  it is the act that makes it unwritable.
- **Never overwrite a file you have not read.** Never delete a staging folder
  in the same operation that might fail; clean up only after a copy succeeds.
- **Verify the effect, not the exit code.** After any file operation, list the
  target and compare hashes. A command that returns success is reporting that
  it did not crash.
- **Never report a copy as done without comparing hashes**, and treat a missing
  file as a failure rather than a match.

---

## File naming

`LEADER - Description with normal spaces (dd-mm-yyyy).docx`

The LEADER is a short project or matter code. One hyphen after it, then a plain
description with ordinary spaces, then the date last in parentheses. No em
dashes, no underscores, no hyphen between every word.

`AUDIT - Acme Holdings 2025 books review findings (19-09-2026).xlsx`

Use the same title inside the document. **Take the date from the system clock,
not from a document you are continuing from**, because a resumed session
inherits the earlier date everywhere it looks.

For multi-session work, keep the same name and append a part number that counts
up, placed after the description and before the date. Never renumber earlier
parts and never restart at Part 1 when resuming.

---

## Confidentiality

Financial records are confidential, and in a dispute they may be subject to a
protective order.

- Do not upload client financial records to third-party conversion or analysis
  services without checking the terms and the engagement's confidentiality
  obligations. Convert locally where it matters.
- Do not include account numbers, tax identification numbers, or personal
  identifiers in a deliverable that does not need them. Mask to the last four.
- Where output may be filed or produced, ask whether it needs redaction before
  it leaves your hands.
- Say in the report who the deliverable is for and that it should not be
  distributed further without the client's agreement.
