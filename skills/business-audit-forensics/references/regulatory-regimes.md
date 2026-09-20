# Regulatory Regimes: Which Obligations Actually Attach

Load at Phase 0, before scoping. **Determine the regime before you plan the
work**, because it changes the scope, the standards, the deliverable, who is
entitled to rely on it, and what has to happen if you find a problem.

Two failures are possible here and both are common:

- **Imposing an obligation that does not exist.** Telling a private LLC it must
  comply with SOX, or must have an external audit, is wrong and it costs the
  owner real money.
- **Missing one that does.** A federal grant recipient, an employee benefit
  plan, a broker-dealer, or a company with a lender covenant has obligations
  the owner may not know about, and discovering one during the engagement is
  far better than discovering it during an examination.

**Ask the question. Do not assume in either direction.**

---

## The determination gate

Run these at intake. Each "yes" attaches a regime.

1. **Is the entity an SEC registrant, or does it have registered securities?**
   Publicly traded, or filing 10-K, 10-Q, 8-K, 20-F, or similar. → Public
   company regime, below.
2. **Is it preparing to register?** An IPO, a direct listing, or a SPAC
   transaction pulls the public-company control requirements forward, usually
   well before the filing.
3. **Does it receive federal awards?** Grants, subawards, or certain federal
   assistance above a threshold trigger a **Single Audit** under the federal
   Uniform Guidance, which is a different and more specific animal than a
   financial statement audit.
4. **Does it sponsor an employee benefit plan?** Retirement and welfare plans
   above a participant count require an **ERISA plan audit**, filed with Form
   5500. The threshold is participant-based and how participants are counted
   has changed. Verify it.
5. **Is it a regulated financial institution?** Banks and credit unions above
   asset thresholds carry **FDICIA** internal-control reporting.
   Broker-dealers, investment advisers, and insurers each carry their own
   examination and reporting regimes.
6. **Is it a nonprofit?** Many states require an audit or review above a
   revenue threshold, and the thresholds differ by state. Funders and grantors
   frequently impose their own, independent of the state.
7. **Does any contract require it?** This is the one that hides. See
   "Contractual triggers" below.
8. **None of the above?** Then there is very likely **no statutory audit
   obligation at all**, which is the normal position for a private LLC,
   partnership, or family business in the United States. Say so plainly.

---

## The public company regime

### What SOX actually requires

The Sarbanes-Oxley Act of 2002 is the centerpiece. The provisions that matter
for this work:

**Section 302 — certifications.** The CEO and CFO personally certify each
periodic report: that they reviewed it, that it does not contain material
misstatements or omissions, that the financial statements fairly present the
condition and results, and that they are responsible for disclosure controls
and have evaluated them. They also certify that they have disclosed to the
auditors and the audit committee any significant control deficiencies, material
weaknesses, and **any fraud involving management or employees with a
significant role in internal control** — regardless of amount.

That last clause is forensic. In a public company, fraud by anyone with a
control role is a disclosure matter even when the dollars are trivial.

**Section 404(a) — management's assessment.** Management must assess and report
on the effectiveness of internal control over financial reporting (ICFR).
**This applies to every filer.** There is no small-company exemption from
404(a).

**Section 404(b) — auditor attestation.** The registered public accounting firm
attests to and reports on ICFR effectiveness. **This is the part with
exemptions**, and the distinction between (a) and (b) is the single most
commonly confused point in this area:

- **Non-accelerated filers are exempt** from 404(b).
- **Emerging growth companies are exempt** from 404(b) for their EGC period
  under the JOBS Act.
- The SEC amended the accelerated filer definitions on **12 March 2020,
  effective 27 April 2020**, to exclude issuers with **public float under $700
  million and annual revenue under $100 million**, which removed 404(b) for a
  further band of smaller issuers. The transition thresholds for exiting
  accelerated status were raised from $50 million to $60 million, and for
  exiting large accelerated status from $500 million to $560 million, with a
  revenue test added.

*(Verified against sec.gov on 19 September 2026. **Thresholds and filer
definitions change. Confirm the current rule and the entity's current filer
status before relying on any figure above.** Filer status is determined as of a
measurement date and an entity can move between categories.)*

**Section 802 — record retention and destruction.** Creates criminal liability
for destroying, altering, or falsifying records with intent to obstruct an
investigation, and imposes retention requirements on audit workpapers. The
retention periods differ between the statute and SEC rule, so **verify the
applicable period rather than quoting one**.

This is directly forensic and it reinforces a hard stop already in this skill:
**never destroy, clean up, or reorganize records in a matter that is live or
reasonably anticipated.** In a public company that exposure is criminal, not
merely procedural.

**Section 806 and Section 1107 — whistleblowers.** Protection from retaliation
for employees who report suspected fraud, and criminal liability for
retaliating. If an engagement originates from an internal report, how the
reporter is treated is itself a live issue. Flag it to counsel.

