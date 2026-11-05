import csv
import io
import json
import unittest

from phone_lookup.report import text, to_csv, to_json
from phone_lookup.result import Result


def result(**kw):
    base = dict(input="+44 20 7946 0958", valid=True, possible=True, e164="+442079460958", international="+44 20 7946 0958",
                national="020 7946 0958", country_code=44, national_number="2079460958", region_code="GB",
                country="United Kingdom", location="London", carrier="", time_zones=("Europe/London",), type="landline")
    base.update(kw)
    return Result(**base)


class TextReport(unittest.TestCase):
    def test_a_valid_number_shows_every_detail_in_order(self):
        out = text(result())
        labels = [line.split(":")[0] for line in out.splitlines()]
        self.assertEqual(labels, ["Number", "Valid", "Possible", "International", "National", "E.164", "Country code",
                                  "National number", "Region", "Type", "Carrier", "Time zones"])
        self.assertIn("Region:          London, United Kingdom (GB)", out)
        self.assertIn("Country code:    +44", out)
        self.assertIn("not listed (common for landlines", out)

    def test_a_place_is_not_repeated_when_the_location_is_the_country(self):
        self.assertIn("Region:          Singapore (SG)", text(result(location="Singapore", country="Singapore", region_code="SG")))

    def test_an_invalid_number_explains_why_details_are_missing(self):
        out = text(result(valid=False, country="", location="", time_zones=()))
        self.assertIn("Valid:           no", out)
        self.assertIn("isn't valid for any country's numbering plan", out)
        self.assertNotIn("Carrier", out)


class Exports(unittest.TestCase):
    def test_json_lists_every_field(self):
        data = json.loads(to_json([result(carrier="Vodafone")]))
        self.assertEqual(data[0]["carrier"], "Vodafone")
        self.assertEqual(data[0]["time_zones"], ["Europe/London"])

    def test_csv_has_a_header_and_defuses_spreadsheet_formulas(self):
        rows = list(csv.reader(io.StringIO(to_csv([result(input="=cmd|'/c calc'!A1", time_zones=("America/New_York", "America/Chicago"))]))))
        self.assertEqual(rows[0][:3], ["input", "valid", "possible"])
        self.assertEqual(rows[1][0], "'=cmd|'/c calc'!A1")
        self.assertEqual(rows[1][3], "'+442079460958", "a leading + would also start a formula")
        self.assertEqual(rows[1][12], "America/New_York America/Chicago")


if __name__ == "__main__":
    unittest.main()
