"""Shared helpers for the business-audit-forensics scripts.

Dependencies: openpyxl only (python-docx for the report builder).
No pandas, deliberately, so the scripts run anywhere with a minimal install.

Design rules enforced here:
  - Files are written to a .tmp in the same directory and then os.replace'd,
    so a failure never leaves a truncated output and never destroys a prior one.
  - Hashes are taken over RAW BYTES. A decoded round-trip can alter bytes and
    produce a false "this file changed".
  - A missing file is a failure, never a match.
  - Every sheet is written at a 12pt floor.
"""

import csv
import hashlib
import os
import re
from datetime import datetime, date, timedelta
from decimal import Decimal, InvalidOperation

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# Key under which every record carries its TRUE source row.
ROW_KEY = "__source_row__"

FONT_NAME = "Arial"
BODY_PT = 12
HEADER_PT = 12
TITLE_PT = 16

HEADER_FILL = PatternFill("solid", fgColor="D9D9D9")
FLAG_FILL = PatternFill("solid", fgColor="FFF2CC")
BAD_FILL = PatternFill("solid", fgColor="F8CBAD")
GOOD_FILL = PatternFill("solid", fgColor="E2EFDA")

THIN = Side(style="thin", color="999999")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


# ---------------------------------------------------------------- hashing


def sha256_file(path, chunk=1024 * 1024):
    """SHA-256 over raw bytes. Raises if the file does not exist."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def hashes_match(path_a, path_b):
    """True only if both files exist and hash identically.

    Two missing files are NOT a match.
    """
    if not (os.path.isfile(path_a) and os.path.isfile(path_b)):
        return False
    return sha256_file(path_a) == sha256_file(path_b)


# ------------------------------------------------------------ parsing


_DATE_FORMATS = (
    "%Y-%m-%d", "%Y/%m/%d",
    "%m/%d/%Y", "%m-%d-%Y",
    "%d/%m/%Y", "%d-%m-%Y",
    "%m/%d/%y", "%m-%d-%y",
    "%d/%m/%y", "%d-%m-%y",
    "%b %d, %Y", "%d %b %Y", "%B %d, %Y",
)

_DMY_SPLIT = re.compile(r"^\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\s*$")


def detect_dayfirst(values, default=False):
    """Decide the date convention ONCE for a whole column.

    Returns (dayfirst, basis_string).

    THE BUG THIS REPLACES: parse_date tries formats per value, so a single
    column could be read both ways in one run. '13/05/2026' parsed day-first
    because month 13 failed, while '03/05/2026' two rows later parsed
    month-first. Roughly 40% of rows landed in the wrong month with no warning.

    Evidence: any value whose FIRST component exceeds 12 proves day-first; any
    whose SECOND component exceeds 12 proves month-first. Contradictory
    evidence is refused rather than guessed.
    """
    first_gt12 = second_gt12 = 0
    for v in values:
        if v is None:
            continue
        m = _DMY_SPLIT.match(str(v))
        if not m:
            continue
        a, b = int(m.group(1)), int(m.group(2))
        if a > 12:
            first_gt12 += 1
        if b > 12:
            second_gt12 += 1

    if first_gt12 and second_gt12:
        raise SystemExit(
            "This date column contains BOTH values whose first component "
            "exceeds 12 (%d rows, proving day-first) and values whose second "
            "component exceeds 12 (%d rows, proving month-first). The column "
            "is internally inconsistent and cannot be parsed safely. Fix the "
            "export or split the file." % (first_gt12, second_gt12))
    if first_gt12:
        return True, "day-first, proven by %d row(s) with a first component over 12" % first_gt12
    if second_gt12:
        return False, "month-first, proven by %d row(s) with a second component over 12" % second_gt12
    return default, ("no row proves the convention, so the %s default was used"
                     % ("day-first" if default else "month-first"))


def parse_date(value, dayfirst=False):
    """Return a date, or None. Ambiguous values follow the dayfirst flag.

    Day-first and month-first are indistinguishable for the first twelve days
    of any month. The caller decides, and the choice is recorded in the output.
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    order = list(_DATE_FORMATS)
    if dayfirst:
        order.remove("%d/%m/%Y")
        order.remove("%d-%m-%Y")
        order.remove("%d/%m/%y")
        order.insert(0, "%d/%m/%Y")
        order.insert(1, "%d-%m-%Y")
        order.insert(2, "%d/%m/%y")
    for fmt in order:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


