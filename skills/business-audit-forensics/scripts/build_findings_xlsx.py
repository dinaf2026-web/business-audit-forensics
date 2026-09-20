"""Build a severity-ranked findings log from a findings JSON file.

Usage:
    python build_findings_xlsx.py --template findings.json     # write a starter
    python build_findings_xlsx.py --input findings.json --output "AUDIT - findings (19-09-2026).xlsx"

The Provenance and Alternative explanation columns are mandatory. A row with
either left blank is written into a separate "Not yet corroborated" sheet
rather than the findings log, because an item that has not cleared the
corroboration gate is not a finding.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_common import (  # noqa: E402
    new_workbook, save_workbook, stamp, write_sheet,
)

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3,
                  "OPEN QUESTION": 4}

VALID_PROVENANCE = {"VERIFIED", "FROM CLIENT MATERIAL", "NOT CHECKED"}

COLUMNS = [
    ("id", "ID", 10),
    ("severity", "Severity", 15),
    ("category", "Category", 18),
    ("finding", "Finding", 56),
    ("condition", "Condition (what is)", 44),
    ("criteria", "Criteria (what should be)", 40),
    ("cause", "Cause", 34),
    ("effect", "Effect", 40),
    ("amount", "Amount", 16),
    ("evidence", "Evidence item IDs", 22),
    ("provenance", "Provenance", 22),
    ("source_examined", "Source document examined", 38),
    ("alternative_considered", "Alternative explanation considered", 44),
    ("recommendation", "Recommendation", 44),
    ("owner", "Owner", 18),
    ("due", "Due", 14),
    ("status", "Status", 14),
]

TEMPLATE = [
    {
        "id": "F-001",
        "severity": "HIGH",
        "category": "Documentation",
        "finding": "State the transaction factually. No characterization of intent.",
        "condition": "What is, with dates, amounts, accounts and counterparties.",
        "criteria": "What should be, and the source of that expectation.",
        "cause": "Usually structural rather than personal.",
        "effect": "Consequence, quantified where possible.",
        "amount": "",
        "evidence": "E-001; E-014",
        "provenance": "VERIFIED",
        "source_examined": "Name the file and the page or line.",
        "alternative_considered": "The innocent explanation you tested and ruled out, and how.",
        "recommendation": "Specific, assigned, dated.",
        "owner": "",
        "due": "",
        "status": "Open",
    },
    {
        "id": "Q-001",
        "severity": "OPEN QUESTION",
        "category": "Authorization",
        "finding": "Worded as a QUESTION, because it did not clear the corroboration gate.",
        "condition": "",
        "criteria": "",
        "cause": "",
        "effect": "",
        "amount": "",
        "evidence": "",
        "provenance": "NOT CHECKED",
        "source_examined": "",
        "alternative_considered": "",
        "recommendation": "Obtain the document named, then re-assess.",
        "owner": "",
        "due": "",
        "status": "Open",
    },
]


def sort_key(row):
    sev = str(row.get("severity", "")).upper().strip()
    return (SEVERITY_ORDER.get(sev, 9), str(row.get("id", "")))


def corroborated(row):
    prov = str(row.get("provenance", "")).upper().strip()
    alt = str(row.get("alternative_considered", "")).strip()
    src = str(row.get("source_examined", "")).strip()
    sev = str(row.get("severity", "")).upper().strip()
    if sev == "OPEN QUESTION":
        return True
    return bool(prov in VALID_PROVENANCE and prov != "NOT CHECKED" and alt and src)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input")
    ap.add_argument("--output")
    ap.add_argument("--template", help="Write a starter JSON to this path and exit")
    ap.add_argument("--matter", default="")
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
    if isinstance(data, dict):
        data = data.get("findings", [])
    if not isinstance(data, list):
        raise SystemExit("Expected a JSON list of findings, or an object with a "
                         "'findings' list.")

    good = [r for r in data if corroborated(r)]
    held = [r for r in data if not corroborated(r)]
    good.sort(key=sort_key)
    held.sort(key=sort_key)

    def to_rows(records):
        out = []
        for r in records:
            out.append([r.get(key, "") for key, _, _ in COLUMNS])
        return out

    headers = [label for _, label, _ in COLUMNS]
    widths = [w for _, _, w in COLUMNS]

    wb = new_workbook()
    write_sheet(
        wb, "Findings", headers, to_rows(good), widths=widths, flag_col=1,
        notes=[
            "%s. Built %s." % (args.matter or "Findings log", stamp()),
            "Severity order: CRITICAL, HIGH, MEDIUM, LOW, OPEN QUESTION. "
            "An OPEN QUESTION is stated as a question, never as a defect.",
            "No row here characterizes intent. Report the transaction and the "
            "documentation gap; the conclusion belongs to the reader.",
        ],
    )

    write_sheet(
        wb, "Not yet corroborated", headers, to_rows(held), widths=widths,
        notes=[
            "These rows are missing a provenance tag, a named source document, "
            "or the alternative explanation they were tested against.",
            "They have NOT cleared the corroboration gate and must not be "
            "reported as findings. Either complete the three columns or "
            "reclassify the row as an OPEN QUESTION.",
        ],
    )

    counts = {}
    for r in good:
        sev = str(r.get("severity", "")).upper().strip() or "(none)"
        counts[sev] = counts.get(sev, 0) + 1
    summary = [["Matter", args.matter or "(unnamed)"],
               ["Built", stamp()],
               ["Source", os.path.abspath(args.input)],
               ["Findings in log", len(good)],
               ["Held back, not corroborated", len(held)],
               ["", ""]]
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "OPEN QUESTION"]:
        if sev in counts:
            summary.append([sev, counts[sev]])
    write_sheet(wb, "Summary", ["Field", "Value"], summary, widths=[36, 62])

    out = save_workbook(wb, args.output)
    print("Findings log written: %s" % out)
    print("In log: %d | held back as not corroborated: %d" % (len(good), len(held)))
    if held:
        print("")
        print("%d row(s) did not clear the corroboration gate and are on the "
              "'Not yet corroborated' sheet:" % len(held))
        for r in held:
            print("  %s  %s" % (r.get("id", "?"), str(r.get("finding", ""))[:70]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
