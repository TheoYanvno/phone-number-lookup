"""Turns lookup results into text for the terminal, JSON or CSV. No phonenumbers import here, so
these are tested on their own."""
from __future__ import annotations

import csv
import io
import json


def text(result) -> str:
    """The report for one number, one line per detail, in the same order every time."""
    yes = lambda b: "yes" if b else "no"
    rows = [
        ("Number", result.input),
        ("Valid", yes(result.valid)),
        ("Possible", yes(result.possible)),
        ("International", result.international),
        ("National", result.national),
        ("E.164", result.e164),
        ("Country code", f"+{result.country_code}"),
        ("National number", result.national_number),
    ]
    if result.valid:
        place = ", ".join(dict.fromkeys(p for p in (result.location, result.country) if p)) or "not listed"
        rows += [
            ("Region", f"{place} ({result.region_code})" if result.region_code else place),
            ("Type", result.type),
            ("Carrier", result.carrier or "not listed (common for landlines, and numbers can move to another carrier)"),
            ("Time zones", ", ".join(result.time_zones) or "not listed"),
        ]
    else:
        rows.append(("Note", "This number isn't valid for any country's numbering plan, so there are no region, carrier or time-zone details."))
    width = max(len(k) for k, _ in rows)
    return "\n".join(f"{k + ':':<{width + 1}} {v}" for k, v in rows)


def to_json(results) -> str:
    return json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False)


COLUMNS = ["input", "valid", "possible", "e164", "international", "national", "country_code", "national_number",
           "region_code", "country", "location", "carrier", "time_zones", "type"]


def _safe(value: str) -> str:
    """A spreadsheet runs cells starting with = + - @ as formulas; a leading ' stops that."""
    s = str(value)
    return f"'{s}" if s[:1] in ("=", "+", "-", "@", "\t", "\r") else s


def to_csv(results) -> str:
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(COLUMNS)
    for r in results:
        d = r.to_dict()
        d["time_zones"] = " ".join(d["time_zones"])
        w.writerow([_safe(d[c]) if isinstance(d[c], str) else d[c] for c in COLUMNS])
    return out.getvalue()
