"""Run the standard analytics battery over a transaction population.

EVERY TEST CARRIES A POSITIVE CONTROL. Before a test's zero is allowed to mean
anything, a synthetic item that the test MUST catch is injected, the test is
run over the data plus the control, and the control is confirmed detected.
Control rows are then removed from the reported exceptions.

A test whose control FAILS is reported as BROKEN, and its output is reported as
NOT SCREENED rather than clear. A false negative has no downstream catch: if
you fail to look, nobody will ever know there was something to find.

Usage:
    python exception_tests.py --input "GL 2025.xlsx" --output "exceptions.xlsx"
        [--round-threshold 1000] [--approval-limit 5000]
        [--near-days 7] [--dayfirst]

Output is an EXCEPTION LIST. Exceptions are hypotheses. Nothing here is a
finding until it has been corroborated against a source document.
"""

import argparse
import math
import os
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_common import (  # noqa: E402
    ROW_KEY, new_workbook, normalize_name, parse_amount, parse_date, pick_column,
    provenance_banner, read_table, save_workbook, write_sheet,
)

ZERO = Decimal("0")
CONTROL_TAG = "ZZ-CONTROL-ROW-DO-NOT-REPORT"
# Far above any plausible cheque number, invoice number or ACH trace, so a
# control can never sit inside a real numbering chain.
CTRL_SEQ_BASE = 99000001


def month_end(d):
    if d.month == 12:
        return date(d.year, 12, 31)
    return date(d.year, d.month + 1, 1) - timedelta(days=1)


# ------------------------------------------------------------------ tests


def t_exact_duplicates(txns, cfg):
    groups = defaultdict(list)
    for t in txns:
        # Rows with no payee data are skipped. Grouping them on an empty
        # norm reported every same-date same-amount pair in the file as
        # "Same date, amount and payee" when there was no payee at all.
        if not t["norm"]:
            continue
        groups[(t["date"], t["amount"], t["norm"])].append(t)
    hits = []
    for key, items in groups.items():
        if len(items) > 1:
            for t in items:
                hits.append((t, "Same date, amount and payee as %d other row(s)"
                             % (len(items) - 1)))
    return hits


def t_near_duplicates(txns, cfg):
    groups = defaultdict(list)
    for t in txns:
        if not t["norm"]:
            continue
        groups[(t["amount"], t["norm"])].append(t)
    hits = []
    for key, items in groups.items():
        if len(items) < 2:
            continue
        items.sort(key=lambda x: x["date"])
        for i in range(len(items) - 1):
            gap = (items[i + 1]["date"] - items[i]["date"]).days
            if 0 < gap <= cfg["near_days"]:
                hits.append((items[i + 1],
                             "Same payee and amount %d day(s) after row %s"
                             % (gap, items[i]["row"])))
    return hits


def t_round_amounts(txns, cfg):
    limit = cfg["round_threshold"]
    hits = []
    for t in txns:
        a = abs(t["amount"])
        if a >= limit and a % Decimal("100") == ZERO:
            hits.append((t, "Round to the nearest 100 and at or above %s" % limit))
    return hits


def t_weekend(txns, cfg):
    hits = []
    for t in txns:
        if t["date"].weekday() >= 5:
            hits.append((t, "Dated a %s" % t["date"].strftime("%A")))
    return hits


def t_period_end(txns, cfg):
    hits = []
    for t in txns:
        me = month_end(t["date"])
        days = (me - t["date"]).days
        if days <= 2:
            hits.append((t, "Within %d day(s) of month end (%s)"
                         % (days, me.isoformat())))
    return hits


def t_threshold_proximity(txns, cfg):
    limit = cfg["approval_limit"]
    if not limit:
        return []
    floor = limit * Decimal("0.9")
    hits = []
    for t in txns:
        a = abs(t["amount"])
        if floor <= a < limit:
            hits.append((t, "Within 10 percent below the %s approval limit" % limit))
    return hits


def t_new_payee(txns, cfg):
    first_seen = {}
    for t in sorted(txns, key=lambda x: x["date"]):
        if t["norm"] and t["norm"] not in first_seen:
            first_seen[t["norm"]] = t
    # Previously this reused cfg["round_threshold"], so raising --round-
    # threshold to cut round-amount noise silently re-based this test too.
    # The Summary labelled the knob only as "Round threshold", so the
    # workpaper claimed first-payment screening was performed at a threshold
    # the operator never chose and could not see.
    limit = cfg["new_payee_threshold"]
    hits = []
    for norm, t in first_seen.items():
        if abs(t["amount"]) >= limit:
            hits.append((t, "First appearance of this payee, at or above %s" % limit))
    return hits


