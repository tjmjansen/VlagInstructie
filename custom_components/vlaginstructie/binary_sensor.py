from datetime import date, datetime, time
from homeassistant.components.binary_sensor import BinarySensorEntity

from .scraper import get_vlagdagen
from .const import get_variable_days


def _is_flag_day(day: date):
    key = day.strftime("%d-%m")
    vlagdagen = get_vlagdagen()
    vlagdagen.update(get_variable_days(day.year))
    return vlagdagen.get(key)


class HalfstokBinarySensor(BinarySensorEntity):
    """True if today the flag should be flown at half-mast."""

    @property
    def name(self):
        return "vlag_halfstok_today"

    @property
    def unique_id(self):
        return "vlaginstructie_binary_halfmast_today"

    @property
    def is_on(self):
        today = date.today()
        now = datetime.now()
        dag = _is_flag_day(today)

        if not dag:
            return False

        # Special rule: May 4th -> only until 18:00
        if today.day == 4 and today.month == 5:
            return now.time() < time(18, 0)

        return dag.get("halfstok", False)
