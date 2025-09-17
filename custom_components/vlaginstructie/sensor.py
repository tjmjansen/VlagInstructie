"""Sensors for Vlaginstructie using ISO-date keys from scraper."""

import logging
from datetime import date, timedelta, datetime
from homeassistant.components.sensor import SensorEntity

from .scraper import fetch_vlagdagen

_LOGGER = logging.getLogger(__name__)


class VlagInstructieBaseSensor(SensorEntity):
    def __init__(self, name: str, unique_id: str):
        self._name = name
        self._unique_id = unique_id
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes


class VlagInstructieTodaySensor(VlagInstructieBaseSensor):
    def __init__(self):
        super().__init__("vlaginstructie_today", "vlaginstructie_sensor_today")

    async def async_update(self):
        vlagdagen = await fetch_vlagdagen()
        _LOGGER.debug("TodaySensor - fetched %d items", len(vlagdagen))
        today_iso = date.today().isoformat()
        info = vlagdagen.get(today_iso)
        if info:
            self._state = info.get("name")
            self._attributes = {
                "reason": info.get("name"),
                "date": today_iso,
                "scope": info.get("scope"),
                "wimpel": info.get("wimpel"),
                "halfstok": info.get("halfstok"),
            }
            _LOGGER.debug("TodaySensor - match %s -> %s", today_iso, self._attributes)
        else:
            self._state = "No flag instruction"
            self._attributes = {"date": today_iso}
            _LOGGER.debug("TodaySensor - no match for %s", today_iso)


class VlagInstructieTomorrowSensor(VlagInstructieBaseSensor):
    def __init__(self):
        super().__init__("vlaginstructie_tomorrow", "vlaginstructie_sensor_tomorrow")

    async def async_update(self):
        vlagdagen = await fetch_vlagdagen()
        tomorrow_iso = (date.today() + timedelta(days=1)).isoformat()
        info = vlagdagen.get(tomorrow_iso)
        if info:
            self._state = info.get("name")
            self._attributes = {
                "reason": info.get("name"),
                "date": tomorrow_iso,
                "scope": info.get("scope"),
                "wimpel": info.get("wimpel"),
                "halfstok": info.get("halfstok"),
            }
            _LOGGER.debug("TomorrowSensor - match %s -> %s", tomorrow_iso, self._attributes)
        else:
            self._state = "No flag instruction"
            self._attributes = {"date": tomorrow_iso}
            _LOGGER.debug("TomorrowSensor - no match for %s", tomorrow_iso)


class NextFlagDaySensor(VlagInstructieBaseSensor):
    def __init__(self):
        super().__init__("next_flag_day", "vlaginstructie_sensor_next_flag_day")

    async def async_update(self):
        vlagdagen = await fetch_vlagdagen()
        _LOGGER.debug("NextFlagDaySensor - fetched %d items", len(vlagdagen))

        # Build a list of date objects from the ISO keys
        parsed = []
        for iso_key, info in vlagdagen.items():
            try:
                d = datetime.strptime(iso_key, "%Y-%m-%d").date()
                parsed.append((d, info))
            except Exception:
                _LOGGER.debug("NextFlagDaySensor - skipping invalid key: %s", iso_key)

        if not parsed:
            self._state = "No upcoming flag day"
            self._attributes = {}
            _LOGGER.warning("NextFlagDaySensor - no parsed dates available")
            return

        today = date.today()
        # Filter future and sort chronologically
        future = [(d, info) for d, info in parsed if d >= today]
        future.sort(key=lambda x: x[0])

        _LOGGER.debug("NextFlagDaySensor - %d future entries after %s", len(future), today.isoformat())
        if not future:
            self._state = "No upcoming flag day"
            self._attributes = {}
            return

        next_d, next_info = future[0]
        self._state = next_d.isoformat()
        self._attributes = {
            "reason": next_info.get("name"),
            "date": next_d.isoformat(),
            "scope": next_info.get("scope"),
            "wimpel": next_info.get("wimpel"),
            "halfstok": next_info.get("halfstok"),
        }
        _LOGGER.debug("NextFlagDaySensor - selected next %s -> %s", next_d.isoformat(), self._attributes)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [
            VlagInstructieTodaySensor(),
            VlagInstructieTomorrowSensor(),
            NextFlagDaySensor(),
        ],
        update_before_add=True,
    )
