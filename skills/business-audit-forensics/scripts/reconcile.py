"""Reconcile a ledger against bank or card statement lines, in BOTH directions.

Direction matters and one direction is not a reconciliation:

  Ledger not in statement  -> entries that exist in the books and not in
                              reality: duplicates, fictitious entries, wrong
                              amounts, timing errors.
  Statement not in ledger  -> the more serious direction: real money moved and
                              the books do not know. Unrecorded deposits,
                              unrecorded withdrawals, off-book activity.

Usage:
    python reconcile.py --ledger "GL cash 2025.xlsx" \\
                        --statement "bank statement 2025.csv" \\
                        --output "reconciliation.xlsx" \\
                        --window 5

    --window          days of clearing lag allowed when matching (default 3)
    --flip-statement  negate statement amounts (use when the two sources use
                      opposite sign conventions)
    --dayfirst        treat ambiguous dates as day-first

The window you allow is recorded in the output. Do not eyeball it.
"""

import argparse
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_common import (  # noqa: E402
    detect_dayfirst, hashes_match, new_workbook, parse_amount, parse_date,
    pick_column, provenance_banner, read_table, save_workbook,
    validate_numeric_column, write_sheet,
)

ZERO = Decimal("0")
CENTS = Decimal("0.01")


def load_lines(path, args, which):
    headers, rows = read_table(path)
    date_col = pick_column(headers, ["date", "transaction date", "posting date",
                                     "posted", "trans date"], label="%s date" % which)
    # A single amount column must NOT be bound to a header that is really one
    # half of a debit/credit pair. "amount" matched inside "Debit Amount",
    # which made the paired branch unreachable and silently discarded every
    # credit-side row: on a trial balance that is the entire liability and
    # equity side, which is the only place a reclassification can show.
    amt_col = pick_column(headers, ["amount", "value", "transaction amount"],
                          required=False, label="%s amount" % which,
                          exclude=("debit", "credit", "dr ", " cr"))
    desc_col = pick_column(headers, ["description", "payee", "memo", "name",
                                     "details", "narrative", "particulars"],
                           required=False, label="%s description" % which)
    deb_col = cre_col = None
    if not amt_col:
        deb_col = pick_column(headers, ["debit", "withdrawal", "payments"],
                              required=False)
        cre_col = pick_column(headers, ["credit", "deposit", "deposits"],
                              required=False)
        if not (deb_col and cre_col):
            raise SystemExit(
                "Could not resolve an amount for the %s file. Found neither a "
                "single amount column nor a debit/credit pair. Headers: %s"
                % (which, ", ".join(headers)))
    if amt_col:
        validate_numeric_column(rows, amt_col, label="%s amount" % which)

    dayfirst, date_basis = detect_dayfirst(
        [r.get(date_col) for r in rows], default=args.dayfirst)

    out = []
    unparsable = []
    for i, row in enumerate(rows, start=2):
        d = parse_date(row.get(date_col), dayfirst=dayfirst)
        if amt_col:
            amt = parse_amount(row.get(amt_col))
        else:
            debit = parse_amount(row.get(deb_col)) or ZERO
            credit = parse_amount(row.get(cre_col)) or ZERO
            amt = credit - debit
        if d is None or amt is None:
            reasons = []
            if d is None:
                reasons.append("unparsable date")
            if amt is None:
                reasons.append("unparsable amount")
            unparsable.append([which, i, str(row.get(date_col)),
                               str(row.get(amt_col or deb_col)),
                               str(row.get(desc_col) or "") if desc_col else "",
                               " and ".join(reasons)])
            continue
        # Quantize so a float artifact out of Excel cannot defeat an exact
        # amount match and push a genuine pair into both exception sheets.
        out.append({
            "row": i,
            "date": d,
            "amount": amt.quantize(CENTS),
            "desc": str(row.get(desc_col) or "").strip() if desc_col else "",
            "matched": False,
            "match_row": None,
            "gap": None,
        })
    basis = ("amount column '%s'" % amt_col) if amt_col else (
        "credit '%s' less debit '%s'" % (cre_col, deb_col))
    return out, basis + "; dates " + date_basis, unparsable


