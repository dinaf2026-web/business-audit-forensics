"""Diff a prior period's CLOSING balances against the current period's OPENING
balances, and flag every account that moved without a documented entry.

This is the highest-yield procedure in the skill. A set of books can tie
internally, balance perfectly, and pass every within-period test while the
balances it STARTS with silently contradict how the prior period ENDED. That
discrepancy is invisible from inside either year.

Usage:
    python rollforward_diff.py --prior "2024 closing TB.xlsx" \\
                               --current "2025 opening TB.xlsx" \\
                               --output "rollforward.xlsx"

Input files may be CSV or XLSX and need an account column plus either a single
balance column or separate debit and credit columns. Column names are detected
automatically; override with --account-col / --balance-col / --debit-col /
--credit-col.

Every difference this reports is a QUESTION, not a finding. The question is
always the same: "show me the entry behind this."
"""

import argparse
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_common import (  # noqa: E402
    new_workbook, parse_amount, pick_column, provenance_banner, read_table,
    save_workbook, write_sheet,
)

ZERO = Decimal("0")
TOL = Decimal("0.01")

# ORDER MATTERS AND IS LOAD-BEARING.
#
# LIABILITY is tested BEFORE EQUITY on purpose. An account called "Member
# Loans" is a liability, and an account called "Members Draw" is equity. If
# EQUITY were tested first, the bare word "member" would claim both, both
# sides of a liability-into-equity reclassification would classify as EQUITY,
# and the CROSS-CLASS flag - the single most valuable output of this script -
# would never fire. That is a real bug that was caught by a planted test case,
# not a hypothetical.
#
# For the same reason the EQUITY list contains no bare "member", "partner" or
# "owner". Those words describe WHO, not WHAT, and they appear on both sides
# of the line.
CLASS_KEYWORDS = [
    # INCOME and EXPENSE are tested FIRST, on explicit words only. The ASSET
    # list contains 'depreciation', 'bank', 'vehicle', 'property', 'equipment'
    # and 'deposit', so with ASSET earlier in the order "Depreciation Expense",
    # "Bank Fees", "Vehicle Expense" and "Property Tax Expense" all classified
    # as ASSET. Same ordering defect as the EQUITY-before-LIABILITY bug, one
    # level down.
    ("EXPENSE", ("expense", "cost of", "cogs", "payroll expense", "fees",
                 "amortization", "depreciation expense")),
    ("INCOME", ("income", "revenue", "sales", "royalt", "earned")),
    ("LIABILITY", ("loan", "note payable", "payable", "liability", "accrued",
                   "debt", "mortgage", "line of credit", "credit card",
                   "deferred", "due to", "owed")),
    ("EQUITY", ("equity", "capital", "retained", "draw", "distribution",
                "contribution", "stock", "surplus", "dividend",
                "members equity", "owners equity", "partners equity")),
    ("ASSET", ("cash", "bank", "checking", "savings", "receivable",
               "inventory", "prepaid", "equipment", "vehicle", "property",
               "asset", "depreciation", "due from", "deposit")),
    ("EXPENSE_TAIL", ("payroll", "rent", "utilities", "insurance",
                      "subscription", "interest")),
]

SUSPENSE_HINTS = ("suspense", "clearing", "ask my accountant", "uncategorized",
                  "undeposited", "opening balance equity", "unapplied")


def classify(name):
    """Heuristic account classification from the account NAME.

    It is a guess, and the examiner must check it. A misnamed account is one
    of the things this script exists to surface, and a misnamed account will
    by definition classify wrongly here. "Loans to Members" is an asset and
    will read as LIABILITY; that is the known limit of name-based
    classification.
    """
    low = str(name or "").lower()
    for label, keys in CLASS_KEYWORDS:
        for key in keys:
            if key in low:
                return "EXPENSE" if label == "EXPENSE_TAIL" else label
    return "UNKNOWN"


