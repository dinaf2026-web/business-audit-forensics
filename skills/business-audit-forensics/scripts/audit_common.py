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
    "%m/%d/%y", "%d/%m/%y",
    "%b %d, %Y", "%d %b %Y", "%B %d, %Y",
)


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


_AMOUNT_CLEAN = re.compile(r"[^0-9.\-()]")


def parse_amount(value):
    """Return a Decimal, or None. Handles $, commas, and (123.45) negatives."""
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
    negative = text.startswith("(") and text.endswith(")")
    text = _AMOUNT_CLEAN.sub("", text).replace("(", "").replace(")", "")
    if text in ("", "-", "."):
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
            rows = [dict(r) for r in reader]
        return headers, rows

    if ext in (".xlsx", ".xlsm"):
        wb = load_workbook(path, data_only=True, read_only=True)
        ws = wb[sheet] if sheet else wb[wb.sheetnames[0]]
        rows_iter = ws.iter_rows(values_only=True)
        headers = []
        for raw in rows_iter:
            if not raw or not any(c is not None and str(c).strip() for c in raw):
                continue
            candidate = [str(c).strip() if c is not None else "" for c in raw]
            if header_contains:
                present = set(candidate)
                if not all(want in present for want in header_contains):
                    continue
            headers = candidate
            break
        if header_contains and not headers:
            wb.close()
            raise SystemExit(
                "Could not find a header row containing %s in sheet '%s' of %s. "
                "Refusing to continue: reading the wrong row as a header would "
                "compare an empty set and report it as clean."
                % (", ".join(header_contains), sheet or "(first)", path))
        out = []
        for raw in rows_iter:
            if raw is None or not any(c is not None and str(c).strip() != "" for c in raw):
                continue
            record = {}
            for i, head in enumerate(headers):
                record[head] = raw[i] if i < len(raw) else None
            out.append(record)
        wb.close()
        return headers, out

    raise ValueError("Unsupported table format: %s" % ext)


def pick_column(headers, candidates, required=True, label=""):
    """Find a column by case-insensitive partial match against candidates."""
    lowered = {h.lower().strip(): h for h in headers if h}
    for cand in candidates:
        if cand.lower() in lowered:
            return lowered[cand.lower()]
    for cand in candidates:
        for low, original in lowered.items():
            if cand.lower() in low:
                return original
    if required:
        raise SystemExit(
            "Could not find a %s column. Looked for %s. Columns present: %s"
            % (label or "required", ", ".join(candidates), ", ".join(headers))
        )
    return None


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