def t_sequence_gaps(txns, cfg):
    numbered = [t for t in txns if t["seq"] is not None]
    if len(numbered) < 3:
        return []
    numbered.sort(key=lambda x: x["seq"])
    hits = []
    seen = Counter(t["seq"] for t in numbered)
    for i in range(len(numbered) - 1):
        a, b = numbered[i]["seq"], numbered[i + 1]["seq"]
        if b - a > 1:
            hits.append((numbered[i + 1],
                         "Gap in sequence: %d missing between %d and %d"
                         % (b - a - 1, a, b)))
    for value, count in seen.items():
        if count > 1:
            for t in numbered:
                if t["seq"] == value:
                    hits.append((t, "Reference number %d used %d times" % (value, count)))
    return hits


TESTS = [
    ("Exact duplicates", t_exact_duplicates,
     "Same date, amount and payee. Genuine duplicates are common and innocent: "
     "two real payments from two payers look identical. Pull the statement "
     "line or invoice for BOTH before reporting."),
    ("Near duplicates", t_near_duplicates,
     "Same payee and amount within the window. Recurring charges are "
     "legitimately repetitive."),
    ("Round amounts", t_round_amounts,
     "Real commercial amounts carry odd cents. Transfers, rent, payroll and "
     "owner draws are legitimately round: segregate them before this means "
     "anything."),
    ("Weekend postings", t_weekend,
     "Weekend dates. Many businesses trade at weekends and many systems post "
     "with a weekend date. Low signal on its own."),
    ("Period end", t_period_end,
     "Within two days of month end. Cross-check the ENTRY date against the "
     "TRANSACTION date in the system audit trail, which is the decisive field."),
    ("Below approval limit", t_threshold_proximity,
     "Amounts sitting just under a stated approval threshold. Repetition is "
     "what makes this meaningful, not a single instance."),
    ("New payee, first payment", t_new_payee,
     "First appearance of a payee at or above the threshold. Cross-check "
     "against the vendor master: when was it added, and by whom."),
    ("Sequence gaps", t_sequence_gaps,
     "Gaps and reuse in reference or cheque numbering. Requires a numeric "
     "reference column; skipped otherwise."),
]


# ---------------------------------------------------------------- controls


def build_controls(cfg):
    """One synthetic row per test that the test MUST catch."""
    d = date(2000, 1, 8)          # a Saturday
    limit = cfg["approval_limit"] or Decimal("5000")
    controls = []

    def mk(row, dt, amount, desc, seq=None):
        return {"row": row, "date": dt, "amount": Decimal(amount),
                "desc": desc, "norm": normalize_name(desc),
                "account": "", "seq": seq, "control": True, "raw_date": "",
                "raw_amount": ""}

    controls.append(mk(-1, d, "123.45", CONTROL_TAG + " DUPE"))
    controls.append(mk(-2, d, "123.45", CONTROL_TAG + " DUPE"))
    controls.append(mk(-3, d + timedelta(days=2), "987.65", CONTROL_TAG + " NEAR"))
    controls.append(mk(-4, d, "987.65", CONTROL_TAG + " NEAR"))
    controls.append(mk(-5, d, str(cfg["round_threshold"] + Decimal("900")),
                       CONTROL_TAG + " ROUND"))
    controls.append(mk(-6, date(2000, 1, 31), "77.11", CONTROL_TAG + " PERIODEND"))
    controls.append(mk(-7, d, str((limit * Decimal("0.95")).quantize(Decimal("0.01"))),
                       CONTROL_TAG + " THRESHOLD"))
    controls.append(mk(-8, d, str(cfg["new_payee_threshold"] + Decimal("13")),
                       CONTROL_TAG + " NEWPAYEE"))
    # Sequence controls are placed FAR above any plausible real reference so
    # they cannot interleave with real data. Previously they were 900001 and
    # 900005, which are ordinary six-digit ACH traces and cheque numbers: a
    # real row at 900003 was reported with "Gap in sequence: 1 missing between
    # 900001 and 900003", a fabricated exception measured against a synthetic
    # row, while the control still reported PASS.
    # THREE numbered rows, because t_sequence_gaps requires at least three to
    # run at all. With only two the control population was below the test's
    # own minimum and the control reported FAIL on working code.
    controls.append(mk(-9, d, "10.00", CONTROL_TAG + " SEQA", seq=CTRL_SEQ_BASE))
    controls.append(mk(-11, d, "10.00", CONTROL_TAG + " SEQC", seq=CTRL_SEQ_BASE + 1))
    controls.append(mk(-10, d, "10.00", CONTROL_TAG + " SEQB", seq=CTRL_SEQ_BASE + 4))
    return controls


