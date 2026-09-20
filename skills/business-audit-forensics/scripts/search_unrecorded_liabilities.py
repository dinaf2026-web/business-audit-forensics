"""Search for unrecorded liabilities, and detect debt that does not look like debt.

Two jobs, both working from OUTSIDE the ledger inward, because an omitted
liability leaves no entry to test and is invisible to any procedure that starts
from the books.

  1. SUBSEQUENT DISBURSEMENTS. Take payments made AFTER period end and find the
     ones with no matching liability recorded AT period end. A payment in
     January for December services is a December liability.

  2. RECURRING FIXED DEBITS. Merchant cash advances and receivable factoring
     are usually documented as a sale of future receivables rather than a loan,
     and frequently appear nowhere on the balance sheet. The tell is in the
     bank activity: same payee, same amount, on a regular short cycle.

Usage:
    python search_unrecorded_liabilities.py \\
        --disbursements "post period payments.csv" \\
        --period-end 2025-12-31 \\
        --recorded "AP aging at 12-31.csv" \\
        --output "unrecorded liabilities.xlsx" \\
        --threshold 500

  --recorded is optional. Without it every post-period payment above the
  threshold is listed for manual comparison, and the output says so.

Output is a CANDIDATE list. Each item needs the invoice pulled and the SERVICE
OR DELIVERY DATE read, which is the field that decides the period. The invoice
date and the payment date both mislead.
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_common import (  # noqa: E402
    detect_dayfirst, new_workbook, normalize_name, parse_amount, parse_date,
    pick_column, provenance_banner, read_table, save_workbook,
    validate_numeric_column, write_sheet,
)

ZERO = Decimal("0")
CONTROL_TAG = "ZZ-CONTROL-ROW-DO-NOT-REPORT"


def load_payments(path, args):
    headers, rows = read_table(path)
    date_col = pick_column(headers, ["date", "payment date", "transaction date",
                                     "posting date"], label="payment date")
    amt_col = pick_column(headers, ["amount", "payment", "value", "debit"],
                          label="amount")
    payee_col = pick_column(headers, ["payee", "vendor", "description", "name",
                                      "memo", "details"], required=False)
    svc_col = pick_column(headers, ["service date", "service period",
                                    "invoice date", "period"], required=False)

    validate_numeric_column(rows, amt_col, label="payment amount")

    dayfirst, date_basis = detect_dayfirst(
        [r.get(date_col) for r in rows], default=args.dayfirst)

    raw = []
    bad = []
    for i, row in enumerate(rows, start=2):
        d = parse_date(row.get(date_col), dayfirst=dayfirst)
        a = parse_amount(row.get(amt_col))
        if d is None or a is None:
            reasons = []
            if d is None:
                reasons.append("unparsable date")
            if a is None:
                reasons.append("unparsable amount")
            bad.append([i, str(row.get(date_col)), str(row.get(amt_col)),
                        str(row.get(payee_col) or ""), " and ".join(reasons)])
            continue
        payee = str(row.get(payee_col) or "").strip() if payee_col else ""
        raw.append({
            "row": i, "date": d, "signed": a, "payee": payee,
            "norm": normalize_name(payee),
            "service": parse_date(row.get(svc_col), dayfirst=dayfirst) if svc_col else None,
            "matched": False, "control": False,
        })

    # SIGN. The previous version took abs() at load, which turned every
    # deposit in a bank register into a candidate unrecorded liability. A
    # $180,000 customer receipt was reported as an unrecorded payable.
    has_neg = any(r["signed"] < ZERO for r in raw)
    has_pos = any(r["signed"] > ZERO for r in raw)
    if args.outflow_sign == "negative":
        keep, basis = (lambda v: v < ZERO), "negative amounts treated as outflows (explicit)"
    elif args.outflow_sign == "positive":
        keep, basis = (lambda v: v > ZERO), "positive amounts treated as outflows (explicit)"
    elif has_neg and has_pos:
        keep, basis = (lambda v: v < ZERO), ("mixed signs detected, negative "
                                             "amounts treated as outflows")
    else:
        keep, basis = (lambda v: True), "single sign throughout, all rows treated as outflows"

    out, inflows = [], []
    for r in raw:
        if keep(r["signed"]):
            r["amount"] = abs(r["signed"])
            out.append(r)
        else:
            inflows.append([r["row"], r["date"].isoformat(),
                            float(r["signed"]), r["payee"],
                            "Excluded as an inflow, not a payment"])

    parsed_service = sum(1 for r in out if r["service"] is not None)
    return out, bad, inflows, (parsed_service > 0), basis, date_basis


def load_recorded(path, args):
    headers, rows = read_table(path)
    payee_col = pick_column(headers, ["payee", "vendor", "name", "description",
                                      "account"], label="recorded payee")
    amt_col = pick_column(headers, ["amount", "balance", "total", "open"],
                          label="recorded amount")
    out, bad = [], []
    for i, row in enumerate(rows, start=2):
        a = parse_amount(row.get(amt_col))
        name = str(row.get(payee_col) or "").strip()
        if a is None or not name:
            bad.append([i, name, str(row.get(amt_col)), "Unparsable or blank"])
            continue
        out.append({"row": i, "payee": name, "norm": normalize_name(name),
                    "amount": abs(a), "used": False})
    return out, bad


def match_against_recorded(payments, recorded, tol):
    """A payment is explained if a recorded liability exists for the same payee
    at approximately the same amount. Greedy, one recorded item per payment."""
    by_payee = defaultdict(list)
    for r in recorded:
        by_payee[r["norm"]].append(r)

    # Control rows are NOT skipped here. They must traverse the same matching
    # code the real rows do, or the control proves nothing about the matcher.
    for p in payments:
        for cand in by_payee.get(p["norm"], []):
            if cand["used"]:
                continue
            if abs(cand["amount"] - p["amount"]) <= tol:
                p["matched"] = True
                cand["used"] = True
                p["match_row"] = cand["row"]
                break


def detect_recurring(payments, min_hits, max_gap):
    """Same payee, same amount, on a short regular cycle.

    This is the merchant cash advance / factoring signature. It is a PATTERN,
    not a finding: legitimate subscriptions, rent and insurance also recur.
    What distinguishes a funder is the short cycle, usually daily or weekly.
    """
    groups = defaultdict(list)
    for p in payments:
        groups[(p["norm"], p["amount"])].append(p)

    hits = []
    for (norm, amount), items in groups.items():
        if len(items) < min_hits or not norm:
            continue
        items.sort(key=lambda x: x["date"])
        gaps = [(items[i + 1]["date"] - items[i]["date"]).days
                for i in range(len(items) - 1)]
        if not gaps:
            continue
        typical = sorted(gaps)[len(gaps) // 2]
        if typical == 0 or typical > max_gap:
            continue
        spread = max(gaps) - min(gaps)
        regular = spread <= max(2, typical)
        if not regular:
            continue
        total = sum((i["amount"] for i in items), ZERO)
        spellings = sorted({i["payee"] for i in items})
        hits.append({
            # 'norm' is carried because the exclusion set downstream MUST key
            # on the same value this grouped on. Keying on the raw payee let
            # alternative spellings of one funder ('RAPID FINANCE, LLC' vs
            # 'Rapid Finance LLC') escape the exclusion and be counted as
            # one-off unrecorded liabilities, reintroducing the overstatement
            # this separation exists to prevent.
            "norm": norm,
            "payee": spellings[0],
            "spellings": spellings,
            "amount": amount, "count": len(items),
            "cycle": typical, "first": items[0]["date"], "last": items[-1]["date"],
            "total": total, "control": items[0]["control"],
        })
    return hits


def build_controls(threshold, period_end):
    """Synthetic items each detector MUST catch.

    THE BUG THIS REPLACES: controls were dated in the year 2000 and were
    skipped by the matcher outright, so the 'unmatched' control could never
    become matched and its PASS was a tautology. It sat beside the sentence
    'a zero here is meaningful only if this reads PASS', which was backed by
    nothing. A control that does not traverse the same code and the same
    filters as the real rows proves nothing.

    These are dated AFTER period end and priced ABOVE the threshold so they
    pass every filter a real candidate passes.
    """
    from datetime import timedelta
    d = period_end + timedelta(days=1)
    ctrl = []
    unmatched_name = CONTROL_TAG + " UNMATCHED"
    ctrl.append({"row": -1, "date": d,
                 "amount": threshold + Decimal("1234.56"),
                 "signed": -(threshold + Decimal("1234.56")),
                 "payee": unmatched_name, "norm": normalize_name(unmatched_name),
                 "service": None, "matched": False, "control": True})

    recurring_name = CONTROL_TAG + " RECURRING"
    for k in range(10):
        ctrl.append({"row": -(10 + k), "date": d + timedelta(days=7 * k),
                     "amount": Decimal("742.19"), "signed": Decimal("-742.19"),
                     "payee": recurring_name,
                     "norm": normalize_name(recurring_name),
                     "service": None, "matched": False, "control": True})
    return ctrl


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disbursements", required=True,
                    help="Payments made AFTER period end")
    ap.add_argument("--period-end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--recorded", help="Liabilities recorded AT period end (AP aging/accruals)")
    ap.add_argument("--output", required=True)
    ap.add_argument("--threshold", type=str, default="500")
    ap.add_argument("--tolerance", type=str, default="0.01")
    ap.add_argument("--recurring-min", type=int, default=4)
    ap.add_argument("--recurring-max-gap", type=int, default=14,
                    help="Longest cycle in days still treated as short-cycle (default 14)")
    ap.add_argument("--dayfirst", action="store_true",
                    help="Default convention when no row in the date column proves it")
    ap.add_argument("--outflow-sign", choices=["auto", "negative", "positive"],
                    default="auto",
                    help="Which sign represents a payment. 'auto' treats "
                         "negatives as outflows when both signs are present.")
    args = ap.parse_args()

    if not os.path.isfile(args.disbursements):
        raise SystemExit("File not found: %s" % args.disbursements)

    # Parsed strictly. Previously this used the ambiguous parser WITHOUT the
    # dayfirst flag while the data used it WITH, so a UK engagement compared
    # transactions dated 5 June against a cut-off resolved as 6 May.
    try:
        period_end = datetime.strptime(args.period_end.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit(
            "--period-end must be written YYYY-MM-DD. Got: %s\n"
            "It is parsed strictly on purpose, so that it cannot be read with "
            "a different day/month convention than the transaction dates."
            % args.period_end)

    try:
        threshold = Decimal(args.threshold)
        tol = Decimal(args.tolerance)
    except Exception:
        raise SystemExit("--threshold and --tolerance must be plain numbers "
                         "with no thousands separators.")

    (payments, bad_pay, inflows, has_service,
     sign_basis, date_basis) = load_payments(args.disbursements, args)

    if not payments:
        raise SystemExit(
            "Zero usable payment rows were read from %s.\n"
            "Nothing was examined. This is an instrument failure, not a clean "
            "result: with no population every detector trivially finds nothing."
            % args.disbursements)

    controls = build_controls(threshold, period_end)
    population = payments + controls

    before = [p for p in payments if p["date"] <= period_end]

    recorded, bad_rec = ([], [])
    if args.recorded:
        if not os.path.isfile(args.recorded):
            raise SystemExit("File not found: %s" % args.recorded)
        if os.path.abspath(args.recorded) == os.path.abspath(args.disbursements):
            raise SystemExit(
                "--recorded and --disbursements point at the same file. Every "
                "payment would explain itself and the run would report nothing "
                "outstanding.")
        recorded, bad_rec = load_recorded(args.recorded, args)
        match_against_recorded(population, recorded, tol)

    recurring = detect_recurring(population, args.recurring_min, args.recurring_max_gap)

    # Candidates computed over the FULL population including controls, so the
    # control passes through the identical filters a real finding does.
    all_candidates = [p for p in population
                      if not p["matched"] and p["amount"] >= threshold
                      and p["date"] > period_end]

    ctrl_unmatched = any(p["control"] and "UNMATCHED" in p["payee"]
                         for p in all_candidates)
    ctrl_recurring = any(r["control"] for r in recurring)

    candidates = [p for p in all_candidates if not p["control"]]
    explained = [p for p in payments if p["matched"]]

    # A payment that is part of a recurring fixed-debit series is NOT an
    # unrecorded liability of the prior period. It is a repayment on a facility.
    # Mixing the two into one total overstates the unrecorded-liability figure
    # by the whole value of the remittance stream, which is exactly the kind of
    # mislabelling this skill exists to prevent. Tag them and total separately.
    recurring_keys = {(r["norm"], r["amount"]) for r in recurring if not r["control"]}
    for p in candidates:
        p["recurring"] = (p["norm"], p["amount"]) in recurring_keys

    one_off = [p for p in candidates if not p["recurring"]]
    repeat = [p for p in candidates if p["recurring"]]

    wb = new_workbook()
    banner = provenance_banner(
        "search_unrecorded_liabilities.py",
        "period_end=%s; threshold=%s; tolerance=%s; recurring_min=%d; "
        "recurring_max_gap=%d; sign=%s; dates=%s; recorded=%s" % (
            period_end.isoformat(), threshold, tol, args.recurring_min,
            args.recurring_max_gap, sign_basis, date_basis,
            os.path.basename(args.recorded) if args.recorded else "NOT SUPPLIED"),
    )

    notes = [banner]
    if not args.recorded:
        notes.append(
            "NO RECORDED-LIABILITY FILE WAS SUPPLIED. Nothing was matched, so "
            "every payment above the threshold is listed. This is a WORKLIST, "
            "not a set of exceptions.")
    notes.append(
        "CONTROL: unmatched-payment detector %s. A zero here is meaningful "
        "only if this reads PASS." % ("PASS" if ctrl_unmatched else "FAIL"))
    notes.append(
        "For each item, pull the invoice and read the SERVICE OR DELIVERY "
        "DATE. That field decides the period. The invoice date and the "
        "payment date both mislead.")
    if not has_service:
        notes.append(
            "No USABLE service dates were parsed from the input, so the period "
            "each obligation belongs to could NOT be assessed here. It must be "
            "read off the invoices by hand. Note this reports on values "
            "actually parsed, not on whether a column with that name exists: a "
            "'Service Period' column holding text such as 'Dec 2025' yields "
            "nothing usable.")

    notes.append(
        "Rows marked YES in 'Part of a recurring series' are NOT prior-period "
        "liabilities. They are repayments on a facility and are totalled "
        "separately on the Summary sheet. Do not add the two figures together.")

    write_sheet(
        wb, "Candidate unrecorded",
        ["Row", "Payment date", "Amount", "Payee", "Part of a recurring series",
         "Service date if given", "Days after period end",
         "Service period per invoice", "Recorded at period end?",
         "Finding or open question"],
        [[p["row"], p["date"].isoformat(), float(p["amount"]), p["payee"],
          "YES" if p.get("recurring") else "",
          p["service"].isoformat() if p["service"] else "",
          (p["date"] - period_end).days, "", "", ""]
         for p in sorted(candidates, key=lambda x: (x.get("recurring", False), -x["amount"]))],
        widths=[8, 14, 15, 38, 22, 18, 16, 26, 22, 30],
        # No flag shading here. The only YES/NO column is "part of a recurring
        # series", and shading it marked the rows the notes say to EXCLUDE
        # with the fill this toolkit uses everywhere to mean "this is the
        # exception". A reader scanning for shaded rows read the facility
        # repayments as the findings.
        notes=notes,
    )

    write_sheet(
        wb, "Explained by recorded",
        ["Row", "Payment date", "Amount", "Payee", "Matched recorded row"],
        [[p["row"], p["date"].isoformat(), float(p["amount"]), p["payee"],
          p.get("match_row", "")] for p in explained],
        widths=[8, 14, 15, 40, 20],
        notes=["A match on payee and amount is a reasonable explanation, not "
               "proof. It does not confirm the amount recorded was complete."],
    )

    rec_rows = [[r["payee"],
                 "; ".join(r["spellings"][1:]) if len(r["spellings"]) > 1 else "",
                 float(r["amount"]), r["count"], r["cycle"],
                 r["first"].isoformat(), r["last"].isoformat(), float(r["total"]),
                 "Daily or near-daily" if r["cycle"] <= 3 else "Weekly or short cycle"]
                for r in sorted(recurring, key=lambda x: -x["total"])
                if not r["control"]]
    write_sheet(
        wb, "Recurring fixed debits",
        ["Payee", "Other spellings grouped", "Amount each", "Times",
         "Typical days apart", "First", "Last", "Total paid", "Cycle"],
        rec_rows,
        widths=[34, 34, 15, 10, 20, 14, 14, 16, 24],
        notes=[
            "CONTROL: recurring detector %s." % ("PASS" if ctrl_recurring else "FAIL"),
            "Same payee, same amount, short regular cycle. This is the "
            "signature of a MERCHANT CASH ADVANCE or RECEIVABLES FACTORING, "
            "which are often documented as a sale of future receivables rather "
            "than a loan and may appear nowhere on the balance sheet.",
            "It is a PATTERN, not a finding. Subscriptions, rent, insurance and "
            "payroll also recur. What distinguishes a funder is the short "
            "cycle. Identify the payee and ask for the agreement.",
        ],
    )

    write_sheet(
        wb, "Not screened",
        ["Row", "Raw date", "Raw amount", "Payee", "Reason"],
        bad_pay,
        widths=[8, 20, 16, 34, 30],
        notes=["Never examined by any test. Not exceptions, and not clear."],
    )

    write_sheet(
        wb, "Excluded as inflows",
        ["Row", "Date", "Signed amount", "Payee", "Reason"],
        inflows,
        widths=[8, 14, 16, 34, 40],
        notes=["Sign convention applied: %s." % sign_basis,
               "These rows were treated as money coming IN and were not "
               "screened as payments. If the convention above is wrong, "
               "re-run with --outflow-sign and these rows change side."],
    )

    write_sheet(
        wb, "Not screened, recorded",
        ["Row", "Payee", "Raw amount", "Reason"],
        bad_rec,
        widths=[8, 40, 18, 34],
        notes=["Rows in the recorded-liability file that could not be read. "
               "Each one makes a real payment look unexplained, so these "
               "INFLATE the candidate list in a direction that cannot be "
               "audited from the other sheets."],
    )

    summary = [
        ["Disbursements file", os.path.abspath(args.disbursements)],
        ["Period end", period_end.isoformat()],
        ["Payments screened (outflows)", len(payments)],
        ["Rows excluded as inflows", len(inflows)],
        ["Sign convention applied", sign_basis],
        ["Date convention applied", date_basis],
        ["Payments dated ON OR BEFORE period end (wrong file?)", len(before)],
        ["Payments NOT parsed (not screened)", len(bad_pay)],
        ["Threshold", float(threshold)],
        ["Match tolerance", float(tol)],
        ["Recurring: minimum occurrences", args.recurring_min],
        ["Recurring: maximum cycle days", args.recurring_max_gap],
        ["Recorded liabilities file", os.path.abspath(args.recorded) if args.recorded else "NOT SUPPLIED"],
        ["Recorded items read", len(recorded)],
        ["Recorded items NOT parsed", len(bad_rec)],
        ["Candidate unrecorded liabilities, ONE-OFF", len(one_off)],
        ["Value of one-off candidates", float(sum((p["amount"] for p in one_off), ZERO))],
        ["Payments that are part of a recurring series", len(repeat)],
        ["Value of recurring-series payments (a FACILITY, not a prior-period liability)",
         float(sum((p["amount"] for p in repeat), ZERO))],
        ["Explained by a recorded liability", len(explained)],
        ["Recurring fixed-debit patterns", len(rec_rows)],
        ["Control: unmatched detector", "PASS" if ctrl_unmatched else "FAIL"],
        ["Control: recurring detector", "PASS" if ctrl_recurring else "FAIL"],
        ["Usable service dates present", "yes" if has_service else "NO - period must be read off invoices"],
    ]
    write_sheet(wb, "Summary", ["Field", "Value"], summary, widths=[50, 60],
                notes=[banner])

    out = save_workbook(wb, args.output)

    print("Written: %s" % out)
    print("One-off candidate unrecorded liabilities: %d, totalling %s"
          % (len(one_off), sum((p["amount"] for p in one_off), ZERO)))
    print("Payments in a recurring series: %d, totalling %s "
          "(a facility, NOT a prior-period liability)"
          % (len(repeat), sum((p["amount"] for p in repeat), ZERO)))
    print("Recurring fixed-debit patterns: %d" % len(rec_rows))
    print("Controls: unmatched %s | recurring %s"
          % ("PASS" if ctrl_unmatched else "FAIL",
             "PASS" if ctrl_recurring else "FAIL"))
    if not ctrl_unmatched or not ctrl_recurring:
        print("")
        print("A CONTROL FAILED. Treat that detector's output as NOT SCREENED.")
    if before:
        print("")
        print("%d payment(s) are dated on or before period end. This script "
              "expects SUBSEQUENT disbursements. Check the file." % len(before))
    if not args.recorded:
        print("")
        print("No recorded-liability file supplied, so nothing was matched. "
              "Output is a worklist, not an exception list.")
    if bad_pay:
        print("")
        print("NOT SCREENED: %d payment row(s) could not be parsed." % len(bad_pay))
    if bad_rec:
        print("NOT SCREENED: %d recorded-liability row(s) could not be parsed. "
              "Each one inflates the candidate list." % len(bad_rec))
    if inflows:
        print("%d row(s) excluded as inflows (%s)." % (len(inflows), sign_basis))

    # A failed control is a failed run. Returning 0 would let a scheduler or a
    # calling script treat a broken detector as a clean result.
    if not ctrl_unmatched or not ctrl_recurring:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
