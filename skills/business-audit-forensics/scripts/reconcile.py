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
    new_workbook, parse_amount, parse_date, pick_column, provenance_banner,
    read_table, save_workbook, write_sheet,
)

ZERO = Decimal("0")


def load_lines(path, args, which):
    headers, rows = read_table(path)
    date_col = pick_column(headers, ["date", "transaction date", "posting date",
                                     "posted", "trans date"], label="%s date" % which)
    amt_col = pick_column(headers, ["amount", "value", "debit", "credit",
                                    "transaction amount"], required=False,
                          label="%s amount" % which)
    desc_col = pick_column(headers, ["description", "payee", "memo", "name",
                                     "details", "narrative", "particulars"],
                           required=False, label="%s description" % which)
    deb_col = cre_col = None
    if not amt_col or amt_col.lower() in ("debit", "credit"):
        deb_col = pick_column(headers, ["debit", "dr", "withdrawal", "payments"],
                              required=False)
        cre_col = pick_column(headers, ["credit", "cr", "deposit", "deposits"],
                              required=False)
        if deb_col and cre_col:
            amt_col = None

    out = []
    unparsable = 0
    for i, row in enumerate(rows, start=2):
        d = parse_date(row.get(date_col), dayfirst=args.dayfirst)
        if amt_col:
            amt = parse_amount(row.get(amt_col))
        else:
            debit = parse_amount(row.get(deb_col)) or ZERO
            credit = parse_amount(row.get(cre_col)) or ZERO
            amt = credit - debit
        if d is None or amt is None:
            unparsable += 1
            continue
        out.append({
            "row": i,
            "date": d,
            "amount": amt,
            "desc": str(row.get(desc_col) or "").strip() if desc_col else "",
            "matched": False,
            "match_row": None,
            "gap": None,
        })
    basis = ("amount column '%s'" % amt_col) if amt_col else (
        "credit '%s' less debit '%s'" % (cre_col, deb_col))
    return out, basis, unparsable


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
            tied = [c for c in candidates
                    if abs((c["date"] - l["date"]).days)
                    == abs((best["date"] - l["date"]).days)]
            if len(tied) > 1:
                ambiguous.append((l, tied))
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

    ledger, ledger_basis, ledger_bad = load_lines(args.ledger, args, "ledger")
    statement, stmt_basis, stmt_bad = load_lines(args.statement, args, "statement")

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
        amb_rows.append([
            l["row"], l["date"].isoformat(), float(l["amount"]), l["desc"],
            ", ".join(str(c["row"]) for c in cands),
            "One ledger line could match %d statement lines equally well. "
            "Resolved arbitrarily. Confirm by hand." % len(cands),
        ])
    write_sheet(
        wb, "Ambiguous matches",
        ["Ledger row", "Date", "Amount", "Description",
         "Candidate statement rows", "Note"],
        amb_rows,
        widths=[12, 14, 15, 40, 26, 62],
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
        ["Ledger lines NOT parsed (not screened)", ledger_bad],
        ["Ledger total", float(led_total)],
        ["Statement file", os.path.abspath(args.statement)],
        ["Statement amount basis", stmt_basis],
        ["Statement sign flipped", "yes" if args.flip_statement else "no"],
        ["Statement lines parsed", len(statement)],
        ["Statement lines NOT parsed (not screened)", stmt_bad],
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

    out = save_workbook(wb, args.output)

    print("Reconciliation written: %s" % out)
    print("Matched %d | ledger-only %d | statement-only %d | ambiguous %d"
          % (len(matched), len(ledger_only), len(stmt_only), len(ambiguous)))
    if ledger_bad or stmt_bad:
        print("")
        print("NOT SCREENED: %d ledger and %d statement lines could not be "
              "parsed and were never compared." % (ledger_bad, stmt_bad))
        print("These are not exceptions. They are unexamined. Fix the input.")
    if stmt_only:
        print("")
        print("%d statement line(s) do not appear in the ledger. Start there."
              % len(stmt_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
