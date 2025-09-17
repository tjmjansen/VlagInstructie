"""Sensors for Vlaginstructie: today, tomorrow and next flag day.

NextFlagDaySensor now scans day-by-day (0..365) and picks the first match.
Extensive debug logging has been added to help understand the selection.
"""

import logging
from datetime import date, timedelta
from homeassistant.components.sensor import SensorEntity

from .scraper import fetch_vlagdagen

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up vlaginstructie sensors via config entry."""
    async_add_entities(
        [
            VlagInstructieTodaySensor(),
            VlagInstructieTomorrowSensor(),
            NextFlagDaySensor(),
        ],
        update_before_add=True,
    )

class VlagInstructieTodaySensor(SensorEntity):
    """Sensor showing today's flag instruction."""

    def __init__(self):
        self._name = "vlaginstructie_today"
        self._unique_id = "vlaginstructie_sensor_today"
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

    async def async_update(self):
        """Async update: fetch vlagdagen and set today's state."""
        vlagdagen = await fetch_vlagdagen()
        _LOGGER.debug("TodaySensor - fetched %d vlagdagen: %s", len(vlagdagen), sorted(vlagdagen.keys()))
        today = date.today()
        key = today.strftime("%d-%m")
        dag = vlagdagen.get(key)

        if dag:
            self._state = dag.get("name")
            self._attributes = {
                "reason": dag.get("name"),
                "date": today.isoformat(),
                "scope": dag.get("scope"),
                "wimpel": dag.get("wimpel"),
                "halfstok": dag.get("halfstok"),
            }
            _LOGGER.debug("TodaySensor - match for key %s -> %s", key, self._attributes)
        else:
            self._state = "No flag instruction"
            self._attributes = {"date": today.isoformat()}
            _LOGGER.debug("TodaySensor - no match for today (%s)", key)


class VlagInstructieTomorrowSensor(SensorEntity):
    """Sensor showing tomorrow's flag instruction."""

    def __init__(self):
        self._name = "vlaginstructie_tomorrow"
        self._unique_id = "vlaginstructie_sensor_tomorrow"
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

    async def async_update(self):
        """Async update: fetch vlagdagen and set tomorrow's state."""
        vlagdagen = await fetch_vlagdagen()
        _LOGGER.debug("TomorrowSensor - fetched %d vlagdagen: %s", len(vlagdagen), sorted(vlagdagen.keys()))
        tomorrow = date.today() + timedelta(days=1)
        key = tomorrow.strftime("%d-%m")
        dag = vlagdagen.get(key)

        if dag:
            self._state = dag.get("name")
            self._attributes = {
                "reason": dag.get("name"),
                "date": tomorrow.isoformat(),
                "scope": dag.get("scope"),
                "wimpel": dag.get("wimpel"),
                "halfstok": dag.get("halfstok"),
            }
            _LOGGER.debug("TomorrowSensor - match for key %s -> %s", key, self._attributes)
        else:
            self._state = "No flag instruction"
            self._attributes = {"date": tomorrow.isoformat()}
            _LOGGER.debug("TomorrowSensor - no match for tomorrow (%s)", key)


class NextFlagDaySensor(SensorEntity):
    """Sensor showing the next upcoming flag day.

    This sensor scans day-by-day from today up to 365 days ahead and picks the
    first day that matches a key in the vlagdagen dict. This avoids problems
    with ambiguous dd-mm keys and incorrect sorting.
    """

    def __init__(self):
        self._name = "next_flag_day"
        self._unique_id = "vlaginstructie_sensor_next_flag_day"
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

    async def async_update(self):
        """Async update: find and set the next flag day."""
        vlagdagen = await fetch_vlagdagen()
        _LOGGER.debug("NextFlagDaySensor - fetched %d vlagdagen: %s", len(vlagdagen), sorted(vlagdagen.keys()))

        if not vlagdagen:
            _LOGGER.warning("NextFlagDaySensor - no vlagdagen available (empty dict).")
            self._state = "No upcoming flag day"
            self._attributes = {}
            return

        today = date.today()
        found = False
        scanned_days = 0

        # Scan up to 365 days ahead for the first matching dd-mm
        for delta in range(0, 366):
            candidate = today + timedelta(days=delta)
            key = candidate.strftime("%d-%m")
            scanned_days += 1
            info = vlagdagen.get(key)
            if info:
                # found the next flag day
                _LOGGER.debug(
                    "NextFlagDaySensor - found candidate on attempt %d: %s (key=%s) -> %s",
                    delta + 1, candidate.isoformat(), key, info
                )
                self._state = info.get("name")
                self._attributes = {
                    "reason": info.get("name"),
                    "date": candidate.isoformat(),
                    "scope": info.get("scope"),
                    "wimpel": info.get("wimpel"),
                    "halfstok": info.get("halfstok"),
                }
                found = True
                break
            else:
                # debug trace optional but helpful when troubleshooting
                _LOGGER.debug("NextFlagDaySensor - no match for %s (key=%s)", candidate.isoformat(), key)

        if not found:
            _LOGGER.warning("NextFlagDaySensor - scanned %d days, no upcoming flag day found.", scanned_days)
            self._state = "No upcoming flag day"
            self._attributes = {}
