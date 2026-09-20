# Business Audit and Forensic Accounting

A Claude skill for examining a business's financial records and investigating
them forensically. It runs two postures:

- **Internal audit.** Your own books. Reconcile, test controls, vouch entries,
  verify assets, and produce a clean set of questions for the bookkeeper or
  CPA. Nobody is a suspect.
- **Forensic investigation.** Adversarial. Chain of custody, fund tracing,
  competing-hypothesis testing, loss quantification, and a report built to
  survive expert scrutiny.

It works for any business, any accounting system, any size.

---

## Why this exists

A general ledger is full of patterns that look like defects and are not.

Two identical deposits on one day look like a double posting. A missing month
of interest looks like a skipped accrual. A missing payment looks like a bill
nobody paid. Every one of those has an innocent explanation sitting in a
document nobody has opened yet.

Inventing a finding is the characteristic failure of this work, and it is worse
than missing one. It sends a bookkeeper chasing a transaction that was always
correct, it accuses a person who did nothing, and it destroys the credibility
of every real finding next to it.

This skill is built around stopping that.

---

## The three rules

**1. A pattern is a hypothesis, not a finding.** Nothing becomes a finding
until it is reconciled to a source document outside the ledger. A ledger cannot
corroborate itself. Anything that cannot be corroborated becomes an *open
question*, worded as a question.

**2. Never opine on intent, and never state a legal conclusion.** You can say
money moved and was not documented. You cannot say someone stole, defrauded, or
embezzled. Those are conclusions for a trier of fact, and stating one turns a
defensible workpaper into a liability.

**3. Every claim carries its provenance, and the tag survives into the
summary.** VERIFIED, FROM CLIENT MATERIAL, or NOT CHECKED, audible in the
sentence. A caveat on page 14 does not protect a claim on page 2.

---

## What is in it

### The skill

`skills/business-audit-forensics/SKILL.md` routes the engagement and carries
the phases: scoping, evidence preservation, reconciliation, exception testing,
building the picture, inquiry, the corroboration gate, quantification,
reporting, and an adversarial self-review.

### Reference files, loaded on demand

| File | Covers |
|---|---|
| `engagement-scoping.md` | Intake, document request list, risk-based planning, limitations language, when to hand off to a credentialed professional |
| `evidence-and-custody.md` | Chain of custody, transformation logs, working rules, admissibility in plain terms |
| `internal-audit-program.md` | Vouching in both directions, control design versus operation, segregation of duties, asset verification, authorization testing, compliance, value for money |
| `reconciliation-and-rollforward.md` | Two-directional tie-out, the prior-year roll forward, intercompany reconciliation, cutoff |
| `exception-tests-and-schemes.md` | The analytics battery, what each scheme leaves behind in the books, the four analysis modes, competing interpretations |
| `damages-and-expert-report.md` | Damages models, the expert standard, report structure, the language discipline |
| `tooling.md` | The software landscape, honestly tiered, with a standing warning that product names go stale |
| `audit-function-governance.md` | Charter, independence, risk-management boundaries, quality programs. Skip it for a single engagement. |
| `deliverables.md` | Formats, severity scale, findings log columns, writing rules, file handling |

### Scripts

Python, `openpyxl` and `python-docx` only. No other dependencies, so the method
runs on any machine without a licensed tool.

| Script | Does |
|---|---|
| `evidence_register.py` | Hashes an intake folder and writes the evidence register, chain-of-custody log, transformation log, and requested-not-produced log. `--verify` re-checks files against the register and reports UNCHANGED / CHANGED / MISSING / NEW. |
| `reconcile.py` | Matches a ledger against statement lines in **both** directions. |
| `rollforward_diff.py` | Diffs prior-period closing balances against current-period opening balances and pairs equal-and-opposite movements as possible reclassifications. |
| `exception_tests.py` | Runs the analytics battery. Every test carries a positive control. |
| `build_findings_xlsx.py` | Severity-ranked findings log. |
| `build_report_docx.py` | Report DOCX at a 12pt floor with the limitations paragraph inserted automatically. |

