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
import re
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


class Sections(object):
    """Numbers sections as they are actually emitted.

    Numbers were hard-coded while several sections are conditional, so a
    report with no Background ran 1, 2, 4. A deliverable meant to be cited by
    section number, and to survive scrutiny, must not look like it is missing
    pages.
    """

    def __init__(self, doc):
        self.doc = doc
        self.n = 0

    def add(self, title):
        self.n += 1
        return heading(self.doc, "%d. %s" % (self.n, title))


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

    sec = Sections(doc)
    sec.add("Assignment")
    para(doc, data.get("assignment", ""))

    sec.add("Scope and limitations")
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

    # The standing paragraph is ALWAYS emitted. Previously any truthy value in
    # "limitations" replaced it, including a single space, while the docstring
    # promised it could be edited but not omitted. Custom text is appended.
    para(doc, DEFAULT_LIMITATIONS, italic=True)
    custom = (data.get("limitations") or "").strip()
    if custom and custom != DEFAULT_LIMITATIONS:
        para(doc, custom, italic=True)

    if data.get("background"):
        sec.add("Background")
        para(doc, data["background"])

    sec.add("Methodology")
    bullets(doc, data.get("methodology"))

    if data.get("what_reconciled"):
        sec.add("What reconciled")
        bullets(doc, data["what_reconciled"])

    findings = data.get("findings") or []
    sec.add("Findings")
    if not findings:
        # Asserting an absence requires having examined something. Previously
        # an empty or partly filled JSON produced "No findings." under a
        # heading with an empty Methodology section above it.
        if not (data.get("methodology") and data.get("what_reconciled")):
            raise SystemExit(
                "The report has no findings AND no methodology or "
                "what-reconciled content. Refusing to assert an absence of "
                "findings on the strength of an empty file. Fill in what was "
                "examined first.")
        para(doc, "No findings are reported in this document. The procedures "
                  "performed are described above; procedures not performed are "
                  "listed in Scope and limitations.")
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
        sec.add("Open questions")
        para(doc, "These could not be resolved from the records produced. They "
                  "are stated as questions and are not findings.")
        bullets(doc, data["open_questions"])

    q = data.get("quantification") or {}
    if any(q.values()):
        sec.add("Quantification")
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
        sec.add("Recommendations")
        bullets(doc, data["recommendations"])

    staged = os.path.join(tempfile.gettempdir(),
                          "report_build_%d.docx" % os.getpid())
    doc.save(staged)

    out_path = os.path.abspath(out_path)
    parent = os.path.dirname(out_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    # Copy to a sibling .tmp then os.replace, which is atomic. A direct
    # copyfile onto the destination truncates it first, so a dropped network
    # mount or a full volume mid-copy destroyed the previously delivered
    # report and left a corrupt .docx in its place. Only PermissionError was
    # being caught, so an OSError surfaced as a traceback after the damage.
    tmp_dest = out_path + ".tmp"
    try:
        shutil.copyfile(staged, tmp_dest)
        os.replace(tmp_dest, out_path)
    except PermissionError:
        for p in (tmp_dest,):
            try:
                os.remove(p)
            except OSError:
                pass
        return None, staged
    except OSError as exc:
        try:
            os.remove(tmp_dest)
        except OSError:
            pass
        raise SystemExit(
            "Could not write %s: %s\nThe previous file at that path is "
            "UNCHANGED. The build is staged at %s." % (out_path, exc, staged))
    try:
        os.remove(staged)
    except OSError:
        pass
    return out_path, None


def check_style(data):
    """Warn on the house-style rules that are easiest to break.

    THE BUG THIS FIXES: json.dumps defaults to ensure_ascii=True, which
    encodes U+2014 as the six characters \\u2014, so the em-dash test compared
    against a string that could never contain one. The check had never fired
    since it was written and its silence was being read as compliance.
    """
    warnings = []
    blob = json.dumps(data, ensure_ascii=False)
    if "—" in blob:
        warnings.append("Em dash found. Use commas, periods, or restructure.")
    if "–" in blob:
        warnings.append("En dash found. Use a plain hyphen or restructure.")
    # Month day, year needs a closing comma after the year, including
    # attributively: "the July 7, 2025, transfer".
    for m in re.finditer(
            r"\b(January|February|March|April|May|June|July|August|September|"
            r"October|November|December)\s+\d{1,2},\s+\d{4}(?=\s+[a-z])", blob):
        warnings.append(
            "Date needs a closing comma after the year: '%s'" % m.group(0))
    return warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input")
    mode.add_argument("--template")
    ap.add_argument("--output")
    ap.add_argument("--force", action="store_true",
                    help="Allow --template to overwrite an existing file.")
    args = ap.parse_args()

    if args.template:
        path = os.path.abspath(args.template)
        # REFUSE to overwrite. The docstring prescribes the same filename for
        # both modes, so re-running the documented --template line from shell
        # history replaced a fully populated report file with the two-section
        # starter. os.replace is atomic and unrecoverable, and there was no
        # prompt, no backup and no flag to forget.
        if os.path.exists(path) and not args.force:
            raise SystemExit(
                "%s already exists.\n"
                "Refusing to overwrite it with the starter template. If that "
                "file holds your work, this would destroy it. Choose another "
                "filename, or pass --force if you are certain." % path)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(TEMPLATE, fh, indent=2)
        os.replace(tmp, path)
        print("Template written: %s" % path)
        return 0

    if not args.output:
        ap.error("--output is required with --input")
    if not os.path.isfile(args.input):
        raise SystemExit("File not found: %s" % args.input)

    # utf-8-sig so a file saved from Notepad does not fail with
    # "Expecting value: line 1 column 1", which reads as malformed JSON
    # rather than as a byte-order mark.
    with open(args.input, "r", encoding="utf-8-sig") as fh:
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
