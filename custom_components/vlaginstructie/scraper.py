import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, date
import os

URL = "https://www.rijksoverheid.nl/onderwerpen/grondwet-en-statuut/vraag-en-antwoord/wanneer-kan-ik-de-vlag-uithangen-en-wat-is-de-vlaginstructie"

MONTHS = {
    "januari": 1, "februari": 2, "maart": 3, "april": 4,
    "mei": 5, "juni": 6, "juli": 7, "augustus": 8,
    "september": 9, "oktober": 10, "november": 11, "december": 12
}

CACHE_FILENAME = "vlagdagen_cache.json"


def parse_date(text: str) -> str | None:
    """Converteer Nederlandse datumstring (bv. '27 april') naar 'dd-mm'."""
    text = re.sub(r"\(.*?\)", "", text)  # verwijder dingen tussen haakjes
    text = text.strip().lower()
    match = re.search(r"(\d{1,2}) (\w+)", text)
    if match:
        dag = int(match.group(1))
        maand_naam = match.group(2)
        maand = MONTHS.get(maand_naam)
        if maand:
            return f"{dag:02d}-{maand:02d}"
    return None


def fetch_vlagdagen_no_cache() -> dict:
    """Haal vlagdagen direct van rijksoverheid.nl."""
    resp = requests.get(URL, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    vlagdagen = {}

    # Zoek naar de kop "Vaste dagen waarop wordt gevlagd"
    header = None
    for h in soup.find_all(["h2", "h3", "h4"]):
        if "Vaste dagen waarop wordt gevlagd" in h.get_text():
            header = h
            break

    if not header:
        list_items = soup.select("ul li")
    else:
        ul = header.find_next_sibling("ul")
        list_items = ul.find_all("li") if ul else []

    for li in list_items:
        text = li.get_text(" ", strip=True)
        parts = re.split(r"[:–-]", text, maxsplit=1)
        if len(parts) < 2:
            continue

        datum_str = parts[0].strip()
        omschrijving = parts[1].strip()
        key = parse_date(datum_str)
        if not key:
            continue

        daginfo = {
            "name": omschrijving,
            "halfstok": "halfstok" in text.lower(),
            "wimpel": "wimpel" in text.lower(),
            "scope": "alle"
        }

        if "enkele gebouwen" in text.lower():
            daginfo["scope"] = "enkele"

        vlagdagen[key] = daginfo

    return vlagdagen


def write_cache(cache_data: dict):
    data = {
        "fetched_date": date.today().isoformat(),
        "vlagdagen": cache_data
    }
    path = os.path.join(os.path.dirname(__file__), CACHE_FILENAME)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def read_cache() -> dict | None:
    path = os.path.join(os.path.dirname(__file__), CACHE_FILENAME)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        fetched = data.get("fetched_date")
        if fetched and datetime.fromisoformat(fetched).date() == date.today():
            return data.get("vlagdagen")
    except Exception:
        return None
    return None


def get_vlagdagen() -> dict:
    """Gebruik cache (1x per dag), anders fetch opnieuw."""
    vlagdagen = read_cache()
    if vlagdagen is not None:
        return vlagdagen
    try:
        vlagdagen = fetch_vlagdagen_no_cache()
        write_cache(vlagdagen)
        return vlagdagen
    except Exception:
        return {}
