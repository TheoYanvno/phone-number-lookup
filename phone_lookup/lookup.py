"""Looks up the public numbering-plan details of a phone number with Google's libphonenumber data
(the `phonenumbers` package): whether it's valid, how to write it, which country or region its
prefix belongs to, the carrier it was first given to, its time zones and what kind of line it is.

Everything comes from the offline data that ships with `phonenumbers`. Nothing is sent anywhere,
and none of it identifies who owns or uses a number: it only describes the number's prefix.
"""
from __future__ import annotations

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat, PhoneNumberType, carrier, geocoder, timezone

from .result import Result

# PhoneNumberType values → plain words
TYPE_NAMES = {
    PhoneNumberType.FIXED_LINE: "landline",
    PhoneNumberType.MOBILE: "mobile",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "landline or mobile",
    PhoneNumberType.TOLL_FREE: "toll-free",
    PhoneNumberType.PREMIUM_RATE: "premium rate",
    PhoneNumberType.SHARED_COST: "shared cost",
    PhoneNumberType.VOIP: "internet (VoIP)",
    PhoneNumberType.PERSONAL_NUMBER: "personal number",
    PhoneNumberType.PAGER: "pager",
    PhoneNumberType.UAN: "company number (UAN)",
    PhoneNumberType.VOICEMAIL: "voicemail",
    PhoneNumberType.UNKNOWN: "unknown",
}

# NumberParseException.error_type values → what to tell the person
PARSE_ERRORS = {
    NumberParseException.INVALID_COUNTRY_CODE: "That doesn't start with a country code. Start with + and the country code "
                                               "(like +1 or +44), or pass --region with a two-letter country (like --region US).",
    NumberParseException.NOT_A_NUMBER: "That isn't a phone number.",
    NumberParseException.TOO_SHORT_AFTER_IDD: "That's too short after the international prefix.",
    NumberParseException.TOO_SHORT_NSN: "That's too short to be a phone number.",
    NumberParseException.TOO_LONG: "That's too long to be a phone number.",
}


class LookupError(ValueError):  # noqa: A001 - a clear name for callers; it's a ValueError
    """The input couldn't be read as a phone number; the message says why."""


def clean_input(raw: str) -> str:
    """Strips what people paste around numbers ("tel:", spaces at the ends) and limits the length."""
    text = str(raw or "").strip()
    if text.lower().startswith("tel:"):
        text = text[4:]
    if len(text) > 40:
        raise LookupError("That's too long to be a phone number.")
    if not text:
        raise LookupError("Type a phone number, like +1 202 555 0123.")
    return text


def lookup(raw: str, region: str | None = None, lang: str = "en") -> Result:
    """Reads `raw` (with a + country code, or a local number plus `region`) and describes it."""
    text = clean_input(raw)
    region = region.upper() if region else None
    if region is not None and region not in phonenumbers.SUPPORTED_REGIONS:
        raise LookupError(f"{region} isn't a two-letter country code that phonenumbers knows (try US, GB, IN…).")
    try:
        number = phonenumbers.parse(text, region)
    except NumberParseException as e:
        raise LookupError(PARSE_ERRORS.get(e.error_type, "That couldn't be read as a phone number.")) from e
    valid = phonenumbers.is_valid_number(number)
    zones = tuple(z for z in timezone.time_zones_for_number(number) if z != "Etc/Unknown")
    region_code = phonenumbers.region_code_for_number(number) or ""
    return Result(
        input=text,
        valid=valid,
        possible=phonenumbers.is_possible_number(number),
        e164=phonenumbers.format_number(number, PhoneNumberFormat.E164),
        international=phonenumbers.format_number(number, PhoneNumberFormat.INTERNATIONAL),
        national=phonenumbers.format_number(number, PhoneNumberFormat.NATIONAL),
        country_code=number.country_code,
        national_number=str(number.national_number),
        region_code=region_code if region_code != "001" else "",
        country=geocoder.country_name_for_number(number, lang) if valid else "",
        location=geocoder.description_for_number(number, lang) if valid else "",
        carrier=carrier.name_for_number(number, lang) if valid else "",
        time_zones=zones if valid else (),
        type=TYPE_NAMES.get(phonenumbers.number_type(number), "unknown") if valid else "unknown",
    )


def example(region: str) -> str:
    """phonenumbers' own example number for a country, in international format (for help text and tests)."""
    n = phonenumbers.example_number(region.upper())
    if n is None:
        raise LookupError(f"There's no example number for {region}.")
    return phonenumbers.format_number(n, PhoneNumberFormat.E164)