def is_suspense(name):
    low = str(name or "").lower()
    return any(h in low for h in SUSPENSE_HINTS)


def load_balances(path, args, which):
    headers, rows = read_table(path)
    acct_col = args.account_col or pick_column(
        headers, ["account", "account name", "description", "name", "gl account"],
        label="%s account" % which)

    bal_col = args.balance_col
    deb_col = args.debit_col
    cre_col = args.credit_col
    # Validate any explicit override against THIS file's headers. Applying an
    # override blindly to both files meant that if the second file used a
    # different header, every row was skipped and every prior account was
    # reported DISAPPEARED: hundreds of false findings from one typo.
    for label_, col in (("--account-col", args.account_col),
                        ("--balance-col", args.balance_col),
                        ("--debit-col", args.debit_col),
                        ("--credit-col", args.credit_col)):
        if col and col not in headers:
            raise SystemExit(
                "%s was given as '%s' but that column is not in the %s file.\n"
                "Columns present: %s" % (label_, col, which, ", ".join(headers)))

    if bool(args.debit_col) != bool(args.credit_col):
        raise SystemExit(
            "--debit-col and --credit-col must be supplied together. Given "
            "only one, the other was silently auto-detected or ignored.")

    if not bal_col and not (deb_col and cre_col):
        # "amount" previously matched inside "Debit Amount", which made this
        # branch truthy and left the paired debit/credit branch unreachable.
        # Every credit-side row then failed to parse and was dropped, so on a
        # standard TB the entire liability and equity side vanished, which is
        # the only place a liability-into-equity reclassification can appear.
        bal_col = pick_column(
            headers, ["balance", "ending balance", "closing balance", "total"],
            required=False, label="%s balance" % which,
            exclude=("debit", "credit"))
        if not bal_col:
            bal_col = pick_column(headers, ["amount"], required=False,
                                  exclude=("debit", "credit"))
        if not bal_col:
            deb_col = pick_column(headers, ["debit"], required=False,
                                  exclude=("credit",))
            cre_col = pick_column(headers, ["credit"], required=False,
                                  exclude=("debit",))
    if not bal_col and not (deb_col and cre_col):
        raise SystemExit(
            "Could not find a balance column (or debit and credit columns) in "
            "%s. Columns present: %s" % (path, ", ".join(headers)))

    balances = {}
    raw_names = {}
    skipped = 0
    for row in rows:
        name = str(row.get(acct_col) or "").strip()
        if not name:
            skipped += 1
            continue
        if bal_col:
            amount = parse_amount(row.get(bal_col))
        else:
            debit = parse_amount(row.get(deb_col)) or ZERO
            credit = parse_amount(row.get(cre_col)) or ZERO
            amount = debit - credit
        if amount is None:
            skipped += 1
            continue
        key = name.upper()
        balances[key] = balances.get(key, ZERO) + amount
        raw_names.setdefault(key, name)

    basis = ("balance column '%s'" % bal_col) if bal_col else (
        "debit '%s' less credit '%s'" % (deb_col, cre_col))
    return balances, raw_names, basis, skipped


