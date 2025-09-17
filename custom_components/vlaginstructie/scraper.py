import aiohttp
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import calendar
import holidays

URL = "https://www.rijksoverheid.nl/onderwerpen/grondwet-en-statuut/vraag-en-antwoord/wanneer-kan-ik-de-vlag-uithangen-en-wat-is-de-vlaginstructie"

# Cache voor max 1 fetch per dag
_cache = {
    "vlagdagen": {},
    "last_update": None
}

# Nederlandse christelijke feestdagen
nl_holidays = holidays.NL()

# --- Helper functies voor variabele datums ---
def last_weekday_of_month(year, month, weekday):
    """Return the last weekday (0=maandag) of a given month."""
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    offset = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=offset)

def nth_weekday_of_month(year, month, weekday, n):
    """Return the nth weekday (0=maandag) of a given month."""
    first_day = date(year, month, 1)
    first_weekday = first_day.weekday()
    delta_days = (weekday - first_weekday + 7) % 7 + (n-1)*7
    return first_day + timedelta(days=delta_days)

def adjust_for_sunday_or_holiday(d):
    """If the date falls on Sunday or a recognized holiday, adjust it."""
    if d.weekday() == 6 or d in nl_holidays:
        # Voor nu: verplaats naar volgende maandag
        return d + timedelta(days=(7 - d.weekday()))
    return d

# --- Variabele dagen ---
def get_variable_days(year):
    vlagdagen = {}

    # Laatste zaterdag in juni
    last_saturday_june = last_weekday_of_month(year, 6, 5)
    last_saturday_june = adjust_for_sunday_or_holiday(last_saturday_june)
    vlagdagen[last_saturday_june.strftime("%d-%m")] = {
        "name": "Laatste zaterdag juni",
        "halfstok": False,
        "wimpel": True,
        "scope": "all"
    }

    # Derde dinsdag in september
    third_tuesday_sep = nth_weekday_of_month(year, 9, 1, 3)
    third_tuesday_sep = adjust_for_sunday_or_holiday(third_tuesday_sep)
    vlagdagen[third_tuesday_sep.strftime("%d-%m")] = {
        "name": "Derde dinsdag september",
        "halfstok": False,
        "wimpel": True,
        "scope": "all"
    }

    return vlagdagen

# --- Live scraping ---
async def fetch_vlagdagen():
    """Fetch vlagdagen from rijksoverheid.nl with caching (once per day)."""
    global _cache
    today = date.today()
    if _cache["last_update"] == today and _cache["vlagdagen"]:
        return _cache["vlagdagen"]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as resp:
                html = await resp.text()
    except Exception:
        # fallback naar cache bij fetch failure
        return _cache["vlagdagen"]

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    vlagdagen = {}
    if table:
        for row in table.find_all("tr")[1:]:  # skip header
            cols = row.find_all("td")
            if len(cols) >= 2:
                datum_str = cols[0].text.strip()
                reason = cols[1].text.strip()
                try:
                    # Datum parsing
                    day = datetime.strptime(datum_str, "%d-%m-%Y").date()
                    day = adjust_for_sunday_or_holiday(day)
                    vlagdagen[day.strftime("%d-%m")] = {
                        "name": reason,
                        "halfstok": "Dodenherdenking" in reason or False,
                        "wimpel": "Koningsdag" in reason or False,
                        "scope": "all"
                    }
                except ValueError:
                    continue

    # Voeg variabele dagen toe
    vlagdagen.update(get_variable_days(today.year))
    vlagdagen.update(get_variable_days(today.year + 1))  # ook volgend jaar

    # Update cache
    _cache["vlagdagen"] = vlagdagen
    _cache["last_update"] = today
    return vlagdagen
