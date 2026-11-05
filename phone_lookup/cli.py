"""Command line:

  python -m phone_lookup +44 20 7946 0958            one number with its country code
  python -m phone_lookup "(202) 555-0123" --region US   a local number and its country
  python -m phone_lookup +81312345678 +61291234567   several at once
  python -m phone_lookup --file numbers.txt --csv    one number per line, as CSV (or --json)
  python -m phone_lookup                             asks for a number, like the classic script
"""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .lookup import LookupError, example, lookup
from .report import text, to_csv, to_json

NOTE = ("Shows public numbering-plan details only (from the offline phonenumbers data). "
        "It can't tell you who a number belongs to. Use it responsibly and legally.")


def main(argv: list[str] | None = None, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr) -> int:
    p = argparse.ArgumentParser(prog="phone_lookup", description="Look up public details of phone numbers.", epilog=NOTE)
    p.add_argument("numbers", nargs="*", help="phone numbers, ideally with + and the country code")
    p.add_argument("--region", "-r", help="two-letter country for numbers without a + country code, like US or GB")
    p.add_argument("--file", "-f", help="a text file with one number per line (# starts a comment)")
    out = p.add_mutually_exclusive_group()
    out.add_argument("--json", action="store_true", help="print JSON")
    out.add_argument("--csv", action="store_true", help="print CSV (for a spreadsheet)")
    p.add_argument("--example", metavar="COUNTRY", help="print an example number for a country, like US")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = p.parse_args(argv)

    if args.example:
        try:
            print(example(args.example), file=stdout)
            return 0
        except LookupError as e:
            print(e, file=stderr)
            return 2

    numbers = list(args.numbers)
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                numbers += [line.split("#", 1)[0].strip() for line in fh if line.split("#", 1)[0].strip()]
        except OSError as e:
            print(f"Couldn't read {args.file}: {e.strerror}", file=stderr)
            return 2
    if not numbers:
        try:
            numbers = [input("Enter phone number with country code: ").strip()]
        except EOFError:
            print("No number given.", file=stderr)
            return 2

    results, failed = [], 0
    for raw in numbers[:1000]:
        try:
            results.append(lookup(raw, args.region))
        except LookupError as e:
            failed += 1
            print(f"{raw}: {e}", file=stderr)
    if args.json:
        print(to_json(results), file=stdout)
    elif args.csv:
        print(to_csv(results), end="", file=stdout)
    else:
        print("\n\n".join(text(r) for r in results), file=stdout)
        if results:
            print(f"\n{NOTE}", file=stdout)
    return 1 if failed and not results else 0