_AMOUNT_STRIP = re.compile(r"[^0-9.,\-()]")
_TRAILING_MINUS = re.compile(r"^([0-9.,]+)-$")


def parse_amount(value):
    """Return a Decimal, or None.

    Handles currency symbols, thousands separators, (123.45) negatives and
    trailing-minus. Detects the decimal convention rather than assuming US.

    THE BUG THIS REPLACES: the previous version deleted every comma and then
    parsed what remained as US format, so '1.234,56' became 1.23456 and
    '1 234,56' became 123456. It never failed, so a European or
    comma-decimal export was silently mis-scaled by 10x to 1000x and every
    downstream total inherited it with no signal anywhere.

    Convention detection:
      - both separators present -> the LAST one is the decimal mark
      - only ',' present, followed by exactly 3 digits at end -> thousands
      - only ',' present, followed by 1 or 2 digits at end    -> decimal
      - only ',' present, appearing more than once            -> thousands
    An input whose separators are internally inconsistent returns None rather
    than a guess.
    """
    if value is None or value == "":
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None

    text = str(value).strip()
    if not text:
        return None

    negative = (text.startswith("(") and text.endswith(")")) or text.endswith("-")
    text = _AMOUNT_STRIP.sub("", text).replace("(", "").replace(")", "")
    m = _TRAILING_MINUS.match(text)
    if m:
        text = m.group(1)
    if text.startswith("-"):
        negative = True
        text = text[1:]
    text = text.replace("-", "")
    if text in ("", ".", ","):
        return None

    last_dot = text.rfind(".")
    last_comma = text.rfind(",")

    if last_dot >= 0 and last_comma >= 0:
        if last_comma > last_dot:
            # 1.234,56  -> comma is the decimal mark
            if text.count(",") > 1:
                return None
            text = text.replace(".", "").replace(",", ".")
        else:
            # 1,234.56  -> dot is the decimal mark
            if text.count(".") > 1:
                return None
            text = text.replace(",", "")
    elif last_comma >= 0:
        tail = len(text) - last_comma - 1
        if text.count(",") > 1 or tail == 3:
            text = text.replace(",", "")          # thousands
        elif tail in (1, 2):
            text = text.replace(",", ".")         # decimal
        else:
            text = text.replace(",", "")
    # dot-only, or neither: already usable

    if text.count(".") > 1:
        return None
    try:
        amount = Decimal(text)
    except InvalidOperation:
        return None
    return -amount if negative else amount


