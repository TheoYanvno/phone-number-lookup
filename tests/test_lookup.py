"""Tests against the real phonenumbers data. They use phonenumbers' own example numbers, so they
never depend on a real person's number."""
import io
import json
import tempfile
import unittest
from pathlib import Path

try:
    import phonenumbers
    from phonenumbers import PhoneNumberType
except ImportError:  # pragma: no cover - the CI installs it
    phonenumbers = None

if phonenumbers:
    from phone_lookup.cli import main
    from phone_lookup.lookup import LookupError, example, lookup


@unittest.skipUnless(phonenumbers, "phonenumbers isn't installed (pip install -r requirements.txt)")
class Lookup(unittest.TestCase):
    def test_an_example_uk_number(self):
        r = lookup(example("GB"))
        self.assertTrue(r.valid and r.possible)
        self.assertEqual(r.region_code, "GB")
        self.assertEqual(r.country, "United Kingdom")
        self.assertEqual(r.country_code, 44)
        self.assertIn("Europe/London", r.time_zones)
        self.assertTrue(r.international.startswith("+44 "))
        self.assertEqual(r.e164, "+" + str(r.country_code) + r.national_number)

    def test_a_local_number_with_its_region(self):
        n = phonenumbers.example_number("US")
        national = phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.NATIONAL)
        r = lookup(national, region="us")
        self.assertTrue(r.valid)
        self.assertEqual(r.region_code, "US")
        self.assertEqual(r.country, "United States")
        self.assertTrue(r.time_zones and all(z.startswith("America/") for z in r.time_zones))

    def test_line_types(self):
        mobile = phonenumbers.example_number_for_type("GB", PhoneNumberType.MOBILE)
        toll = phonenumbers.example_number_for_type("US", PhoneNumberType.TOLL_FREE)
        self.assertEqual(lookup(phonenumbers.format_number(mobile, phonenumbers.PhoneNumberFormat.E164)).type, "mobile")
        self.assertEqual(lookup(phonenumbers.format_number(toll, phonenumbers.PhoneNumberFormat.E164)).type, "toll-free")

    def test_tel_links_and_spaces_are_accepted(self):
        self.assertTrue(lookup("tel:" + example("FR")).valid)
        self.assertTrue(lookup("  " + example("JP") + "  ").valid)

    def test_invalid_but_well_formed_numbers_have_no_details(self):
        r = lookup("+1 000 000 0000")
        self.assertFalse(r.valid)
        self.assertEqual((r.country, r.carrier, r.time_zones), ("", "", ()))

    def test_unreadable_input_says_why(self):
        cases = {"hello": "isn't a phone number", "2079460958": "doesn't start with a country code", "+44 1": "too short",
                 "": "Type a phone number", "+1" + "2" * 45: "too long"}
        for raw, message in cases.items():
            with self.assertRaises(LookupError) as e:
                lookup(raw)
            self.assertIn(message, str(e.exception), raw)
        with self.assertRaisesRegex(LookupError, "isn't a two-letter country code"):
            lookup("2079460958", region="XX")


@unittest.skipUnless(phonenumbers, "phonenumbers isn't installed")
class Cli(unittest.TestCase):
    def run_cli(self, *argv, stdin=""):
        out, err = io.StringIO(), io.StringIO()
        code = main(list(argv), stdin=io.StringIO(stdin), stdout=out, stderr=err)
        return code, out.getvalue(), err.getvalue()

    def test_one_number(self):
        code, out, _ = self.run_cli(example("GB"))
        self.assertEqual(code, 0)
        self.assertIn("Valid:", out)
        self.assertIn("United Kingdom", out)
        self.assertIn("Use it responsibly and legally.", out)

    def test_several_numbers_from_a_file_as_json_with_one_bad_line(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "numbers.txt"
            f.write_text(f"# my list\n{example('US')}\nnot a number\n{example('IN')}  # India\n", encoding="utf-8")
            code, out, err = self.run_cli("--file", str(f), "--json")
        self.assertEqual(code, 0)
        self.assertEqual([r["region_code"] for r in json.loads(out)], ["US", "IN"])
        self.assertIn("not a number: That isn't a phone number.", err)

    def test_csv_and_example(self):
        code, out, _ = self.run_cli(example("DE"), "--csv")
        self.assertTrue(out.startswith("input,valid,"))
        self.assertEqual(self.run_cli("--example", "GB")[1].strip(), example("GB"))

    def test_nothing_readable_fails(self):
        code, _, err = self.run_cli("nope")
        self.assertEqual(code, 1)
        self.assertIn("isn't a phone number", err)


if __name__ == "__main__":
    unittest.main()
