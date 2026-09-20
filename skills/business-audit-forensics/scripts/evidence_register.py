"""Build an evidence register and chain-of-custody log for an intake folder.

Hashes every file at intake so that any later claim about integrity is
provable. Run this BEFORE opening anything substantive. It cannot be done
retroactively.

Usage:
    python evidence_register.py --input <folder> --output <register.xlsx>
        [--matter "Acme Holdings 2025 books review"]
        [--received-from "the bookkeeper"]
        [--received-how "Email attachment"]

Re-verify a previously built register against the files as they stand now:
    python evidence_register.py --verify <register.xlsx> --input <folder>

The verify mode answers one question: is what I am analyzing still what I was
given? It reports UNCHANGED, CHANGED, MISSING, and NEW per item.
"""

import argparse
import os
import stat
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_common import (  # noqa: E402
    BAD_FILL, GOOD_FILL, new_workbook, provenance_banner, read_table,
    save_workbook, sha256_file, stamp, write_sheet,
)

SKIP_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
SKIP_DIRS = {".git", "__pycache__", ".ipynb_checkpoints"}

DESCRIBE = [
    (("bank", "stmt", "statement"), "Bank or card statement"),
    (("gl", "general ledger", "ledger"), "General ledger"),
    (("trial", "tb"), "Trial balance"),
    (("p&l", "pl", "profit", "income"), "Profit and loss"),
    (("balance sheet", "bs"), "Balance sheet"),
    (("1099", "w-2", "w2", "k-1", "k1"), "Tax information return"),
    (("return", "1040", "1065", "1120"), "Tax return"),
    (("invoice", "inv"), "Invoice"),
    (("payroll",), "Payroll record"),
    (("agreement", "contract", "operating"), "Agreement or contract"),
    (("minutes", "consent", "resolution"), "Governance record"),
    (("recon",), "Reconciliation"),
    (("journal", "je"), "Journal entries"),
    (("audit trail", "changelog", "change log"), "System audit trail"),
]


def guess_description(name):
    low = name.lower()
    for keys, label in DESCRIBE:
        for key in keys:
            if key in low:
                return label
    return ""


def is_reparse(path):
    """True for a symlink OR an NTFS junction.

    os.walk(followlinks=False) suppresses directory SYMLINKS only, and since
    Python 3.8 os.path.islink() returns False for a junction. This machine
    carries deliberate junctions. Without this check the register hashed an
    entire junction target as part of the intake set, inflating the file count
    and byte total, minting evidence IDs for records that were never produced,
    and in verify mode reporting a false integrity breach when an unrelated
    process touched the target. A junction pointing at an ancestor recursed
    until the path length failed.
    """
    if os.path.islink(path):
        return True
    try:
        if hasattr(os.path, "isjunction") and os.path.isjunction(path):
            return True
    except OSError:
        return False
    try:
        return bool(os.lstat(path).st_file_attributes
                    & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, OSError):
        return False


def walk_files(root, skipped=None):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        keep = []
        for d in dirnames:
            full = os.path.join(dirpath, d)
            if d in SKIP_DIRS:
                if skipped is not None:
                    skipped.append([os.path.relpath(full, root), "directory",
                                    "Excluded by name (%s)" % d])
                continue
            if is_reparse(full):
                if skipped is not None:
                    skipped.append([os.path.relpath(full, root), "junction or symlink",
                                    "NOT followed. Points outside the intake set."])
                continue
            keep.append(d)
        dirnames[:] = keep

        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            if name in SKIP_NAMES or name.endswith(".tmp"):
                if skipped is not None:
                    skipped.append([os.path.relpath(full, root), "file",
                                    "Excluded by name or .tmp suffix"])
                continue
            if is_reparse(full):
                if skipped is not None:
                    skipped.append([os.path.relpath(full, root), "link",
                                    "NOT hashed. Link, not a produced record."])
                continue
            found.append(full)
    return sorted(found)


def collect(root, received_from, received_how, skipped=None):
    rows = []
    for idx, full in enumerate(walk_files(root, skipped), start=1):
        rel = os.path.relpath(full, root)
        st = os.stat(full)
        rows.append({
            "id": "E-%03d" % idx,
            "rel": rel.replace("\\", "/"),
            "name": os.path.basename(full),
            "ext": os.path.splitext(full)[1].lower().lstrip("."),
            "size": st.st_size,
            "sha256": sha256_file(full),
            "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "logged": stamp(),
            "from": received_from,
            "how": received_how,
            "desc": guess_description(os.path.basename(full)),
            "abs": full,
        })
    return rows