def find_reclass_pairs(moves):
    """Pair a decrease in one account against an equal increase in another.

    A liability that closed one year and opens the next inside equity is the
    signature this exists to catch. Matching on absolute value only; the pair
    is a HYPOTHESIS requiring the journal entry to confirm.
    """
    pairs = []
    ambiguous = []
    decreases = [m for m in moves if m["delta"] < -TOL]
    increases = [m for m in moves if m["delta"] > TOL]
    used = set()
    for dec in decreases:
        target = -dec["delta"]
        cands = [inc for inc in increases
                 if inc["key"] not in used and abs(inc["delta"] - target) <= TOL]
        if not cands:
            continue
        if len(cands) > 1:
            # REFUSE to pair. The previous version took the first candidate in
            # alphabetical order regardless of class, so an unrelated refinance
            # of the same amount could claim the equity account and produce a
            # fabricated CROSS-CLASS row, while the genuine liability-into-
            # equity movement was left paired with the refinance and labelled
            # "same class". That both invents the headline finding and
            # suppresses it.
            ambiguous.append((dec, cands))
            continue
        # Prefer a cross-class partner when exactly one exists, since that is
        # the movement this script exists to surface.
        inc = cands[0]
        pairs.append((dec, inc))
        used.add(inc["key"])
    return pairs, ambiguous


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prior", required=True, help="Prior period CLOSING balances")
    ap.add_argument("--current", required=True, help="Current period OPENING balances")
    ap.add_argument("--output", required=True, help="Output .xlsx")
    ap.add_argument("--account-col")
    ap.add_argument("--balance-col")
    ap.add_argument("--debit-col")
    ap.add_argument("--credit-col")
    args = ap.parse_args()

    for path in (args.prior, args.current):
        if not os.path.isfile(path):
            raise SystemExit("File not found: %s" % path)

    if os.path.abspath(args.prior) == os.path.abspath(args.current):
        raise SystemExit(
            "--prior and --current point at the same file. Every account would "
            "agree with itself and the run would report a clean roll-forward.")

    prior, prior_names, prior_basis, prior_skipped = load_balances(args.prior, args, "prior")
    current, current_names, current_basis, current_skipped = load_balances(args.current, args, "current")

    if not prior or not current:
        raise SystemExit(
            "Zero usable balances on the %s side (prior %d, current %d).\n"
            "Nothing was compared. This is an instrument failure, not a clean "
            "roll-forward." % ("prior" if not prior else "current",
                               len(prior), len(current)))

    all_keys = sorted(set(prior) | set(current))
    rows = []
    moves = []
    flagged = 0

    for key in all_keys:
        p = prior.get(key)
        c = current.get(key)
        name = prior_names.get(key) or current_names.get(key)
        klass = classify(name)

        if p is None:
            delta = c
            status = "NEW ACCOUNT"
        elif c is None:
            delta = -p
            status = "DISAPPEARED"
        else:
            delta = c - p
            status = "MOVED" if abs(delta) > TOL else "agrees"

        flags = []
        if status != "agrees":
            flags.append(status)
        if p is not None and c is not None and p != ZERO and c != ZERO:
            if (p > ZERO) != (c > ZERO):
                flags.append("SIGN FLIP")
        if is_suspense(name) and (c or ZERO) != ZERO:
            flags.append("SUSPENSE BALANCE")
        if klass == "UNKNOWN":
            flags.append("UNCLASSIFIED")

        if status != "agrees":
            moves.append({"key": key, "name": name, "class": klass,
                          "delta": delta or ZERO, "prior": p, "current": c})
            flagged += 1

        rows.append([
            name, klass,
            float(p) if p is not None else None,
            float(c) if c is not None else None,
            float(delta) if delta is not None else None,
            status,
            "; ".join(flags),
            "",
        ])

    rows.sort(key=lambda r: (r[5] == "agrees", -abs(r[4] or 0)))

    pairs, amb_pairs = find_reclass_pairs(moves)

    wb = new_workbook()
    banner = provenance_banner(
        "rollforward_diff.py",
        "prior=%s (%s); current=%s (%s)" % (
            os.path.basename(args.prior), prior_basis,
            os.path.basename(args.current), current_basis),
    )

    write_sheet(
        wb, "Roll-forward",
        ["Account", "Class", "Prior closing", "Current opening", "Difference",
         "Status", "Flags", "Entry behind it (fill in)"],
        rows,
        widths=[42, 12, 16, 16, 16, 14, 30, 40],
        flag_col=6,
        notes=[
            banner,
            "Every non-zero Difference needs a journal entry explaining it. "
            "An opening balance that cannot be traced to a closing balance "
            "plus a documented entry is an OPEN QUESTION, not a finding.",
            "THE CLASS COLUMN IS A GUESS from the account NAME, not a fact. "
            "Check it before relying on it. A misnamed account is one of the "
            "things this script exists to surface, and a misnamed account "
            "will by definition classify wrongly here. 'Loans to Members' is "
            "an asset and will read as LIABILITY.",
        ],
    )

    pair_rows = []
    for dec, inc in pairs:
        cross_class = dec["class"] != inc["class"]
        pair_rows.append([
            dec["name"], dec["class"], float(dec["delta"]),
            inc["name"], inc["class"], float(inc["delta"]),
            float(abs(dec["delta"])),
            "CROSS-CLASS" if cross_class else "same class",
            "Liability or asset moved into equity changes basis and may change "
            "whether later payments to an owner are taxable. Confirm with a CPA."
            if cross_class else "",
        ])

    write_sheet(
        wb, "Possible reclassifications",
        ["Account decreased", "Class", "Decrease", "Account increased",
         "Class", "Increase", "Amount", "Type", "Why it matters"],
        pair_rows,
        widths=[34, 12, 15, 34, 12, 15, 15, 14, 52],
        flag_col=7,
        notes=[
            "Equal and opposite movements, paired on amount alone. These are "
            "HYPOTHESES. A pair proves nothing without the journal entry. "
            "CROSS-CLASS pairs are the ones that matter most.",
        ],
    )

    amb_rows = []
    for dec, cands in amb_pairs:
        amb_rows.append([
            dec["name"], dec["class"], float(dec["delta"]),
            "; ".join("%s (%s, %+.2f)" % (c["name"], c["class"], c["delta"])
                      for c in cands),
            len(cands),
            "NOT PAIRED. More than one account moved by this amount, so any "
            "pairing would be arbitrary. Read these by hand: picking one "
            "would both invent a relationship and hide the real one.",
        ])
    write_sheet(
        wb, "Ambiguous pairings",
        ["Account decreased", "Class", "Decrease", "Candidate increases",
         "Candidates", "Why it was not paired"],
        amb_rows,
        widths=[34, 12, 15, 60, 12, 60],
        notes=["Equal-and-opposite movements where the partner is not unique. "
               "These are deliberately left unpaired."],
    )

    prior_total = sum(prior.values(), ZERO)
    current_total = sum(current.values(), ZERO)
    summary = [
        ["Prior file", os.path.abspath(args.prior)],
        ["Prior basis", prior_basis],
        ["Prior accounts", len(prior)],
        ["Prior total (should be ~0 for a balanced TB)", float(prior_total)],
        ["Current file", os.path.abspath(args.current)],
        ["Current basis", current_basis],
        ["Current accounts", len(current)],
        ["Current total (should be ~0 for a balanced TB)", float(current_total)],
        ["Accounts compared", len(all_keys)],
        ["Accounts that moved or appeared or disappeared", flagged],
        ["Accounts that agree", len(all_keys) - flagged],
        ["Possible reclassification pairs", len(pairs)],
        ["Ambiguous, deliberately NOT paired", len(amb_rows)],
        ["Tolerance suppressing differences below", float(TOL)],
        ["Rows skipped, prior (no account or unparsable amount)", prior_skipped],
        ["Rows skipped, current", current_skipped],
    ]
    write_sheet(wb, "Summary", ["Field", "Value"], summary, widths=[52, 60])

    out = save_workbook(wb, args.output)

    print("Roll-forward written: %s" % out)
    print("Accounts compared: %d" % len(all_keys))
    print("Moved / new / disappeared: %d" % flagged)
    print("Possible reclassification pairs: %d" % len(pairs))
    cross = sum(1 for d, i in pairs if d["class"] != i["class"])
    if cross:
        print("")
        print("%d CROSS-CLASS pair(s). Look at these first." % cross)
    if prior_skipped or current_skipped:
        print("")
        print("NOT SCREENED: %d prior and %d current rows were skipped."
              % (prior_skipped, current_skipped))
        print("Those rows were never compared. Check them before relying on this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
