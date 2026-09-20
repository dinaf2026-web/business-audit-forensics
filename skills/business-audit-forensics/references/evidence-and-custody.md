# Evidence Handling and Chain of Custody

Load for any forensic posture, and for any internal audit that might later
become one. The work here is invisible in the report until someone challenges
it, and then it is the most important page in the file.

You cannot do this retroactively. **Start it before opening the first file.**

---

## The governing idea

Chain of custody answers one question: **can you prove that what you analyzed
is what you were given, unchanged?**

If you cannot, then every finding built on it is arguable, no matter how good
the analysis was. The cost of doing it properly is a few minutes at intake. The
cost of not doing it is the whole engagement.

---

## Intake procedure

### 1. Receive and freeze

- Take delivery in a way that records the source: an email with attachments, a
  portal download with a receipt, a drive handed over with a signed note.
- **Copy everything into an `originals/` folder and never write to it again.**
  Set it read-only. Do not open documents from it; open the copies.
- Create `working/` for copies and `output/` for what you produce.

### 2. Hash everything immediately

SHA-256 every file at intake, before any analysis. Record the hash next to the
filename. This is the anchor for every later claim that a file is unchanged.

`scripts/evidence_register.py` does this and writes the register.

### 3. Record for each item

| Field | Why it matters |
|---|---|
| Item ID | A short stable reference you can cite in the report |
| Filename and path as received | The name frequently carries meaning, and it changes |
| SHA-256 | Proof of integrity |
| Size and file type | Catches truncation and format surprises |
| Date and time received | Sequencing, and it answers "when did you have this" |
| Received from | The person or system that produced it |
| How received | Email, portal, drive, direct export, scan |
| Description | What it actually is, in plain words |
| Period covered | The date range the document covers, not the date it was sent |
| Custody location | Where the original now sits |

### 4. Note what is missing

Gaps recorded at intake are evidence. Gaps discovered at report time are
embarrassment. A statement series missing one month, a ledger that starts
mid-year, a card with no January statement: write it down when you notice it.

---

## The transformation log

Every time data changes shape, log it. This is what makes your analysis
reproducible, and reproducibility is the practical meaning of "reliable
method."

Log: what you did, to which item, with what tool and version, with what
parameters, when, and what came out. Keep the script or query itself as a
workpaper, not just a description of it.

Things that count as transformations and get logged:

- Converting a PDF to text or a table
- Exporting or re-exporting from an accounting system, with the report
  parameters used
- Normalizing names, dates, or amounts
- Merging, joining, or deduplicating datasets
- Filtering or excluding rows, **including exclusions meant to reduce noise**
- Any manual correction, with the reason

**Exclusions deserve special attention.** A filter added to cut clutter is part
of the instrument. Run your control through the filtered dataset, not the raw
one, or a filter will hide the very item you are looking for and report it as
absent.

---

## Working rules

**Never modify a file the client produced.** Not to fix a typo, not to add a
column, not to insert a correcting entry. If an adjustment is needed, it goes
in a clearly labelled block **outside** the exported data, marked as not being
part of the original record. Inserting a row into an export makes it look like
the accounting system produced something it never produced, and it silently
breaks any running-balance formula in the sheet.

**Keep derived work separate from source.** Anyone should be able to tell at a
glance which files came from the client and which you created.

**Version everything you produce.** Dated filenames, kept, not overwritten. A
superseded version is part of the record of how the analysis developed.

**Re-hash before you rely on a file.** A hash taken at intake certifies a state
at intake. If time has passed, another session has run, or the machine has
slept, re-derive the hash at the moment of use rather than trusting the one you
wrote down. A hash check inside the script that is about to act is worth more
than one at the top of the day.

**Hash raw bytes.** Read in binary. A decoded round-trip through a text mode
can alter bytes and produce a false "this file changed."

**Two missing files are not a match.** A hash function that returns nothing for
an absent source and nothing for an absent destination will compare equal.
Confirm both files exist before comparing, and treat a missing file as a
failure.

---

## Handling by posture

| | Internal audit | Forensic |
|---|---|---|
| Originals | Copy and work on copies | Preserve read-only, formally logged |
| Hashing | Recommended | Mandatory, at intake and before use |
| Transformation log | Keep the scripts | Full log, every step, retained |
| Access | Normal | Restricted, with a check-in and check-out record |
| Retention | Per engagement | Until the matter closes, then per counsel's instruction |

**Never destroy anything in a dispute posture.** Once litigation is reasonably
anticipated, deletion of relevant records can carry serious consequences
independent of the underlying dispute. If the user asks you to delete, clean
up, or reorganize records in a matter that is live or threatened, **stop and
tell them to speak to counsel first.** This is a hard stop.

---

## Digital sources

- **Exports beat screenshots.** An export from the accounting system with the
  report parameters recorded is reproducible. A screenshot is not.
- **Record the export parameters.** Date range, basis (cash or accrual),
  accounts included, filters. The same report run with different parameters
  gives different numbers, and "the P&L" is not a specification.
- **Statements from the bank beat statements from the client.** A PDF the
  client assembled is a representation of a statement. Where it matters, get
  the download from the institution.
- **A scanned document may have no text layer at all.** Before concluding a
  term does not appear in a PDF, print the extracted character count. Zero
  characters means the extraction failed, not that the phrase is absent.
- **Preserve metadata where it may matter.** Creation and modification dates,
  author, revision count. For office documents, the internal properties often
  answer "who last touched this" when nothing else does. Note that a document
  with no such properties cannot answer that question, and say so rather than
  inferring from file size or date.

---

## Admissibility, in plain terms

You are not the one who decides what gets admitted. What you control is whether
your work gives a court a reason to exclude it. The practical requirements:

- **The record is what it claims to be.** Custody and hashing carry this.
- **The method is reliable and was applied reliably.** The transformation log
  and reproducible scripts carry this.
- **The analysis can be re-performed by someone else.** Workpapers,
  parameters, and the data dictionary carry this.
- **The reasoning is transparent.** Assumptions stated, limits stated,
  alternatives considered.

For the expert-testimony standard and how a report is structured to meet it,
see `damages-and-expert-report.md`.