Three of them enforce discipline rather than just producing output, which is
the point:

- `exception_tests.py` injects a synthetic item each test **must** catch. A
  test whose control fails is reported **BROKEN** and its population is marked
  **NOT SCREENED**, never "clear". Tests that could not run at all are reported
  **NOT RUN**, kept separate from tests that ran and found nothing.
- `build_findings_xlsx.py` **refuses to put an uncorroborated row in the
  findings log.** A row missing its provenance tag, its named source document,
  or the alternative explanation it was tested against is moved to a separate
  sheet.
- `evidence_register.py --verify` exits non-zero when a source file is not what
  it was at intake, and **refuses to report at all** if it parsed zero rows,
  because a comparison against nothing looks identical to a clean result.

---

## Install

**Claude Code / Cowork, via the marketplace:**

Settings → Add marketplace → paste this repository URL → Sync → Install.

**Manually:** copy `skills/business-audit-forensics/` into `~/.claude/skills/`.

**Scripts:**

```bash
pip install openpyxl python-docx
```

---

## Quick start

```bash
cd skills/business-audit-forensics/scripts

# 1. Preserve the evidence BEFORE reading anything substantive
python evidence_register.py --input ./intake --output register.xlsx \
    --matter "2025 books review" --received-from "Bookkeeper"

# 2. Tie the ledger to the bank, both directions
python reconcile.py --ledger GL.csv --statement bank.csv \
    --output reconciliation.xlsx --window 3

# 3. The highest-yield procedure: prior close against current open
python rollforward_diff.py --prior TB_2024.csv --current TB_2025.csv \
    --output rollforward.xlsx

# 4. Exception battery, every test control-checked
python exception_tests.py --input GL.csv --output exceptions.xlsx \
    --round-threshold 1000 --approval-limit 5000

# 5. Findings log and report
python build_findings_xlsx.py --template findings.json
python build_findings_xlsx.py --input findings.json --output findings.xlsx
python build_report_docx.py --template report.json
python build_report_docx.py --input report.json --output report.docx

# Later: is what I am analyzing still what I was given?
python evidence_register.py --verify register.xlsx --input ./intake
```

Run `--help` on any script for the full options.

---

## What this is not

It does **not** issue an audit opinion, a review report, a compilation report,
or any other attest product. Those require a licensed CPA working under
professional standards.

It does not give legal advice, tax advice, or a valuation certification. It does
not conclude that anyone committed a crime.

A widely repeated claim worth not believing: that every legal entity is
required to have an external audit. That is not true for US private companies
as a general matter. An audit obligation comes from a specific trigger, such as
SEC registration, a lender covenant, a franchise agreement, ERISA plan size, or
a state nonprofit threshold. Check the trigger before telling an owner they are
non-compliant.

The skill names the handoff points explicitly, and the handoff is not a
failure. Work done properly here becomes what the credentialed professional
starts from, which is usually the expensive part of their engagement.

---

## A note on verification

This skill is opinionated about a thing that is easy to get wrong: stating
something as checked when it was not.

Where it quotes an external standard it carries the source and the date it was
checked, because rules are amended and product names go stale. It deliberately
contains **no statistics, salary figures, or benchmark percentages**, because a
number hardcoded into a reference file is a number that quietly rots and then
gets quoted as current. Where a benchmark is needed, the skill says where to go
and get one, and to date-stamp it.

Two examples of why that discipline earns its cost, both encountered while
building this:

- The IIA's internal audit framework was restructured. The 2024 Global Internal
  Audit Standards took effect 9 January 2025, and the five separately named
  mandatory elements of the previous framework no longer exist as separate
  entities. Material written before that, including a great deal currently
  published, uses vocabulary a generation behind.
- The best-known audit analytics product has had three owners in six years. ACL
  and Rsam rebranded as Galvanize in 2019, and Diligent completed its
  acquisition of Galvanize in April 2021. Articles published this year still
  name an owner that sold five years ago.

---

## Credits and license

MIT. Copyright Dina Farhat.

Content is an original synthesis. See `NOTICES.md`.