def normalize_name(value):
    """Canonical form for matching. The RAW value is always kept separately."""
    if value is None:
        return ""
    text = str(value).upper()
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = re.sub(r"\b(INC|LLC|LTD|CO|CORP|COMPANY|THE)\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# ------------------------------------------------------------ table input


def read_table(path, sheet=None, header_contains=None):
    """Read a CSV or XLSX into (headers, rows-as-dicts).

    Values come back raw. Parsing is the caller's job, so that the raw value
    is always available for the workpaper.

    header_contains: a list of column names that the real header row must
    contain. REQUIRED when reading back a sheet this toolkit wrote, because
    those sheets carry explanatory notes ABOVE the header. Without it the
    first note line is taken as the header, every lookup returns nothing, and
    the caller silently compares an empty set - which looks exactly like a
    clean result. That bug was real; this parameter is the fix.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".txt", ".tsv"):
        delim = "\t" if ext == ".tsv" else ","
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh, delimiter=delim)
            headers = list(reader.fieldnames or [])
            rows = []
            for rec in reader:
                d = dict(rec)
                # TRUE file row, so a "Source row" citation in a workpaper
                # lands on the right line. Callers previously used
                # enumerate(start=2), which drifts by one for every blank row
                # the reader skips: a GL with a separator row between months
                # offset every subsequent citation.
                d[ROW_KEY] = reader.line_num
                rows.append(d)
        # header_contains was previously enforced for XLSX only, so a caller
        # asking for validation on a CSV got none and no error. That left the
        # single guard against reading a note line as a header with a hole in
        # half its input space.
        if header_contains:
            present = set(headers)
            missing = [w for w in header_contains if w not in present]
            if missing:
                raise SystemExit(
                    "Expected header column(s) %s not found in %s. Headers "
                    "read: %s. Refusing to continue: reading the wrong row as "
                    "a header would compare an empty set and report it as "
                    "clean." % (", ".join(missing), path, ", ".join(headers)))
            if not rows:
                raise SystemExit(
                    "%s has the expected headers but zero data rows. Refusing "
                    "to continue: a comparison against nothing is not a clean "
                    "result." % path)
        return headers, rows

    if ext in (".xlsx", ".xlsm"):
        # Walked by explicit row index rather than by iterator position, so
        # every record carries its TRUE sheet row. Callers previously numbered
        # records with enumerate(start=2), which drifts by one for every blank
        # row skipped, so a "Source row" citation in a workpaper pointed at
        # the wrong line.
        wb = load_workbook(path, data_only=True)
        ws = wb[sheet] if sheet else wb[wb.sheetnames[0]]
        out = []
        header_row = None
        headers = []
        for r in range(1, ws.max_row + 1):
            values = [ws.cell(row=r, column=c).value
                      for c in range(1, ws.max_column + 1)]
            if not any(v is not None and str(v).strip() for v in values):
                continue
            candidate = [str(v).strip() if v is not None else "" for v in values]
            if header_contains:
                present = set(candidate)
                if not all(w in present for w in header_contains):
                    continue
            headers = candidate
            header_row = r
            break

        if header_contains and header_row is None:
            wb.close()
            raise SystemExit(
                "Could not find a header row containing %s in sheet '%s' of %s. "
                "Refusing to continue: reading the wrong row as a header would "
                "compare an empty set and report it as clean."
                % (", ".join(header_contains), sheet or "(first)", path))
        if header_row is None:
            wb.close()
            return [], []

        for r in range(header_row + 1, ws.max_row + 1):
            values = [ws.cell(row=r, column=c).value
                      for c in range(1, ws.max_column + 1)]
            if not any(v is not None and str(v).strip() != "" for v in values):
                continue
            record = {}
            for i, head in enumerate(headers):
                record[head] = values[i] if i < len(values) else None
            record[ROW_KEY] = r
            out.append(record)
        wb.close()
        return headers, out

    raise ValueError("Unsupported table format: %s" % ext)


def pick_column(headers, candidates, required=True, label="", exclude=()):
    """Find a column by exact then word-boundary match against candidates.

    exclude: reject any header containing one of these words, even on an
    otherwise good match. Used to stop a generic candidate such as "amount"
    binding to "Debit Amount" when a paired debit/credit branch exists.

    THE BUG THIS REPLACES: the fallback was a bare substring test in header
    order, so ["debit","dr"] bound to "Doc Address" and ["num","number"] bound
    to "Account Number". Combined with a permissive amount parser, a text
    column then produced numbers instead of failing, and the run reported
    almost nothing unparsable.
    """
    lowered = {h.lower().strip(): h for h in headers if h}
    blocked = tuple(e.lower() for e in exclude)

    def ok(header_lower):
        return not any(b in header_lower for b in blocked)

    for cand in candidates:
        c = cand.lower()
        if c in lowered and ok(c):
            return lowered[c]

    for cand in candidates:
        c = cand.lower()
        if len(c) < 3:
            continue          # 2-letter candidates matched far too much
        pat = re.compile(r"\b" + re.escape(c) + r"\b")
        for low, original in lowered.items():
            if pat.search(low) and ok(low):
                return original

    if required:
        raise SystemExit(
            "Could not find a %s column. Looked for %s. Columns present: %s"
            % (label or "required", ", ".join(candidates), ", ".join(headers))
        )
    return None


def validate_numeric_column(rows, col, label="", min_ratio=0.7):
    """Confirm a column chosen as an amount actually contains numbers.

    Guards against a text column being bound by name matching and then parsed
    into numbers scraped out of payment narratives.
    """
    sample = [r.get(col) for r in rows[:200] if r.get(col) not in (None, "")]
    if not sample:
        return
    good = sum(1 for v in sample if parse_amount(v) is not None)
    ratio = good / float(len(sample))
    if ratio < min_ratio:
        raise SystemExit(
            "Column '%s' was chosen as the %s column but only %d of %d sampled "
            "values parse as numbers (%.0f%%). That is almost certainly the "
            "wrong column. Name it explicitly rather than relying on "
            "detection." % (col, label or "amount", good, len(sample),
                            ratio * 100))


# ------------------------------------------------------------ xlsx output


def new_workbook():
    wb = Workbook()
    wb.remove(wb.active)
    return wb


def write_sheet(wb, title, headers, rows, widths=None, flag_col=None,
                notes=None):
    """Write one sheet at the 12pt floor with a frozen, filtered header row.

    rows: list of lists, already in display order.
    flag_col: 0-based index of a column whose truthy value shades the row.
    notes: list of strings written above the table, for scope and method.
    """
    ws = wb.create_sheet(title=title[:31])
    start = 1

    if notes:
        for note in notes:
            cell = ws.cell(row=start, column=1, value=note)
            cell.font = Font(name=FONT_NAME, size=BODY_PT, italic=True)
            start += 1
        start += 1

    for col, head in enumerate(headers, start=1):
        cell = ws.cell(row=start, column=col, value=head)
        cell.font = Font(name=FONT_NAME, size=HEADER_PT, bold=True)
        cell.fill = HEADER_FILL
        cell.border = BOX
        cell.alignment = Alignment(vertical="top", wrap_text=True)

    for r, row in enumerate(rows, start=start + 1):
        shade = None
        if flag_col is not None and flag_col < len(row):
            value = row[flag_col]
            if value not in (None, "", False, "NO", "no", 0):
                shade = FLAG_FILL
        for c, value in enumerate(row, start=1):
            if isinstance(value, Decimal):
                value = float(value)
            cell = ws.cell(row=r, column=c, value=value)
            cell.font = Font(name=FONT_NAME, size=BODY_PT)
            cell.border = BOX
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if shade:
                cell.fill = shade

    if widths:
        for i, width in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = width
    else:
        for i, head in enumerate(headers, start=1):
            longest = len(str(head))
            for row in rows[:200]:
                if i - 1 < len(row) and row[i - 1] is not None:
                    longest = max(longest, len(str(row[i - 1])))
            ws.column_dimensions[get_column_letter(i)].width = min(max(longest + 2, 12), 55)

    ws.freeze_panes = ws.cell(row=start + 1, column=1)
    if rows:
        ws.auto_filter.ref = "A%d:%s%d" % (
            start, get_column_letter(len(headers)), start + len(rows)
        )
    return ws


def save_workbook(wb, path):
    """Write via .tmp then os.replace. The target is never opened for writing."""
    path = os.path.abspath(path)
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    tmp = path + ".tmp"
    wb.save(tmp)
    os.replace(tmp, path)
    return path


def stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def provenance_banner(script_name, args_summary):
    """The line that goes at the top of every output sheet."""
    return (
        "Generated by %s on %s. Parameters: %s. "
        "Output is an EXCEPTION LIST, not a set of findings. "
        "Every item requires corroboration against a source document before "
        "it may be reported." % (script_name, stamp(), args_summary)
    )
