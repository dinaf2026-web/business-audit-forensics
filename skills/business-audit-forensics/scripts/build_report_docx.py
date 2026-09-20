"""Build the audit or investigation report as a .docx from a report JSON.

Usage:
    python build_report_docx.py --template report.json
    python build_report_docx.py --input report.json \\
        --output "AUDIT - Acme Holdings 2025 books review (19-09-2026).docx"

Formatting is fixed at the house standard: Arial, 12pt floor everywhere
including tables, 8pt paragraph spacing, no em dashes. The standing
limitations paragraph is inserted automatically and cannot be omitted, only
edited.

The file is built to a staging path and copied to the destination, so a
destination locked by a word processor does not destroy the build.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

FONT = "Arial"
BODY = Pt(12)
SPACE_AFTER = Pt(8)

DEFAULT_LIMITATIONS = (
    "This work is an examination of the records identified in this report. It "
    "is not an audit, review, or compilation conducted under professional "
    "auditing or accounting standards, and it expresses no opinion on the "
    "financial statements taken as a whole. It is not legal advice, tax "
    "advice, or a valuation opinion. Conclusions that depend on law, tax "
    "treatment, or the interpretation of a contract should be confirmed with a "
    "qualified professional before being acted on. Findings are limited to the "
    "records produced and the period examined. Records requested and not "
    "produced are identified in the Scope and Limitations section."
)

TEMPLATE = {
    "title": "AUDIT - Matter name books review (dd-mm-yyyy)",
    "subtitle": "Prepared for: ",
    "prepared_by": "",
    "date": "",
    "assignment": "State, word for word, who engaged you, when, and what you "
                  "were asked to determine.",
    "scope": {
        "period": "1 January 2025 through 31 December 2025",
        "records_examined": [
            "General ledger, 2025",
            "Bank statements, account ending 0000, all twelve months",
        ],
        "records_requested_not_produced": [
            "January 2026 credit card statement. Without it the 31 December "
            "2025 card balance cannot be confirmed."
        ],
        "assumptions": [
            "Amounts are stated on the cash basis unless noted."
        ],
        "not_covered": [
            "Payroll tax compliance was not examined."
        ],
    },
    "background": "The business, the parties, and the events. Plain narrative.",
    "methodology": [
        "Reconciled the ledger to the bank statements line by line for the "
        "full period, in both directions.",
        "Compared the prior period closing balance sheet against the current "
        "period opening ledger, account by account.",
        "Ran the exception battery over the transaction population. Each test "
        "carried a positive control; control results are in the workpapers.",
    ],
    "what_reconciled": [
        "State plainly what tied out. A report containing only problems "
        "misrepresents the records and hides what was actually covered."
    ],
    "findings": [
        {
            "id": "F-001",
            "severity": "HIGH",
            "heading": "Short factual heading, no characterization of intent",
            "body": "Condition, criteria, cause, effect. State the transaction "
                    "with dates, amounts, accounts and counterparties.",
            "provenance": "VERIFIED. Bank statement dated 31 December 2025, "
                          "item E-014.",
            "alternative": "The innocent explanation tested, and how it was "
                           "ruled out.",
        }
    ],
    "open_questions": [
        "Worded as questions. These did not clear the corroboration gate."
    ],
    "quantification": {
        "model": "",
        "why_this_model": "",
        "result": "",
        "sensitivity": "",
    },
    "recommendations": [
        "Specific, assigned, dated."
    ],
    "limitations": DEFAULT_LIMITATIONS,
}


def style_document(doc):
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = BODY
    normal.paragraph_format.space_after = SPACE_AFTER


def para(doc, text, size=12, bold=False, italic=False, align=None, style=None):
    p = doc.add_paragraph(style=style)
    run = p.add_run(text or "")
    run.font.name = FONT
    run.font.size = Pt(max(size, 12))
    run.bold = bold
    run.italic = italic
    p.paragraph_format.space_after = SPACE_AFTER
    if align is not None:
        p.alignment = align
    return p


def heading(doc, text, size=15):
    return para(doc, text, size=size, bold=True)


def bullets(doc, items):
    for item in items or []:
        p = doc.add_paragraph(style="List Bullet")
        run = p.add_run(str(item))
        run.font.name = FONT
        run.font.size = BODY
        p.paragraph_format.space_after = SPACE_AFTER


def build(data, out_path):
    doc = Document()
    style_document(doc)

    para(doc, data.get("title", "Report"), size=17, bold=True)
    if data.get("subtitle"):
        para(doc, data["subtitle"], size=12)
    meta = []
    if data.get("prepared_by"):
        meta.append("Prepared by: %s" % data["prepared_by"])
    if data.get("date"):
        meta.append("Date: %s" % data["date"])
    if meta:
        para(doc, "   ".join(meta), size=12, italic=True)

    heading(doc, "1. Assignment")
    para(doc, data.get("assignment", ""))

    heading(doc, "2. Scope and limitations")
    scope = data.get("scope", {}) or {}
    if scope.get("period"):
        para(doc, "Period examined: %s" % scope["period"], bold=True)
    if scope.get("records_examined"):
        para(doc, "Records examined:", bold=True, size=13)
        bullets(doc, scope["records_examined"])
    if scope.get("records_requested_not_produced"):
        para(doc, "Requested and not produced:", bold=True, size=13)
        bullets(doc, scope["records_requested_not_produced"])
    if scope.get("assumptions"):
        para(doc, "Assumptions:", bold=True, size=13)
        bullets(doc, scope["assumptions"])
    if scope.get("not_covered"):
        para(doc, "Not covered by this work:", bold=True, size=13)
        bullets(doc, scope["not_covered"])

    para(doc, data.get("limitations") or DEFAULT_LIMITATIONS, italic=True)

    if data.get("background"):
        heading(doc, "3. Background")
        para(doc, data["background"])

    heading(doc, "4. Methodology")
    bullets(doc, data.get("methodology"))

    if data.get("what_reconciled"):
        heading(doc, "5. What reconciled")
        bullets(doc, data["what_reconciled"])

    findings = data.get("findings") or []
    heading(doc, "6. Findings")
    if not findings:
        para(doc, "No findings.")
    for f in findings:
        para(doc, "%s  [%s]  %s" % (f.get("id", ""), f.get("severity", ""),
                                    f.get("heading", "")), size=13, bold=True)
        para(doc, f.get("body", ""))
        if f.get("provenance"):
            para(doc, "Provenance: %s" % f["provenance"], size=12, italic=True)
        if f.get("alternative"):
            para(doc, "Alternative explanation considered: %s" % f["alternative"],
                 size=12, italic=True)

    if data.get("open_questions"):
        heading(doc, "7. Open questions")
        para(doc, "These could not be resolved from the records produced. They "
                  "are stated as questions and are not findings.")
        bullets(doc, data["open_questions"])

    q = data.get("quantification") or {}
    if any(q.values()):
        heading(doc, "8. Quantification")
        if q.get("model"):
            para(doc, "Model used: %s" % q["model"], bold=True)
        if q.get("why_this_model"):
            para(doc, "Why this model, and alternatives rejected: %s"
                 % q["why_this_model"])
        if q.get("result"):
            para(doc, "Result: %s" % q["result"], bold=True)
        if q.get("sensitivity"):
            para(doc, "Sensitivity: %s" % q["sensitivity"])

    if data.get("recommendations"):
        heading(doc, "9. Recommendations")
        bullets(doc, data["recommendations"])

    staged = os.path.join(tempfile.gettempdir(),
                          "report_build_%d.docx" % os.getpid())
    doc.save(staged)

    out_path = os.path.abspath(out_path)
    parent = os.path.dirname(out_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    try:
        shutil.copyfile(staged, out_path)
        os.remove(staged)
        return out_path, None
    except PermissionError:
        return None, staged


def check_style(data):
    """Warn on the two house-style rules that are easiest to break."""
    warnings = []
    blob = json.dumps(data)
    if "—" in blob:
        warnings.append("Em dash found. Use commas, periods, or restructure.")
    return warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input")
    ap.add_argument("--output")
    ap.add_argument("--template")
    args = ap.parse_args()

    if args.template:
        path = os.path.abspath(args.template)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(TEMPLATE, fh, indent=2)
        os.replace(tmp, path)
        print("Template written: %s" % path)
        return 0

    if not args.input or not args.output:
        ap.error("--input and --output are required unless --template is used")
    if not os.path.isfile(args.input):
        raise SystemExit("File not found: %s" % args.input)

    with open(args.input, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    for w in check_style(data):
        print("STYLE: %s" % w)

    out, staged = build(data, args.output)
    if out:
        print("Report written: %s" % out)
        print("Open it only once the work has settled. Opening it is what makes "
              "it unwritable.")
        return 0

    print("DESTINATION LOCKED. The build succeeded and is staged at:")
    print("  %s" % staged)
    print("Close the document in your word processor and re-run to promote it.")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
