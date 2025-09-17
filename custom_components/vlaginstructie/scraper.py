import aiohttp
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import calendar
import re
import logging

_LOGGER = logging.getLogger(__name__)

URL = (
    "https://www.rijksoverheid.nl/onderwerpen/grondwet-en-statuut/"
    "vraag-en-antwoord/wanneer-kan-ik-de-vlag-uithangen-en-wat-is-de-vlaginstructie"
)

_cache = {"vlagdagen": {}, "last_update": None}

# Dutch month name -> month number
MONTHS = {
    "januari": 1, "februari": 2, "maart": 3, "april": 4,
    "mei": 5, "juni": 6, "juli": 7, "augustus": 8,
    "september": 9, "oktober": 10, "november": 11, "december": 12
}


# ---------- Easter algorithm & christian-holidays ----------
def easter_date(year: int) -> date:
    """Return Easter Sunday date for given Gregorian year (Meeus/Jones algorithm)."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def is_christian_holiday(d: date) -> bool:
    """Return True for commonly recognized Christian holidays used in NL context."""
    year = d.year
    easter = easter_date(year)
    good_friday = easter - timedelta(days=2)
    easter_monday = easter + timedelta(days=1)
    ascension = easter + timedelta(days=39)
    pentecost = easter + timedelta(days=49)  # Pinksteren (Sunday)
    pentecost_monday = easter + timedelta(days=50)
    christmas_1 = date(year, 12, 25)
    christmas_2 = date(year, 12, 26)

    holidays = {good_friday, easter, easter_monday, ascension, pentecost, pentecost_monday, christmas_1, christmas_2}
    return d in holidays


# ---------- helpers to parse date strings ----------
def parse_date_string(raw: str):
    """
    Parse a raw date string and return tuple (day, month, year_or_None, had_year_bool).
    Supports formats:
      - "04-05-2025"
      - "04-05"
      - "4 mei 2025"
      - "4 mei"
    Returns (day:int, month:int, year:int|None, had_year:bool) or (None, None, None, False).
    """
    raw = raw.strip().lower()
    # direct numeric with dashes: dd-mm-yyyy or dd-mm
    m = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", raw)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3)), True
    m = re.match(r"^(\d{1,2})[-/](\d{1,2})$", raw)
    if m:
        return int(m.group(1)), int(m.group(2)), None, False

    # textual month (Dutch)
    m = re.match(r"^(\d{1,2})\s+([a-zé]+)\s+(\d{4})$", raw)
    if m:
        day = int(m.group(1))
        month_name = m.group(2)
        month = MONTHS.get(month_name)
        if month:
            return day, month, int(m.group(3)), True

    m = re.match(r"^(\d{1,2})\s+([a-zé]+)$", raw)
    if m:
        day = int(m.group(1))
        month = MONTHS.get(m.group(2))
        if month:
            return day, month, None, False

    return None, None, None, False


# ---------- variable days ----------
def last_weekday_of_month(year, month, weekday: int):
    """Last weekday (0=Mon) of month."""
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    offset = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=offset)


def nth_weekday_of_month(year, month, weekday: int, n: int):
    """Nth weekday (0=Mon) of month."""
    first_day = date(year, month, 1)
    first_weekday = first_day.weekday()
    delta_days = (weekday - first_weekday + 7) % 7 + (n - 1) * 7
    return first_day + timedelta(days=delta_days)


def get_variable_days_for_year(year: int):
    """Return mapping of ISO-dates to info for variable days of the given year."""
    v = {}

    # Veteranendag = last Saturday of June
    vet = last_weekday_of_month(year, 6, 5)  # 5 = Saturday
    v[vet.isoformat()] = {
        "name": "Veteranendag",
        "halfstok": False,
        "wimpel": False,
        "scope": "all",
    }

    # Prinsjesdag = third Tuesday of September
    prins = nth_weekday_of_month(year, 9, 1, 3)  # 1 = Tuesday
    v[prins.isoformat()] = {
        "name": "Prinsjesdag",
        "halfstok": False,
        "wimpel": False,
        "scope": "all",
    }

    return v


# ---------- main fetcher ----------
async def fetch_vlagdagen():
    """
    Return dict keyed by ISO dates 'YYYY-MM-DD' -> info.
    Caches per day to avoid excessive requests.
    """
    global _cache
    today = date.today()
    if _cache["last_update"] == today and _cache["vlagdagen"]:
        _LOGGER.debug("fetch_vlagdagen - returning cached %d items", len(_cache["vlagdagen"]))
        return _cache["vlagdagen"]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as resp:
                html = await resp.text()
    except Exception as e:
        _LOGGER.warning("fetch_vlagdagen - fetch failed: %s, returning cache (%d items)", e, len(_cache["vlagdagen"]))
        return _cache["vlagdagen"]

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")
    result = {}

    if table:
        rows = table.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            raw_date_cell = cols[0].get_text(" ", strip=True)
            reason = cols[1].get_text(" ", strip=True)

            # split main and optional parenthetical alternative
            pm = re.match(r"^(.*?)\s*\((.*?)\)\s*$", raw_date_cell)
            if pm:
                main_raw = pm.group(1).strip()
                alt_raw = pm.group(2).strip()
            else:
                main_raw = raw_date_cell.strip()
                alt_raw = None

            # parse main once to see if it contains a year
            main_day, main_month, main_year, main_has_year = parse_date_string(main_raw)
            alt_day = alt_month = alt_year = None
            alt_has_year = False
            if alt_raw:
                alt_day, alt_month, alt_year, alt_has_year = parse_date_string(alt_raw)

            # determine which years to create entries for
            years = []
            if main_has_year:
                years = [main_year]
            else:
                years = [today.year, today.year + 1]

            for y in years:
                # build main_date for this year (if parsing succeeded)
                if main_day is None or main_month is None:
                    continue
                main_dt = date(y, main_month, main_day)

                # determine alt_dt if provided
                alt_dt = None
                if alt_raw and (alt_day is not None and alt_month is not None):
                    if alt_has_year:
                        alt_dt = date(alt_year, alt_month, alt_day)
                    else:
                        alt_dt = date(y, alt_month, alt_day)

                # apply "use parentheses only if main falls on Sunday or Christian holiday"
                use_dt = main_dt
                if alt_dt:
                    if main_dt.weekday() == 6 or is_christian_holiday(main_dt):
                        use_dt = alt_dt
                        _LOGGER.debug(
                            "Row '%s' reason '%s': main %s is Sunday/holiday -> using alt %s for year %d",
                            raw_date_cell, reason, main_dt.isoformat(), alt_dt.isoformat(), y
                        )
                    else:
                        _LOGGER.debug(
                            "Row '%s' reason '%s': main %s is valid -> using main for year %d",
                            raw_date_cell, reason, main_dt.isoformat(), y
                        )
                else:
                    # no alt specified -> use main (no automatic shift)
                    _LOGGER.debug(
                        "Row '%s' reason '%s': no alt -> using main %s for year %d",
                        raw_date_cell, reason, main_dt.isoformat(), y
                    )

                # final key and info
                key = use_dt.isoformat()
                result[key] = {
                    "name": reason,
                    "halfstok": "dodenherdenking" in reason.lower(),
                    "wimpel": "koning" in reason.lower() or "koningsdag" in reason.lower() or "wimpel" in reason.lower(),
                    "scope": "all",
                }

    # add variable days for this and next year
    result.update(get_variable_days_for_year(today.year))
    result.update(get_variable_days_for_year(today.year + 1))

    # cache and return
    _cache["vlagdagen"] = result
    _cache["last_update"] = today
    _LOGGER.debug("fetch_vlagdagen - parsed %d iso-date entries", len(result))
    return result