def build_register(args):
    root = os.path.abspath(args.input)
    if not os.path.isdir(root):
        raise SystemExit("Input folder not found: %s" % root)

    # Refuse to overwrite an existing register. The intake hashes are the only
    # proof of the state at receipt, and this script's own docstring says the
    # step cannot be done retroactively. Nothing previously stopped a rebuild
    # replacing them.
    out_path = os.path.abspath(args.output)
    if os.path.exists(out_path) and not args.force:
        raise SystemExit(
            "%s already exists.\n"
            "Refusing to overwrite it: an intake register records the state of "
            "the evidence at receipt and cannot be rebuilt afterwards. Write "
            "to a new filename, or pass --force if you are certain."
            % out_path)
    if os.path.abspath(root) in out_path:
        raise SystemExit(
            "The output would be written inside the intake folder, which would "
            "make the register part of the evidence it describes. Choose a "
            "path outside %s." % root)

    skipped = []
    items = collect(root, args.received_from, args.received_how, skipped)
    if not items:
        raise SystemExit("No files found under %s" % root)

    wb = new_workbook()
    banner = provenance_banner(
        "evidence_register.py",
        "matter=%s; root=%s" % (args.matter or "(unnamed)", root),
    )

    headers = [
        "Item ID", "File name", "Path as received", "Type", "Size (bytes)",
        "SHA-256", "File modified", "Logged at", "Received from",
        "How received", "Description", "Period covered", "Custody location",
        "Notes",
    ]
    rows = [[
        it["id"], it["name"], it["rel"], it["ext"], it["size"], it["sha256"],
        it["modified"], it["logged"], it["from"], it["how"], it["desc"],
        "", root, "",
    ] for it in items]

    write_sheet(
        wb, "Evidence Register", headers, rows,
        widths=[10, 34, 40, 8, 14, 66, 20, 20, 24, 18, 26, 18, 40, 30],
        notes=[
            banner,
            "Period covered and Notes are filled in by the examiner. The "
            "period a document COVERS is not the date it was received.",
        ],
    )

    custody_headers = [
        "Date and time", "Item ID", "Action", "By whom", "Purpose",
        "Hash at this point", "Notes",
    ]
    custody_rows = [[
        it["logged"], it["id"], "Received and hashed at intake",
        args.examiner, "Intake and preservation", it["sha256"], "",
    ] for it in items]
    write_sheet(
        wb, "Chain of Custody", custody_headers, custody_rows,
        widths=[20, 10, 34, 24, 30, 66, 34],
        notes=[
            "Append a row for EVERY transfer, copy, conversion, or analysis "
            "step. An entry made later is worth far less than one made at "
            "the time.",
        ],
    )

    write_sheet(
        wb, "Transformation Log",
        ["Date and time", "Item ID", "Step", "Tool and version",
         "Parameters and thresholds", "Output produced", "By whom", "Notes"],
        [],
        widths=[20, 10, 34, 24, 40, 34, 20, 34],
        notes=[
            "Log every change of shape: extraction, export, normalization, "
            "merge, dedupe, filter. Exclusions count, including ones added "
            "only to reduce noise.",
        ],
    )

    write_sheet(
        wb, "Requested Not Produced",
        ["Item requested", "Date requested", "Requested from", "Status",
         "What it would have let me test", "Effect on conclusions"],
        [],
        widths=[40, 16, 24, 16, 44, 40],
        notes=[
            "Anything still open at report time goes into Scope and "
            "Limitations BY NAME. An unrecorded gap becomes an unexplained "
            "hole in the analysis later.",
        ],
    )

    write_sheet(
        wb, "Excluded from the register",
        ["Path", "Kind", "Why it was excluded"],
        skipped,
        widths=[60, 22, 60],
        notes=["Everything the walk chose NOT to hash. Previously these were "
               "dropped with no row, no count and no note, while the "
               "Transformation Log sheet instructs that exclusions be recorded "
               "including ones added only to reduce noise.",
               "Junctions and symlinks are NOT followed. A junction points "
               "outside the intake set, and hashing its target would put "
               "records into the register that were never produced."],
    )

    summary = [
        ["Matter", args.matter or "(unnamed)"],
        ["Intake root", root],
        ["Files logged", len(items)],
        ["Paths excluded from the register", len(skipped)],
        ["Total bytes", sum(i["size"] for i in items)],
        ["Register built", stamp()],
        ["Examiner", args.examiner],
        ["Hash algorithm", "SHA-256 over raw bytes"],
    ]
    write_sheet(wb, "Summary", ["Field", "Value"], summary, widths=[24, 80])

    out = save_workbook(wb, args.output)
    print("Evidence register written: %s" % out)
    print("Files logged: %d" % len(items))
    print("Total bytes: %d" % sum(i["size"] for i in items))
    print("")
    print("NEXT: set the intake folder read-only and work only on copies.")
    return 0


