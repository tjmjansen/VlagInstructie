"""Sensors for Vlaginstructie using ISO-date keys from scraper."""

import logging
from datetime import date, datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class VlagInstructieBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name: str, unique_id: str):
        super().__init__(coordinator)
        self._name = name
        self._unique_id = unique_id

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id


class VlagInstructieDaySensor(VlagInstructieBaseSensor):
    def __init__(self, coordinator, name: str, unique_id: str, offset_days: int):
        super().__init__(coordinator, name, unique_id)
        self._offset_days = offset_days

    @property
    def _target_date(self):
        return date.today() + timedelta(days=self._offset_days)

    @property
    def state(self):
        info = self.coordinator.data.get(self._target_date.isoformat())
        if info:
            return info.get("name")
        return "No flag instruction"

    @property
    def extra_state_attributes(self):
        target_date = self._target_date
        target_iso = target_date.isoformat()
        info = self.coordinator.data.get(target_iso)
        if info:
            return {
                "reason": info.get("name"),
                "date": target_iso,
                "scope": info.get("scope"),
                "wimpel": info.get("wimpel"),
                "halfstok": info.get("halfstok"),
            }
        return {"date": target_iso}


class VlagInstructieTodaySensor(VlagInstructieDaySensor):
    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            "vlaginstructie_today",
            "vlaginstructie_sensor_today",
            0,
        )


class VlagInstructieTomorrowSensor(VlagInstructieDaySensor):
    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            "vlaginstructie_tomorrow",
            "vlaginstructie_sensor_tomorrow",
            1,
        )


class NextFlagDaySensor(VlagInstructieBaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "next_flag_day", "vlaginstructie_sensor_next_flag_day")

    def _next_flag_day(self):
        vlagdagen = self.coordinator.data
        _LOGGER.debug("NextFlagDaySensor - fetched %d items", len(vlagdagen))

        parsed = []
        for iso_key, info in vlagdagen.items():
            try:
                d = datetime.strptime(iso_key, "%Y-%m-%d").date()
                parsed.append((d, info))
            except Exception:
                _LOGGER.debug("NextFlagDaySensor - skipping invalid key: %s", iso_key)

        if not parsed:
            _LOGGER.warning("NextFlagDaySensor - no parsed dates available")
            return None, None

        today = date.today()
        future = [(d, info) for d, info in parsed if d >= today]
        future.sort(key=lambda x: x[0])

        _LOGGER.debug("NextFlagDaySensor - %d future entries after %s", len(future), today.isoformat())
        if not future:
            return None, None

        return future[0]

    @property
    def state(self):
        next_d, _next_info = self._next_flag_day()
        if not next_d:
            return "No upcoming flag day"
        return next_d.isoformat()

    @property
    def extra_state_attributes(self):
        next_d, next_info = self._next_flag_day()
        if not next_d:
            return {}
        return {
            "reason": next_info.get("name"),
            "date": next_d.isoformat(),
            "scope": next_info.get("scope"),
            "wimpel": next_info.get("wimpel"),
            "halfstok": next_info.get("halfstok"),
        }


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            VlagInstructieTodaySensor(coordinator),
            VlagInstructieTomorrowSensor(coordinator),
            NextFlagDaySensor(coordinator),
        ]
    )