**Exchange Act Section 10A — illegal acts.** Where an auditor becomes aware of
information indicating a possible illegal act, a defined escalation path
follows: to management, to the audit committee, and in some circumstances to
the board and onward to the Commission. **Verify the current requirements and
the trigger.** The practical point for this skill is that in a public-company
engagement, discovery is not a private matter between you and the client, and
you must say so before proceeding rather than after.

### ICFR and the control framework

A 404 assessment is performed against a recognized control framework. In US
practice that is almost always **COSO's Internal Control — Integrated
Framework**, organized as five components, each supported by underlying
principles, all of which must be present and functioning:

1. **Control environment** — governance, integrity, competence, accountability
2. **Risk assessment** — objectives, identifying and analyzing risk, including
   **fraud risk** explicitly
3. **Control activities** — the controls themselves, including over technology
4. **Information and communication** — quality information, internal and
   external communication
5. **Monitoring** — ongoing and separate evaluations, and reporting deficiencies

**Verify the current framework version and its principle count** before citing
it. Note the fraud-risk component: assessing fraud risk is a required part of
the framework, not an optional extra.

### Which auditing standards govern

- **Public issuers:** PCAOB standards.
- **US private companies:** AICPA standards (the AU-C sections).
- **Internationally:** ISA, issued by the IAASB. **The United States does not
  use ISA**, and material citing ISA for a US engagement has confused the two.
- **Internal audit:** the IIA's Global Internal Audit Standards, which are a
  separate framework again. See `audit-function-governance.md`.

Do not cite a standard number from memory or from a secondary source.

### Disclosure when something is found

If a material weakness exists at period end, management cannot conclude ICFR is
effective, and the weakness is disclosed, together with remediation. A material
weakness is disclosed **whether or not** any actual misstatement occurred:
the test is reasonable possibility, not realized error.

Where fraud or a material error is found, there may be obligations around
current reporting, restatement, and audit committee involvement. **These are
securities-law questions.** State the facts you found and route the disclosure
question to counsel and the auditors. Do not advise on whether to file.

---

## Contractual and investor triggers on a private company

The most commonly missed category, because the obligation is in a document
nobody has read since closing.

- **Loan and credit agreements.** Frequently require audited or reviewed
  statements, delivery deadlines, financial ratio covenants, and sometimes
  specific control representations. Breach can accelerate the loan.
- **Investor agreements.** Preferred stock terms, side letters, and operating
  agreements often require audits, information rights, or board-level
  reporting.
- **Franchise agreements.** May require reporting on a defined basis and permit
  the franchisor to audit.
- **Government contracts.** Bring cost-accounting and audit-access clauses.
- **Insurance policies.** Fidelity and crime policies impose notice deadlines
  and proof-of-loss requirements after a discovered loss. **Missing a notice
  deadline can void recovery**, which makes it urgent the moment a loss is
  suspected.
- **Buy-sell and partnership agreements.** Often require valuation or audit on
  a triggering event such as a death, a withdrawal, or a dispute.
- **Preparing for a sale or raise.** Not an obligation, but a buyer's quality
  of earnings review will test what the books will not, and control gaps become
  price adjustments.

**Read the loan agreement and the operating agreement.** They are the two
documents most likely to contain an obligation the owner does not know exists,
and they are always available.

---

## Applying this correctly

**When the regime attaches:** apply it properly. Use its vocabulary, test
against its framework, classify deficiencies on its ladder, and say which
standard governs.

**When it does not:** do not apply it, and do not imply it. The methodology in
this skill still works, because scoping to risk, testing design and operation,
corroborating before asserting, and documenting so a reviewer can re-perform is
good practice at any size. That is method, not obligation.

**State the determination in the report.** One sentence near the front:

> The Company is a privately held limited liability company. It is not an SEC
> registrant and is not subject to Sarbanes-Oxley Section 404. The procedures
> described here were performed at the owner's request and are not an audit
> under any professional standard. The credit agreement dated [date] requires
> [X]; compliance with that requirement was [not] within the scope of this
> work.

That paragraph prevents both failures at once. It stops a reader assuming
obligations that do not exist, and it names the contractual ones that do.

---

## Standing verification rule for this file

Everything in this file is a legal or regulatory claim, and every threshold,
exemption, filer definition, retention period, and framework version in it is
**subject to amendment**.

Two items were verified against sec.gov on 19 September 2026 and carry their
date in the text. **Everything else in this file is structure, not authority.**

Before stating any of it to a client, in a report, or in correspondence:
confirm it against the primary source for the current period, and confirm the
entity's own current status. If you cannot verify it in the moment, say "this
needs to be confirmed against the current rule" rather than stating it. That
answer is complete and it is safe. A confident wrong answer about a securities
obligation is not recoverable.
