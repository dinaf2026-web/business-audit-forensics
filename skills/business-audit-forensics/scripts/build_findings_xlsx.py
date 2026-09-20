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


def classify_row(row):
    """Return one of: 'finding', 'client_only', 'question', 'held'.

    THE BUG THIS REPLACES: only NOT CHECKED was excluded, so a row sourced
    entirely from the subject's own records was written to the Findings sheet,
    sorted among VERIFIED items, with nothing distinguishing it. The
    bookkeeper's spreadsheet is the record under examination; it cannot
    corroborate a finding about itself.
    """
    prov = str(row.get("provenance", "")).upper().strip()
    alt = str(row.get("alternative_considered", "")).strip()
    src = str(row.get("source_examined", "")).strip()
    sev = str(row.get("severity", "")).upper().strip()

    if sev == "OPEN QUESTION":
        return "question"
    if prov not in VALID_PROVENANCE or prov == "NOT CHECKED" or not alt or not src:
        return "held"
    if prov == "FROM CLIENT MATERIAL":
        return "client_only"
    return "finding"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input")
    mode.add_argument("--template", help="Write a starter JSON to this path and exit")
    ap.add_argument("--output")
    ap.add_argument("--matter", default="")
    ap.add_argument("--force", action="store_true",
                    help="Allow --template to overwrite an existing file.")
    args = ap.parse_args()

    if args.template:
        path = os.path.abspath(args.template)
        # Refuse to overwrite. The docstring prescribes the same filename for
        # both modes, so re-running the documented --template line replaced a
        # fully populated findings file with the two-row starter. os.replace
        # is atomic and unrecoverable.
        if os.path.exists(path) and not args.force:
            raise SystemExit(
                "%s already exists.\n"
                "Refusing to overwrite it with the starter template. If that "
                "file holds your findings, this would destroy them. Choose "
                "another filename, or pass --force if you are certain." % path)
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

    with open(args.input, "r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        # A dict missing the key previously yielded [], which IS a list, so the
        # type guard never fired and the tool wrote an empty findings log at
        # exit 0. An empty log is indistinguishable from an engagement that
        # found nothing.
        if "findings" not in data:
            raise SystemExit(
                "The JSON object has no 'findings' key. Keys present: %s\n"
                "Refusing to write an empty findings log, which would be "
                "indistinguishable from an engagement that found nothing."
                % ", ".join(sorted(data.keys())))
        data = data["findings"]
    if not isinstance(data, list):
        raise SystemExit("Expected a JSON list of findings, or an object with a "
                         "'findings' list.")
    if not data:
        raise SystemExit(
            "%s contains zero findings. Refusing to write an empty findings "
            "log. If the engagement genuinely found nothing, say so in the "
            "report rather than shipping an empty log." % args.input)

    buckets = {"finding": [], "client_only": [], "question": [], "held": []}
    for r in data:
        buckets[classify_row(r)].append(r)
    for v in buckets.values():
        v.sort(key=sort_key)

    good = buckets["finding"] + buckets["question"]
    good.sort(key=sort_key)
    client_only = buckets["client_only"]
    held = buckets["held"]

    def to_rows(records):
        out = []
        for r in records:
            out.append([r.get(key, "") for key, _, _ in COLUMNS])
        return out

    headers = [label for _, label, _ in COLUMNS]
    widths = [w for _, _, w in COLUMNS]

    wb = new_workbook()
    write_sheet(
        wb, "Findings", headers, to_rows(good), widths=widths,
        # No flag column. flag_col pointed at Severity, which is truthy on
        # every row, so the exception fill shaded the entire sheet and carried
        # no information at all.
        notes=[
            "%s. Built %s." % (args.matter or "Findings log", stamp()),
            "Severity order: CRITICAL, HIGH, MEDIUM, LOW, OPEN QUESTION. "
            "An OPEN QUESTION is stated as a question, never as a defect.",
            "No row here characterizes intent. Report the transaction and the "
            "documentation gap; the conclusion belongs to the reader.",
        ],
    )

    write_sheet(
        wb, "Supported only by client records", headers, to_rows(client_only),
        widths=widths,
        notes=[
            "Every row here is tagged FROM CLIENT MATERIAL. It rests entirely "
            "on records the subject produced, with nothing independent behind "
            "it.",
            "These are kept OFF the Findings sheet on purpose. The records "
            "under examination cannot corroborate a finding about themselves, "
            "and a reader cannot tell the difference once the rows are sorted "
            "together.",
            "To promote a row, obtain an independent source and re-tag it "
            "VERIFIED.",
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
               ["Corroborated findings", len(buckets["finding"])],
               ["Open questions", len(buckets["question"])],
               ["Supported only by client records", len(client_only)],
               ["Held back, not corroborated", len(held)],
               ["", ""]]
    known = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "OPEN QUESTION"]
    for sev in known:
        if sev in counts:
            summary.append([sev, counts[sev]])
    # Unrecognized severities were counted in the total but omitted from the
    # breakdown, so the breakdown silently failed to sum to the total.
    for sev in sorted(k for k in counts if k not in known):
        summary.append([sev + "  (UNRECOGNIZED severity)", counts[sev]])
    write_sheet(wb, "Summary", ["Field", "Value"], summary, widths=[36, 62])

    out = save_workbook(wb, args.output)
    print("Findings log written: %s" % out)
    print("Corroborated findings: %d | open questions: %d | client-records "
          "only: %d | held back: %d"
          % (len(buckets["finding"]), len(buckets["question"]),
             len(client_only), len(held)))
    if client_only:
        print("")
        print("%d row(s) rest only on records the subject produced and are on "
              "a separate sheet." % len(client_only))
    if held:
        print("")
        print("%d row(s) did not clear the corroboration gate and are on the "
              "'Not yet corroborated' sheet:" % len(held))
        for r in held:
            print("  %s  %s" % (r.get("id", "?"), str(r.get("finding", ""))[:70]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