CONTROL_EXPECT = {
    "Exact duplicates": -1,
    "Near duplicates": -3,
    "Round amounts": -5,
    "Weekend postings": -1,
    "Period end": -6,
    "Below approval limit": -7,
    "New payee, first payment": -8,
    "Sequence gaps": -10,
}


# ----------------------------------------------------------------- benford


def benford(txns):
    digits = []
    for t in txns:
        a = abs(t["amount"])
        if a < 1:
            continue
        s = str(a).lstrip("0.")
        for ch in s:
            if ch.isdigit() and ch != "0":
                digits.append(int(ch))
                break
    n = len(digits)
    if n == 0:
        return None
    counts = Counter(digits)
    rows = []
    chi = 0.0
    mad = 0.0
    for d in range(1, 10):
        expected_p = math.log10(1 + 1.0 / d)
        expected_n = expected_p * n
        observed_n = counts.get(d, 0)
        observed_p = observed_n / n
        if expected_n > 0:
            chi += (observed_n - expected_n) ** 2 / expected_n
        mad += abs(observed_p - expected_p)
        rows.append([d, observed_n, round(observed_p * 100, 2),
                     round(expected_n, 1), round(expected_p * 100, 2),
                     round((observed_p - expected_p) * 100, 2)])
    return {"n": n, "rows": rows, "chi": round(chi, 2), "mad": round(mad / 9, 5)}


def benford_controls():
    """Positive and negative control for the Benford implementation.

    Positive: a set constructed to follow Benford should score a LOW MAD.
    Negative: a uniform set should score a clearly HIGHER MAD.
    If the two are not separated, the implementation cannot distinguish them
    and its output about real data means nothing.
    """
    conforming = []
    for d in range(1, 10):
        count = int(round(math.log10(1 + 1.0 / d) * 3000))
        for i in range(count):
            conforming.append({"amount": Decimal("%d%03d.00" % (d, i % 1000))})
    uniform = []
    for d in range(1, 10):
        for i in range(333):
            uniform.append({"amount": Decimal("%d%03d.00" % (d, i % 1000))})
    good = benford(conforming)
    bad = benford(uniform)
    ok = bool(good and bad and good["mad"] < bad["mad"] / 2)
    return ok, (good["mad"] if good else None), (bad["mad"] if bad else None)


