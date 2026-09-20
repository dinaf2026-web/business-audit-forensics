# Software and Tooling

**Provenance warning, and it applies to this whole file.** Product names,
owners, and availability are recorded from general knowledge, **not verified
against vendor sites at the time you are reading this.** This market
consolidates hard: vendors get acquired, products get renamed, and some are
discontinued. Categories are stable. Names are not.

**Before recommending, quoting, or buying any specific product, check it is
still sold, still named that, and still owned by who you think.** Never state a
price from this file. Never state a feature from this file as a fact about the
current version.

**A worked example of why.** The best-known audit analytics product has been
called three things in six years. ACL and Rsam rebranded as **Galvanize** in
May 2019, and **Diligent completed its acquisition of Galvanize on 7 April
2021** (verified against diligent.com, 19 September 2026). Articles published
recently still say "ACL, now Galvanize HighBond," which names an owner that
sold five years ago. If a current article is a generation stale, a reference
file written today will be too.

---

## The honest headline

**Most real forensic and audit work is done in a spreadsheet, a database, and a
scripting language.** The specialist packages are faster and produce better
audit trails, but they do not find anything a competent person with Excel, SQL,
and source documents cannot find. Nothing in this skill requires a licensed
tool.

Do not let a tool list become a reason not to start. The binding constraint is
almost always **getting the source documents**, not analyzing them.

---

## Tier 1: the stack that actually does the work

Available to anyone, no specialist licence.

| Tool | Used for | Notes |
|---|---|---|
| **Excel** with Power Query and Power Pivot | Everything. Reconciliation, pivots, exception tests, damages models. | Power Query is the underused part: it records transformation steps, which is exactly the reproducibility the evidence rules want. |
| **SQL** (SQLite, PostgreSQL, SQL Server) | Joining large transaction sets, tracing across accounts and entities | SQLite needs no server and travels with the case file |
| **Python** with pandas | Repeatable analysis, large files, anything you will run more than once | The scripts in this skill are plain Python |
| **R** | Statistical testing, Benford, sampling | Interchangeable with Python for this work |
| **Power BI** or **Tableau** | Timelines, flow visuals, exhibits for non-accountants | A clear chart moves a settlement conference more than a schedule does |
| **LibreOffice** (headless) | Recalculating workbooks written by a script | Python spreadsheet libraries generally do not compute formulas; a headless conversion does |

**A warning about spreadsheet-only work:** a spreadsheet has no audit trail
unless you build one. If the analysis matters, keep the transformation steps
(Power Query, a script, a documented procedure), not just the final sheet.

---

## Tier 2: audit data analytics (CAAT)

Purpose-built for testing whole populations rather than samples, with logging
built in. This is the traditional professional tier.

- **IDEA** (CaseWare) and **ACL / Analytics** (Diligent, formerly Galvanize)
  are the two long-standing names. Both do import from almost anything,
  population testing, duplicate and gap detection, Benford, sampling, and a
  command log that doubles as a transformation record.
- **Arbutus Analyzer** occupies the same space.
- **TeamMate Analytics** (Wolters Kluwer) ties analytics to workpapers.
- **Alteryx** for data preparation and blending where the inputs are messy and
  numerous.
- **MindBridge** and similar apply machine learning to flag anomalous entries
  across a full ledger.

**What you gain over Excel:** handling files too large for a spreadsheet, and a
command log that records exactly what was run. **What you do not gain:**
judgment. These tools produce exception lists, and an exception list is a
hypothesis set, not findings.

---

## Tier 3: audit management and workpapers

For running engagements rather than analyzing data.

- **CaseWare Working Papers**, **TeamMate+**, **AuditBoard**, **Workiva**,
  **Diligent HighBond**
- **Suralink** and similar for tracking document requests, which is a
  surprisingly large share of the actual work

Overkill for a single engagement. Useful when there is a recurring plan, a
findings population to track across cycles, and someone asking whether last
cycle's recommendations were implemented.

---

## Tier 4: digital forensics and e-discovery

Reach for these when the evidence is **devices and communications**, not
ledgers. Most engagements never need them.

- **Relativity**, **Everlaw**, **DISCO**, **Logikcull**, **Nuix** for document
  review and e-discovery at volume
- **EnCase**, **FTK**, **Magnet AXIOM**, **X-Ways** for disk and device imaging
- **Cellebrite** for mobile devices
- **Autopsy / The Sleuth Kit** as the open-source option

**Serious caution.** Imaging a device, accessing an account, or reviewing
someone's communications can carry legal consequences, including under computer
access and privacy statutes, employment law, and privilege rules. **This is not
an accounting decision.** Do not touch a device or a mailbox in a dispute
without counsel's instruction, in writing, and do not advise the client that it
is fine. Say it needs a lawyer.

---

## Tier 5: link analysis and visualization

For relationships between people, entities, and accounts.

- **IBM i2 Analyst's Notebook** is the traditional link-chart tool
- **Maltego**, **Linkurious**, **Neo4j** (graph database), **Gephi**
  (open source)
- For most matters, a hand-built diagram in a drawing tool is clearer than a
  generated graph. Generated network graphs look impressive and are frequently
  unreadable to the audience that matters.

---

## Tier 6: public records, asset tracing, and background

