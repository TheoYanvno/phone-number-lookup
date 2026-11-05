# Phone Number Lookup

A Python command-line tool that checks a phone number and shows its **public numbering-plan details**: whether it's valid, how to write it in every standard format, the country and region its prefix belongs to, the carrier the number range was first given to, its time zones and what kind of line it is (mobile, landline, toll-free…).

It uses [`phonenumbers`](https://github.com/daviddrysdale/python-phonenumbers), the Python port of Google's libphonenumber, and works entirely **offline** from the data that comes with it.

```
$ python -m phone_lookup +442079460958
Number:          +442079460958
Valid:           yes
Possible:        yes
International:   +44 20 7946 0958
National:        020 7946 0958
E.164:           +442079460958
Country code:    +44
National number: 2079460958
Region:          London, United Kingdom (GB)
Type:            landline
Carrier:         not listed (common for landlines, and numbers can move to another carrier)
Time zones:      Europe/London

Shows public numbering-plan details only (from the offline phonenumbers data). It can't tell you who a number belongs to. Use it responsibly and legally.
```

*+44 20 7946 0xxx is a range Ofcom sets aside for dramas and examples, so it's safe to use in docs.*

## What it can and can't tell you

- **It describes the number, not the person.** Everything comes from numbering plans: which country a prefix belongs to, which area or carrier a block of numbers was assigned to, and the line type. It doesn't look anything up online and can't tell you who owns or uses a number.
- **Carrier is the original one.** In many countries people keep their number when they switch carriers, so the carrier shown may not be the current one. Landlines often show none.
- **Valid means it fits the plan.** A valid number follows the country's rules; it doesn't mean the number is in service.

## Use it

```
pip install -r requirements.txt

python -m phone_lookup +14155550132                      # with + and the country code
python -m phone_lookup "(202) 555-0143" --region US      # a local number and its country
python -m phone_lookup +81312345678 +61291234567         # several at once
python -m phone_lookup --file numbers.txt --csv > out.csv   # one number per line (# for comments)
python -m phone_lookup +33123456789 --json               # JSON for other programs
python -m phone_lookup --example IN                      # an example number for a country
python -m phone_lookup                                   # asks for a number
```

`pip install .` also adds a `phone-lookup` command.

## How it works

- [`phone_lookup/lookup.py`](phone_lookup/lookup.py) cleans the input (spaces, a `tel:` prefix, a length limit), parses it with `phonenumbers.parse`, and builds one `Result` with every detail. Parse errors become plain advice, like *"That doesn't start with a country code. Start with + …, or pass --region"*. Details that only make sense for a valid number (region, carrier, time zones) are left empty for invalid ones.
- [`phone_lookup/report.py`](phone_lookup/report.py) turns results into the aligned text above, JSON, or CSV. In the CSV, values starting with `=`, `+`, `-` or `@` get a leading `'` so a spreadsheet can't run them as formulas (E.164 numbers start with `+`).
- [`phone_lookup/cli.py`](phone_lookup/cli.py) reads numbers from the command line, a file or a prompt, reports bad lines without stopping, and exits with an error only if nothing could be read.

## Tests

```
python -m unittest -v
```

The tests use `phonenumbers`' own example numbers for each country, never real people's numbers. GitHub Actions runs them on Python 3.10, 3.12 and 3.13.

| File | What it does |
|---|---|
| `phone_lookup/lookup.py` | Parsing and every detail of one number |
| `phone_lookup/result.py` | The `Result` with all the fields |
| `phone_lookup/report.py` | Text, JSON and CSV output |
| `phone_lookup/cli.py` | The command line |
| `tests/` | Report tests, plus lookup and command tests on the real data |

Built with help from AI coding tools for planning, code review and tests.

## License

MIT, see [LICENSE](LICENSE). Numbering-plan data © Google, through the Apache-2.0-licensed `phonenumbers` package.
