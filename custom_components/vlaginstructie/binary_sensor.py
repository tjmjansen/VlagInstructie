from datetime import date, datetime, time, timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


def _get_info_for_day(day: date, vlagdagen):
    """Return vlaginfo dict for given day if it exists."""
    return vlagdagen.get(day.isoformat())


class VlagInstructieBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)


class VlagUithangenToday(VlagInstructieBinarySensor):
    @property
    def name(self):
        return "vlag_uithangen_today"

    @property
    def unique_id(self):
        return "vlaginstructie_binary_uithangen_today"

    @property
    def is_on(self):
        info = _get_info_for_day(date.today(), self.coordinator.data)
        if not info:
            return False
        return True


class VlagHalfstokToday(VlagInstructieBinarySensor):
    @property
    def name(self):
        return "vlag_halfstok_today"

    @property
    def unique_id(self):
        return "vlaginstructie_binary_halfstok_today"

    @property
    def is_on(self):
        today = date.today()
        now = datetime.now()
        info = _get_info_for_day(today, self.coordinator.data)
        if not info:
            return False

        if today.day == 4 and today.month == 5:
            return now.time() < time(18, 0)

        return info.get("halfstok", False)


class OranjeWimpelToday(VlagInstructieBinarySensor):
    @property
    def name(self):
        return "oranje_wimpel_today"

    @property
    def unique_id(self):
        return "vlaginstructie_binary_oranje_wimpel_today"

    @property
    def is_on(self):
        info = _get_info_for_day(date.today(), self.coordinator.data)
        if not info:
            return False
        return info.get("wimpel", False)


class OranjeWimpelTomorrow(VlagInstructieBinarySensor):
    @property
    def name(self):
        return "oranje_wimpel_tomorrow"

    @property
    def unique_id(self):
        return "vlaginstructie_binary_oranje_wimpel_tomorrow"

    @property
    def is_on(self):
        tomorrow = date.today() + timedelta(days=1)
        info = _get_info_for_day(tomorrow, self.coordinator.data)
        if not info:
            return False
        return info.get("wimpel", False)


class VlagUithangenTomorrow(VlagInstructieBinarySensor):
    @property
    def name(self):
        return "vlag_uithangen_tomorrow"

    @property
    def unique_id(self):
        return "vlaginstructie_binary_uithangen_tomorrow"

    @property
    def is_on(self):
        tomorrow = date.today() + timedelta(days=1)
        return bool(_get_info_for_day(tomorrow, self.coordinator.data))


class VlagHalfstokTomorrow(VlagInstructieBinarySensor):
    @property
    def name(self):
        return "vlag_halfstok_tomorrow"

    @property
    def unique_id(self):
        return "vlaginstructie_binary_halfstok_tomorrow"

    @property
    def is_on(self):
        tomorrow = date.today() + timedelta(days=1)
        info = _get_info_for_day(tomorrow, self.coordinator.data)
        if not info:
            return False
        return info.get("halfstok", False)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            VlagUithangenToday(coordinator),
            VlagHalfstokToday(coordinator),
            VlagUithangenTomorrow(coordinator),
            VlagHalfstokTomorrow(coordinator),
            OranjeWimpelToday(coordinator),
            OranjeWimpelTomorrow(coordinator),
        ]
    )
