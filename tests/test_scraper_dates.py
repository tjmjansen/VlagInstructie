"""Tests for Vlaginstructie date calculations."""

from datetime import date
import importlib.util
from pathlib import Path
import unittest

try:
    import aiohttp  # noqa: F401
    import bs4  # noqa: F401
except ImportError as err:
    raise unittest.SkipTest(f"Optional scraper dependency is unavailable: {err}") from err

SCRAPER_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "vlaginstructie"
    / "scraper.py"
)

spec = importlib.util.spec_from_file_location("vlaginstructie_scraper", SCRAPER_PATH)
scraper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper)


class ScraperDateTests(unittest.TestCase):
    """Test pure date helpers used by the scraper."""

    def test_parse_date_string(self):
        cases = [
            ("04-05-2025", (4, 5, 2025, True)),
            ("04-05", (4, 5, None, False)),
            ("4 mei 2025", (4, 5, 2025, True)),
            ("4 mei", (4, 5, None, False)),
            ("geen datum", (None, None, None, False)),
        ]

        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(scraper.parse_date_string(raw), expected)

    def test_easter_date_known_years(self):
        self.assertEqual(scraper.easter_date(2025), date(2025, 4, 20))
        self.assertEqual(scraper.easter_date(2026), date(2026, 4, 5))

    def test_christian_holiday_detection(self):
        self.assertTrue(scraper.is_christian_holiday(date(2026, 4, 3)))
        self.assertTrue(scraper.is_christian_holiday(date(2026, 4, 5)))
        self.assertTrue(scraper.is_christian_holiday(date(2026, 5, 14)))
        self.assertFalse(scraper.is_christian_holiday(date(2026, 6, 1)))

    def test_variable_days_for_year(self):
        days = scraper.get_variable_days_for_year(2026)

        self.assertEqual(days["2026-06-27"]["name"], "Veteranendag")
        self.assertEqual(days["2026-09-15"]["name"], "Prinsjesdag")
        self.assertFalse(days["2026-06-27"]["halfstok"])
        self.assertFalse(days["2026-09-15"]["wimpel"])


if __name__ == "__main__":
    unittest.main()