# -------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--round-threshold", type=str, default="1000")
    ap.add_argument("--new-payee-threshold", type=str, default="",
                    help="Materiality floor for the first-payment test. "
                         "Defaults to --round-threshold, and is recorded "
                         "separately in the output.")
    ap.add_argument("--approval-limit", type=str, default="")
    ap.add_argument("--near-days", type=int, default=7)
    ap.add_argument("--dayfirst", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        raise SystemExit("File not found: %s" % args.input)

    try:
        cfg = {
            "round_threshold": Decimal(args.round_threshold),
            "new_payee_threshold": Decimal(args.new_payee_threshold
                                           or args.round_threshold),
            "approval_limit": Decimal(args.approval_limit) if args.approval_limit else None,
            "near_days": args.near_days,
        }
    except Exception:
        raise SystemExit("--round-threshold, --new-payee-threshold and "
                         "--approval-limit must be plain numbers with no "
                         "thousands separators.")

    headers, rows = read_table(args.input)
    date_col = pick_column(headers, ["date", "transaction date", "posting date"],
                           label="date")
    amt_col = pick_column(headers, ["amount", "value", "total"], label="amount")
    desc_col = pick_column(headers, ["description", "payee", "name", "memo",
                                     "vendor", "details"], required=False)
    acct_col = pick_column(headers, ["account", "gl account", "category"],
                           required=False)
    seq_col = pick_column(headers, ["num", "number", "reference", "check",
                                    "cheque", "invoice"], required=False)

    txns = []
    not_screened = []
    for row in rows:
        i = row.get(ROW_KEY)
        d = parse_date(row.get(date_col), dayfirst=args.dayfirst)
        a = parse_amount(row.get(amt_col))
        if d is None or a is None:
            not_screened.append([i, str(row.get(date_col)), str(row.get(amt_col)),
                                 str(row.get(desc_col) or ""),
                                 "Unparsable date" if d is None else "Unparsable amount"])
            continue
        seq = None
        if seq_col:
            raw = str(row.get(seq_col) or "").strip()
            if raw.isdigit():
                seq = int(raw)
        desc = str(row.get(desc_col) or "").strip() if desc_col else ""
        txns.append({
            "row": i, "date": d, "amount": a, "desc": desc,
            "norm": normalize_name(desc),
            "account": str(row.get(acct_col) or "").strip() if acct_col else "",
            "seq": seq, "control": False,
        })

    # THE BUG THIS GUARDS: the ten control rows are self-sufficient. They
    # duplicate each other, recur against each other, and carry their own
    # sequence gap. With an empty transaction population every control was
    # still detected, so all eight tests printed "control PASS | 0
    # exception(s)" and the sheets asserted "a zero from this test is
    # meaningful". The run examined nothing and certified eight meaningful
    # zeros, at exit code 0.
    if not txns:
        raise SystemExit(
            "Zero usable transaction rows were read from %s (%d row(s) were "
            "unparsable).\n"
            "Nothing was examined. This is an instrument failure, not a clean "
            "result: with no population every test trivially finds nothing "
            "while its control still passes on the synthetic rows."
            % (args.input, len(not_screened)))

    controls = build_controls(cfg)
    population = txns + controls

    wb = new_workbook()
    # The resolved column names belong in the banner. Without them nobody can
    # establish which field a sheet was computed over, which for an
    # evidence-grade deliverable is a provenance failure, not a convenience
    # gap. The sibling scripts already record their basis.
    banner = provenance_banner(
        "exception_tests.py",
        "round_threshold=%s; new_payee_threshold=%s; approval_limit=%s; "
        "near_days=%d; rows=%d; columns used: date='%s', amount='%s', "
        "description='%s', account='%s', reference='%s'" % (
            cfg["round_threshold"], cfg["new_payee_threshold"],
            cfg["approval_limit"], cfg["near_days"], len(txns),
            date_col, amt_col, desc_col or "(none)", acct_col or "(none)",
            seq_col or "(none)"),
    )

    control_rows = []
    summary_counts = []

    for name, fn, caution in TESTS:
        # Two separate runs. The control population never touches the real
        # one, so a synthetic row cannot generate an exception against real
        # data (control sequence values once sat inside the real numbering
        # chain and produced fabricated gap and duplicate-reference findings
        # while still reporting PASS), and a real row cannot accidentally
        # satisfy a control.
        hits = fn(txns, cfg)
        ctrl_hits = fn(controls, cfg)

        expected = CONTROL_EXPECT.get(name)
        detected_rows = {t["row"] for t, _ in ctrl_hits}
        if name == "Sequence gaps" and not any(t["seq"] is not None for t in txns):
            control_status = "NOT RUN"
            control_note = ("No numeric reference column in the input, so this "
                            "test was skipped entirely. Its result is NOT "
                            "SCREENED, not clear.")
        elif name == "Below approval limit" and not cfg["approval_limit"]:
            control_status = "NOT RUN"
            control_note = ("No --approval-limit supplied, so this test was "
                            "skipped. Ask for the delegated authority policy.")
        elif expected is not None and expected in detected_rows:
            control_status = "PASS"
            control_note = "Control row detected. A zero from this test is meaningful."
        else:
            control_status = "FAIL"
            control_note = ("Control row NOT detected. This test is BROKEN. "
                            "Treat its population as NOT SCREENED.")

        control_rows.append([name, control_status, control_note])

        real_hits = [(t, why) for t, why in hits if not t["control"]]
        leaked = [t for t, _ in hits if t["control"]]
        if leaked:
            raise SystemExit(
                "A control row reached the '%s' results. Controls must never "
                "appear in reported output. Rows: %s"
                % (name, ", ".join(str(t["row"]) for t in leaked)))
        sheet_rows = [[
            t["row"], t["date"].isoformat(), float(t["amount"]), t["desc"],
            t["account"], t["seq"], why, "", "", "",
        ] for t, why in sorted(real_hits, key=lambda x: (x[0]["date"], x[0]["row"]))]

        write_sheet(
            wb, name,
            ["Source row", "Date", "Amount", "Description", "Account",
             "Reference", "Why flagged", "Source document examined",
             "Innocent explanation considered", "Finding or open question"],
            sheet_rows,
            widths=[12, 13, 15, 40, 22, 12, 46, 34, 40, 30],
            notes=[
                banner,
                "CONTROL: %s. %s" % (control_status, control_note),
                "CAUTION: %s" % caution,
                "The last three columns are filled in by the examiner. An item "
                "with them blank has NOT cleared the corroboration gate and "
                "must not be reported as a finding.",
            ],
        )
        summary_counts.append([name, control_status, len(real_hits), "exception(s)"])

    # Benford
    b = benford(txns)
    b_ok, good_mad, bad_mad = benford_controls()
    if b:
        write_sheet(
            wb, "Benford",
            ["Leading digit", "Observed count", "Observed %", "Expected count",
             "Expected %", "Difference (pp)"],
            b["rows"],
            widths=[16, 18, 14, 16, 14, 18],
            notes=[
                "Population: %d amounts with a leading digit. Chi-square %s, "
                "MAD %s." % (b["n"], b["chi"], b["mad"]),
                "CONTROL: %s. A Benford-conforming synthetic set scored MAD %s; "
                "a uniform synthetic set scored %s. The test can distinguish "
                "them." % ("PASS" if b_ok else "FAIL", good_mad, bad_mad),
                "CAUTION: this is one of the WEAKEST signals available. It is a "
                "direction to look, never evidence. It fails legitimately on "
                "assigned numbers, price points, thresholds, bounded ranges and "
                "small samples. Never put a Benford result in a report as "
                "support for a conclusion about a person.",
                "Populations under a few hundred items are not worth reading."
                if b["n"] < 300 else "",
            ],
        )
        # Benford yields a DISTRIBUTION, never an exception list. Labelling
        # its population as "exceptions" would overstate it by the whole
        # population, which is exactly the mislabelling this skill exists to
        # prevent.
        summary_counts.append(["Benford", "PASS" if b_ok else "FAIL", b["n"],
                               "amount(s) analyzed, no exception list produced"])

    write_sheet(
        wb, "Controls",
        ["Test", "Control result", "What it means"],
        control_rows,
        widths=[30, 16, 86],
        notes=["A test whose control FAILED has told you about the test, not "
               "about the data. Its population is NOT SCREENED."],
    )

    write_sheet(
        wb, "Not screened",
        ["Source row", "Raw date", "Raw amount", "Description", "Reason"],
        not_screened,
        widths=[12, 22, 18, 40, 34],
        notes=["These rows were NEVER EXAMINED by any test. They are not "
               "exceptions and they are not clear. Fix the input and re-run, "
               "or report them as unscreened with the count stated."],
    )

    summary = [["Input", os.path.abspath(args.input)],
               ["Rows read", len(rows)],
               ["Rows screened", len(txns)],
               ["Rows NOT screened", len(not_screened)],
               ["Round threshold", float(cfg["round_threshold"])],
               ["New-payee threshold", float(cfg["new_payee_threshold"])],
               ["Approval limit", float(cfg["approval_limit"]) if cfg["approval_limit"] else "not supplied"],
               ["Near-duplicate window (days)", cfg["near_days"]],
               ["", ""],
               ["TEST", "CONTROL / COUNT"]]
    for name, status, count, noun in summary_counts:
        summary.append([name, "%s | %d %s" % (status, count, noun)])
    write_sheet(wb, "Summary", ["Field", "Value"], summary, widths=[42, 52],
                notes=[banner])

    out = save_workbook(wb, args.output)

    print("Exception tests written: %s" % out)
    print("Rows screened: %d | not screened: %d" % (len(txns), len(not_screened)))
    print("")
    for name, status, count, noun in summary_counts:
        print("  %-28s control %-8s %d %s" % (name, status, count, noun))
    failed = [n for n, s, _, _ in summary_counts if s == "FAIL"]
    skipped = [n for n, s, _, _ in summary_counts if s == "NOT RUN"]
    if failed:
        print("")
        print("CONTROL FAILURES: %s" % ", ".join(failed))
        print("Those tests are broken. Do not report their zeros as clear.")
    if skipped:
        print("")
        print("NOT RUN: %s" % ", ".join(skipped))
    print("")
    print("Every row above is a HYPOTHESIS. Nothing is a finding until it has "
          "been corroborated against a source document.")

    # A failed control is a failed run. Exiting 0 let a caller or a scheduler
    # treat a broken detector as a clean population.
    if failed:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