def reconcile(ledger, statement, window):
    """Two passes: exact same-day first, then widen to the window.

    Doing exact-date first stops a near match inside the window from consuming
    a line that has a perfect same-day counterpart.
    """
    by_amount = {}
    for s in statement:
        by_amount.setdefault(s["amount"], []).append(s)

    ambiguous = []

    for allowed in (0, window):
        for l in ledger:
            if l["matched"]:
                continue
            candidates = [s for s in by_amount.get(l["amount"], [])
                          if not s["matched"]
                          and abs((s["date"] - l["date"]).days) <= allowed]
            if not candidates:
                continue
            candidates.sort(key=lambda s: abs((s["date"] - l["date"]).days))
            best = candidates[0]
            # Flag whenever MORE THAN ONE candidate was available, not only on
            # an exact tie. Greedy nearest-first can take a candidate that a
            # later ledger line needed, stranding both and manufacturing an
            # entry in "In statement not in ledger" - the most serious output
            # this tool produces. A strictly-nearer winner hid that case from
            # the ambiguity sheet entirely.
            if len(candidates) > 1 and allowed > 0:
                ambiguous.append((l, candidates))
            l["matched"] = best["matched"] = True
            l["match_row"] = best["row"]
            best["match_row"] = l["row"]
            gap = (best["date"] - l["date"]).days
            l["gap"] = best["gap"] = gap

    return ambiguous


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--statement", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--window", type=int, default=3,
                    help="Days of clearing lag allowed (default 3)")
    ap.add_argument("--flip-statement", action="store_true",
                    help="Negate statement amounts")
    ap.add_argument("--dayfirst", action="store_true")
    args = ap.parse_args()

    for path in (args.ledger, args.statement):
        if not os.path.isfile(path):
            raise SystemExit("File not found: %s" % path)

    # Same file on both sides: every line matches itself and the run reports a
    # perfect reconciliation. hashes_match covers a copy under a second name.
    if os.path.abspath(args.ledger) == os.path.abspath(args.statement):
        raise SystemExit(
            "--ledger and --statement point at the same file. Every line would "
            "match itself and the run would report a perfect reconciliation.")
    if hashes_match(args.ledger, args.statement):
        raise SystemExit(
            "--ledger and --statement are byte-identical files under different "
            "names. Every line would match itself and the run would report a "
            "perfect reconciliation.")

    if args.window < 0:
        raise SystemExit("--window cannot be negative. Got %d." % args.window)

    ledger, ledger_basis, ledger_bad = load_lines(args.ledger, args, "ledger")
    statement, stmt_basis, stmt_bad = load_lines(args.statement, args, "statement")

    # A reconciliation that compared nothing must never be able to print
    # "Fully reconciled: YES". Both sides empty satisfied every emptiness test
    # in the summary and returned 0, which is indistinguishable from a genuine
    # clean reconciliation.
    if not ledger or not statement:
        raise SystemExit(
            "Zero usable rows on the %s side (ledger %d, statement %d).\n"
            "Nothing was compared. This is an instrument failure, not a clean "
            "reconciliation." % (
                "ledger" if not ledger else "statement",
                len(ledger), len(statement)))

    if args.flip_statement:
        for s in statement:
            s["amount"] = -s["amount"]

    ambiguous = reconcile(ledger, statement, args.window)

    matched = [l for l in ledger if l["matched"]]
    ledger_only = [l for l in ledger if not l["matched"]]
    stmt_only = [s for s in statement if not s["matched"]]

    wb = new_workbook()
    banner = provenance_banner(
        "reconcile.py",
        "window=%d day(s); ledger %s; statement %s%s" % (
            args.window, ledger_basis, stmt_basis,
            "; statement sign flipped" if args.flip_statement else ""),
    )

    write_sheet(
        wb, "Matched",
        ["Ledger row", "Ledger date", "Amount", "Ledger description",
         "Statement row", "Days apart"],
        [[l["row"], l["date"].isoformat(), float(l["amount"]), l["desc"],
          l["match_row"], l["gap"]] for l in matched],
        widths=[12, 14, 15, 46, 14, 12],
        notes=[banner],
    )

    write_sheet(
        wb, "In ledger not in statement",
        ["Ledger row", "Date", "Amount", "Description", "Question to answer"],
        [[l["row"], l["date"].isoformat(), float(l["amount"]), l["desc"],
          "Outstanding item that will clear next period, or an entry with no "
          "real transaction behind it? Confirm against the following period."]
         for l in ledger_only],
        widths=[12, 14, 15, 46, 62],
        notes=["Outstanding cheques and deposits in transit belong here and are "
               "normal. PROVE them by confirming they clear in the following "
               "period. An item that never clears is a finding."],
    )

    write_sheet(
        wb, "In statement not in ledger",
        ["Statement row", "Date", "Amount", "Description", "Question to answer"],
        [[s["row"], s["date"].isoformat(), float(s["amount"]), s["desc"],
          "Real money moved and the books do not record it. Identify the "
          "transaction and why it was not posted."]
         for s in stmt_only],
        widths=[14, 14, 15, 46, 62],
        notes=["This is the more serious direction. Unrecorded activity is not "
               "visible to any test that runs against the ledger alone."],
    )

    amb_rows = []
    for l, cands in ambiguous:
        gaps = sorted(abs((c["date"] - l["date"]).days) for c in cands)
        amb_rows.append([
            l["row"], l["date"].isoformat(), float(l["amount"]), l["desc"],
            ", ".join(str(c["row"]) for c in cands),
            ", ".join(str(g) for g in gaps),
            "This ledger line had %d statement candidates inside the window. "
            "The nearest was taken. Matching is greedy in ledger order, so a "
            "candidate another line needed may have been consumed here. "
            "Confirm by hand before relying on either exception sheet."
            % len(cands),
        ])
    write_sheet(
        wb, "Ambiguous matches",
        ["Ledger row", "Date", "Amount", "Description",
         "Candidate statement rows", "Days apart", "Note"],
        amb_rows,
        widths=[12, 14, 15, 36, 26, 14, 62],
        notes=["A one-to-many match is a finding to investigate, not a nuisance "
               "to resolve quietly. Identical amounts on identical dates are "
               "usually two genuine transactions."],
    )

    led_total = sum((l["amount"] for l in ledger), ZERO)
    stmt_total = sum((s["amount"] for s in statement), ZERO)
    summary = [
        ["Ledger file", os.path.abspath(args.ledger)],
        ["Ledger amount basis", ledger_basis],
        ["Ledger lines parsed", len(ledger)],
        ["Ledger lines NOT parsed (not screened)", len(ledger_bad)],
        ["Ledger total", float(led_total)],
        ["Statement file", os.path.abspath(args.statement)],
        ["Statement amount basis", stmt_basis],
        ["Statement sign flipped", "yes" if args.flip_statement else "no"],
        ["Statement lines parsed", len(statement)],
        ["Statement lines NOT parsed (not screened)", len(stmt_bad)],
        ["Statement total", float(stmt_total)],
        ["Clearing window allowed (days)", args.window],
        ["Matched pairs", len(matched)],
        ["In ledger not in statement", len(ledger_only)],
        ["In statement not in ledger", len(stmt_only)],
        ["Ambiguous matches", len(ambiguous)],
        ["Difference in totals", float(led_total - stmt_total)],
        ["Fully reconciled", "YES" if not ledger_only and not stmt_only
         and not ledger_bad and not stmt_bad else "NO"],
    ]
    write_sheet(wb, "Summary", ["Field", "Value"], summary, widths=[46, 62],
                notes=["If Fully reconciled is YES, record that as a positive "
                       "finding with the accounts, the statements used and the "
                       "ending balance. It stops the work being redone."])

    write_sheet(
        wb, "Not screened",
        ["Side", "Row", "Raw date", "Raw amount", "Description", "Reason"],
        ledger_bad + stmt_bad,
        widths=[12, 8, 20, 18, 36, 30],
        notes=["These rows were never compared by either direction. They are "
               "not exceptions and they are not clear. Previously only a COUNT "
               "reached the summary, so nobody could find them to fix them."],
    )

    out = save_workbook(wb, args.output)

    print("Reconciliation written: %s" % out)
    print("Matched %d | ledger-only %d | statement-only %d | ambiguous %d"
          % (len(matched), len(ledger_only), len(stmt_only), len(ambiguous)))
    if ledger_bad or stmt_bad:
        print("")
        print("NOT SCREENED: %d ledger and %d statement lines could not be "
              "parsed and were never compared."
              % (len(ledger_bad), len(stmt_bad)))
        print("These are not exceptions. They are unexamined. See the "
              "'Not screened' sheet.")
    if stmt_only:
        print("")
        print("%d statement line(s) do not appear in the ledger. Start there."
              % len(stmt_only))

    # Unrecorded activity is the serious direction. A caller or scheduler must
    # not read this run as clean.
    if stmt_only or ledger_bad or stmt_bad:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
