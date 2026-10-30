#!/usr/bin/env python3
"""Set the date at the top of both privacy pages. Standard library only.

The site has no build step, so the date cannot follow a deploy by itself. Run this
as the last step before merging a policy change to main, which is what publishes it.

Usage:
    python3 scripts/set_policy_date.py              # today
    python3 scripts/set_policy_date.py 2026-11-02   # a given date
"""
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MONTHS_EN = ("January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December")
MONTHS_DE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
             "August", "September", "Oktober", "November", "Dezember")


def main():
    day = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
    pages = (
        (ROOT / "en/privacy/index.html", r"Last updated \d{1,2} \w+ \d{4}\.",
         f"Last updated {day.day} {MONTHS_EN[day.month - 1]} {day.year}."),
        (ROOT / "de/datenschutz/index.html", r"Stand: \d{1,2}\. \w+ \d{4}\.",
         f"Stand: {day.day}. {MONTHS_DE[day.month - 1]} {day.year}."),
    )
    pending = []
    for path, pattern, replacement in pages:
        text = path.read_text(encoding="utf-8")
        text, found = re.subn(pattern, replacement, text)
        if found != 1:
            sys.exit(f"{path.relative_to(ROOT)}: expected one date, found {found}")
        pending.append((path, text, replacement))
    for path, text, replacement in pending:
        path.write_text(text, encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: {replacement}")


if __name__ == "__main__":
    main()
