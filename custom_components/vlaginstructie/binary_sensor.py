from datetime import date, datetime, time, timedelta
from homeassistant.components.binary_sensor import BinarySensorEntity
import logging

from .scraper import fetch_vlagdagen

_LOGGER = logging.getLogger(__name__)


def _get_info_for_day(day: date, vlagdagen):
    """Return vlaginfo dict for given day if it exists."""
    return vlagdagen.get(day.isoformat())


class VlagUithangenToday(BinarySensorEntity):
    @property
    def name(self):
        return "vlag_uithangen_today"

    @property
    def unique_id(self):
        return "vlaginstructie_binary_uithangen_today"

    @property
    def is_on(self):
        today = date.today()
        info = self._info
        if not info:
            return False
        # halfstok betekent dat hij WEL moet hangen, maar halfstok
        return True

    async def async_update(self):
        vlagdagen = await fetch_vlagdagen()
        self._info = _get_info_for_day(date.today(), vlagdagen)


class VlagHalfstokToday(BinarySensorEntity):
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
        info = self._info
        if not info:
            return False

        # Speciale regel: 4 mei -> halfstok tot 18:00, daarna wel uithangen
        if today.day == 4 and today.month == 5:
            return now.time() < time(18, 0)

        return info.get("halfstok", False)

    async def async_update(self):
        vlagdagen = await fetch_vlagdagen()
        self._info = _get_info_for_day(date.today(), vlagdagen)


class VlagUithangenTomorrow(BinarySensorEntity):
    @property
    def name(self):
        return "vlag_uithangen_tomorrow"

    @property
    def unique_id(self):
        return "vlaginstructie_binary_uithangen_tomorrow"

    @property
    def is_on(self):
        return bool(self._info)

    async def async_update(self):
        vlagdagen = await fetch_vlagdagen()
        tomorrow = date.today() + timedelta(days=1)
        self._info = _get_info_for_day(tomorrow, vlagdagen)


class VlagHalfstokTomorrow(BinarySensorEntity):
    @property
    def name(self):
        return "vlag_halfstok_tomorrow"

    @property
    def unique_id(self):
        return "vlaginstructie_binary_halfstok_tomorrow"

    @property
    def is_on(self):
        tomorrow = date.today() + timedelta(days=1)
        if not self._info:
            return False

        # Voor morgen hoef je geen tijdsgrens (18:00) te checken
        return self._info.get("halfstok", False)

    async def async_update(self):
        vlagdagen = await fetch_vlagdagen()
        tomorrow = date.today() + timedelta(days=1)
        self._info = _get_info_for_day(tomorrow, vlagdagen)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [
            VlagUithangenToday(),
            VlagHalfstokToday(),
            VlagUithangenTomorrow(),
            VlagHalfstokTomorrow(),
        ],
        update_before_add=True,
    )
