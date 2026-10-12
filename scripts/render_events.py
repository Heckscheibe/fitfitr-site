#!/usr/bin/env python3
"""Render the event tables of the privacy policy from PRIVACY.md.

The tables under "Every event the app can send" in the app's PRIVACY.md are the
single source. This script converts those tables (with their group headings) to
HTML and writes them between the `<!-- events:start -->` and `<!-- events:end -->`
markers of both privacy pages. Standard library only, deterministic output.

Usage:
    python3 scripts/render_events.py --source /path/to/PRIVACY.md
    python3 scripts/render_events.py --source /path/to/PRIVACY.md --check

--check rewrites nothing and exits 1 if a page is out of date.
"""
import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [ROOT / "en" / "privacy" / "index.html", ROOT / "de" / "datenschutz" / "index.html"]
SECTION = "## Every event the app can send"
START, END = "<!-- events:start -->", "<!-- events:end -->"
EXPECTED_EVENTS = 32


def section_lines(text):
    lines = text.splitlines()
    try:
        begin = next(i for i, l in enumerate(lines) if l.strip() == SECTION)
    except StopIteration:
        sys.exit("section not found: " + SECTION)
    end = len(lines)
    for i in range(begin + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return lines[begin + 1:end]


def split_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def inline(cell):
    """Backtick code spans become <code>; everything else is escaped text."""
    out, last = [], 0
    for m in re.finditer(r"`([^`]+)`", cell):
        out.append(html.escape(cell[last:m.start()], quote=False))
        out.append("<code>%s</code>" % html.escape(m.group(1), quote=False))
        last = m.end()
    out.append(html.escape(cell[last:], quote=False))
    result = "".join(out)
    if "*" in re.sub(r"<code>.*?</code>", "", result):
        print("warning: unconverted markdown emphasis in cell: " + cell, file=sys.stderr)
    return result


def parse(lines):
    groups, current, table = [], None, None
    for line in lines:
        if line.startswith("### "):
            current = {"title": line[4:].strip(), "header": None, "rows": []}
            groups.append(current)
            table = None
        elif line.startswith("|") and current is not None:
            cells = split_row(line)
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                continue
            if current["header"] is None:
                current["header"] = cells
            else:
                current["rows"].append(cells)
    return [g for g in groups if g["header"] is not None]


def render(groups):
    """Explicit ARIA roles keep the table semantics when narrow screens restack the rows with CSS."""
    out = []
    for g in groups:
        out.append("<h3>%s</h3>" % html.escape(g["title"], quote=False))
        out.append('<div class="table-scroll">')
        out.append('<table role="table">')
        out.append('<thead role="rowgroup">')
        out.append('<tr role="row">' + "".join(
            '<th scope="col" role="columnheader">%s</th>' % inline(c) for c in g["header"]) + "</tr>")
        out.append("</thead>")
        out.append('<tbody role="rowgroup">')
        for row in g["rows"]:
            first, rest = row[0], row[1:]
            out.append('<tr role="row">' + '<th scope="row" role="rowheader">%s</th>' % inline(first)
                       + "".join('<td role="cell">%s</td>' % inline(c) for c in rest) + "</tr>")
        out.append("</tbody>")
        out.append("</table>")
        out.append("</div>")
    return "\n".join(out)


def splice(page_text, block):
    s = page_text.index(START) + len(START)
    e = page_text.index(END)
    return page_text[:s] + "\n" + block + "\n" + page_text[e:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, help="path to the app's PRIVACY.md")
    ap.add_argument("--check", action="store_true", help="do not write; exit 1 if a page is out of date")
    args = ap.parse_args()

    groups = parse(section_lines(Path(args.source).read_text(encoding="utf-8")))
    total = sum(len(g["rows"]) for g in groups)
    print("%d groups, %d event rows" % (len(groups), total))
    if total != EXPECTED_EVENTS:
        sys.exit("expected %d events, found %d" % (EXPECTED_EVENTS, total))

    block = render(groups)
    stale = False
    for page in PAGES:
        old = page.read_text(encoding="utf-8")
        new = splice(old, block)
        if new != old:
            if args.check:
                print("out of date: " + str(page.relative_to(ROOT)))
                stale = True
            else:
                page.write_text(new, encoding="utf-8")
                print("updated " + str(page.relative_to(ROOT)))
        else:
            print("unchanged " + str(page.relative_to(ROOT)))
    sys.exit(1 if stale else 0)


if __name__ == "__main__":
    main()