def verify(args):
    reg_path = os.path.abspath(args.verify)
    root = os.path.abspath(args.input)
    if not os.path.isfile(reg_path):
        raise SystemExit("Register not found: %s" % reg_path)
    if not os.path.isdir(root):
        raise SystemExit("Input folder not found: %s" % root)

    from openpyxl import load_workbook
    probe = load_workbook(reg_path, read_only=True)
    sheets = list(probe.sheetnames)
    probe.close()
    if "Evidence Register" not in sheets:
        raise SystemExit(
            "%s has no 'Evidence Register' sheet. Sheets present: %s\n"
            "This does not look like a register produced by this script. "
            "Nothing was compared."
            % (reg_path, ", ".join(sheets)))

    headers, recorded = read_table(
        reg_path, sheet="Evidence Register",
        header_contains=["Item ID", "Path as received", "SHA-256"])
    # Rows were previously discarded two ways with no count: a blank path cell
    # dropped the row, and a duplicate path overwrote the earlier entry. The
    # guard below only fired on ZERO rows, so a register of 500 with 40 bad
    # cells verified 460 and reported UNCHANGED 460 | CHANGED 0 | MISSING 0 at
    # exit 0. Forty pieces of evidence were never verified and nothing said so.
    by_rel = {}
    blank_rows, dup_rows = [], []
    for row in recorded:
        rel = str(row.get("Path as received") or "").strip()
        if not rel:
            blank_rows.append(str(row.get("Item ID") or "(no id)"))
            continue
        if rel in by_rel:
            dup_rows.append(rel)
        by_rel[rel] = row

    if blank_rows or dup_rows:
        raise SystemExit(
            "The register could not be read completely and verification was "
            "NOT attempted.\n"
            "  %d row(s) have a blank path cell: %s\n"
            "  %d duplicated path(s): %s\n"
            "Verifying a subset and reporting the result as clean would hide "
            "every item that was skipped. Repair the register first."
            % (len(blank_rows), ", ".join(blank_rows[:10]) or "none",
               len(dup_rows), ", ".join(sorted(set(dup_rows))[:10]) or "none"))

    # Positive control on the instrument itself. If the register parsed to
    # nothing, every current file reads as NEW and the run reports no changes
    # and no missing items, which is indistinguishable from a clean result.
    # A verification that compared nothing must never exit as though it passed.
    if not by_rel:
        raise SystemExit(
            "Read 0 usable rows from the Evidence Register sheet of %s.\n"
            "Nothing was compared. This is an instrument failure, not a clean "
            "result. Check that the file is a register produced by this script."
            % reg_path)

    current = {}
    for full in walk_files(root):
        rel = os.path.relpath(full, root).replace("\\", "/")
        current[rel] = full

    results = []
    changed = missing = new = unchanged = 0

    for rel, row in sorted(by_rel.items()):
        item_id = str(row.get("Item ID") or "")
        want = str(row.get("SHA-256") or "").strip().lower()
        if rel not in current:
            results.append([item_id, rel, "MISSING", want, "", "File is no longer present"])
            missing += 1
            continue
        got = sha256_file(current[rel]).lower()
        if got == want:
            results.append([item_id, rel, "UNCHANGED", want, got, ""])
            unchanged += 1
        else:
            results.append([item_id, rel, "CHANGED", want, got,
                            "Content differs from intake. Do not analyze until explained."])
            changed += 1

    for rel in sorted(current):
        if rel not in by_rel:
            results.append(["", rel, "NEW", "", sha256_file(current[rel]),
                            "Present now, not in the register. Log it."])
            new += 1

    wb = new_workbook()
    ws = write_sheet(
        wb, "Verification",
        ["Item ID", "Path", "Status", "Hash at intake", "Hash now", "Note"],
        results,
        widths=[10, 44, 14, 66, 66, 46],
        notes=[provenance_banner("evidence_register.py --verify",
                                 "register=%s; root=%s" % (reg_path, root))],
    )

    first_data_row = ws.max_row - len(results) + 1
    for offset, row in enumerate(results):
        excel_row = first_data_row + offset
        fill = GOOD_FILL if row[2] == "UNCHANGED" else BAD_FILL
        for col in range(1, 7):
            ws.cell(row=excel_row, column=col).fill = fill

    out = save_workbook(wb, args.output or (os.path.splitext(reg_path)[0] + " - verification.xlsx"))
    print("Verification written: %s" % out)
    print("UNCHANGED %d | CHANGED %d | MISSING %d | NEW %d" % (unchanged, changed, missing, new))
    if changed or missing:
        print("")
        print("STOP. At least one item is not what it was at intake.")
        print("Do not report findings from a changed or missing source until it is explained.")
        return 2
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="Intake folder to hash")
    ap.add_argument("--output", help="Output .xlsx path")
    ap.add_argument("--matter", default="", help="Matter or engagement name")
    ap.add_argument("--received-from", default="", help="Who produced these records")
    ap.add_argument("--received-how", default="", help="Email, portal, drive, direct export")
    ap.add_argument("--examiner", default=os.environ.get("USERNAME", "examiner"))
    ap.add_argument("--verify", help="Re-verify against an existing register")
    ap.add_argument("--force", action="store_true",
                    help="Allow overwriting an existing register. Intake "
                         "hashes cannot be rebuilt once replaced.")
    args = ap.parse_args()

    if args.verify:
        return verify(args)
    if not args.output:
        ap.error("--output is required when building a register")
    return build_register(args)


if __name__ == "__main__":
    raise SystemExit(main())