Where "where did the money go" becomes "what does this person own."

- Commercial aggregators: **TLOxp**, **Thomson Reuters CLEAR**,
  **LexisNexis Accurint**, **IRBsearch**. Access is generally restricted to
  users with a permissible purpose under privacy statutes.
- Free and public: **PACER** (federal courts), state court portals, Secretary
  of State business registries, **UCC** filings, county recorder and assessor
  records, **OpenCorporates**, **ICIJ Offshore Leaks**.
- **Permissible purpose is a real legal constraint**, not a formality. Running
  a person through a credit-header database without one can itself be a
  violation. Confirm the basis before searching a person.

For crypto: **Chainalysis**, **TRM Labs**, **Elliptic** commercially; public
block explorers for basic tracing. Following funds on-chain is mechanically
easier than bank tracing; attributing an address to a person is the hard part
and is where the commercial tools earn their price.

---

## Tier 7: getting the data out of documents

Usually the real bottleneck. Bank statements arrive as PDFs and the analysis
needs tables.

- **Adobe Acrobat** and **ABBYY FineReader** for OCR and export
- **Tabula**, **Camelot**, **pdfplumber**, **PyMuPDF** for extracting tables
  programmatically
- Statement-conversion services exist and will turn PDFs into CSV. **Read the
  terms before uploading client financial records to any third-party
  converter.** For a dispute or anything confidential, convert locally.

**Always reconcile the extracted table back to the document totals** before
analyzing it. Extraction silently drops rows, merges columns, and mangles
negative numbers in parentheses. If the extracted deposits do not sum to the
statement's stated total for the month, the extraction is wrong and every
downstream number is wrong with it.

**A scanned statement may carry no text layer at all.** Print the extracted
character count before concluding anything is absent from it.

---

## Valuation and damages modelling

- **Excel** is the workhorse and will remain so, because a damages model has to
  be transparent and auditable line by line. A model a reviewer cannot follow
  is worse than a simpler one that they can.
- **ValuSource** and the data products from **Business Valuation Resources**
  (transaction databases, cost of capital data) structure formal valuation
  reports and supply comparables.
- **Monte Carlo** add-ins exist for sensitivity work. Use them only where the
  inputs genuinely justify a distribution. A simulation built on guessed
  distributions produces false precision with a confidence interval attached,
  which is worse than a point estimate honestly labelled.

**Treat comparables data as evidence, and cite it.** A yardstick model stands
or falls on whether the comparator is defensible, and "industry data" with no
source is the first thing an opposing expert attacks.

---

## Practice and engagement management

A category worth knowing exists, because forensic engagements are multi-phase,
deadline-driven, and billed in detail that attorneys and courts actually read.

What the category covers: engagement and workflow templates, task assignment
and deadline tracking, multi-matter time capture with defensible descriptions,
itemized billing, secure document storage with per-person permissions,
e-signature for engagement letters, and budget-versus-actual tracking so scope
growth surfaces before it becomes a billing dispute.

Several vendors sell this. **Much of the writing you will find comparing them
is published by those vendors**, so read a recommendation and check who owns
the site. For a single engagement, a disciplined folder structure and the
evidence register in this skill do the same job.

**One feature is not optional in a dispute posture:** access control on the
document store, with a record of who opened what. That is the custody log, and
if the practice tool does not produce one, keep the register separately.

---

## Tax preparation software

You will encounter these because the client's returns were prepared in one, and
because prior-year returns are a source document for the roll-forward.

**Lacerte**, **ProConnect**, **ProSeries** (Intuit), **UltraTax** and
**GoSystem** (Thomson Reuters), **Drake**, **CCH Axcess** (Wolters Kluwer).

You rarely need to operate them. You need to be able to **read what came out of
them**, and to ask for the right thing: the as-filed return with all schedules
and statements, not a summary, and the prior-year comparison the software
generates.

---

## Tier 8: source accounting systems

You are usually reading exports from one of these. Knowing which changes what
you can ask for.

**QuickBooks** (Desktop and Online), **Xero**, **Sage** (50, Intacct),
**NetSuite**, **Microsoft Dynamics 365 Business Central**, **SAP**, **Oracle**,
**Odoo**, **Wave**, **FreshBooks**, **Zoho Books**.

Two things to ask of any of them:

1. **The audit trail or change log.** Most systems record who entered or
   modified a transaction and when, and most users never look at it. In a
   dispute this is frequently the single most valuable export available. Ask
   for it explicitly and by name, because it is not part of a standard
   financial statement package.
2. **The export parameters.** Basis (cash or accrual), date range, accounts
   included, filters. The same report run two ways gives two answers.

**Proprietary company files (for example QuickBooks `.qbw` and `.qbm`) cannot
be read without the software that made them.** Do not plan an analysis around
opening one directly. Ask for exports, or ask the holder to produce them.

---

## What this skill assumes

The scripts here assume **Tier 1 only**: Python, a spreadsheet, and source
documents as CSV, XLSX, or PDF. That is deliberate. It means the method runs on
any machine, for any business, without a licence, and it means the output is
reproducible by anyone who receives the workpapers.

If a licensed tool is available, use it for the heavy lifting and keep the
discipline in this skill. The tool changes the speed. It does not change the
corroboration gate.
