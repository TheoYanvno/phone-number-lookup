"""One number's details. Kept apart from the lookup so the reports can be used and tested without phonenumbers."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Result:
    input: str
    valid: bool
    possible: bool
    e164: str
    international: str
    national: str
    country_code: int
    national_number: str
    region_code: str            # two letters, like "US" ("" when the prefix isn't one country's)
    country: str                # the country's name, like "United States"
    location: str               # a region or city for the prefix when known, like "California"
    carrier: str                # the network the number range was first given to ("" for many landlines)
    time_zones: tuple[str, ...] = field(default_factory=tuple)
    type: str = "unknown"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["time_zones"] = list(self.time_zones)
        return d
