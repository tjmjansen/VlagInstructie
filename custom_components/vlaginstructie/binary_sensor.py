from datetime import date, datetime, time, timedelta
from homeassistant.components.binary_sensor import BinarySensorEntity
from .scraper import fetch_vlagdagen, get_variable_days

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        VlagUithangenTodaySensor(),
        VlagHalfstokTodaySensor(),
        VlagUithangenTomorrowSensor(),
        VlagHalfstokTomorrowSensor()
    ], True)

# Basisklasse
class VlagBinaryBase(BinarySensorEntity):
    def __init__(self, name, check_halfstok=False, day_offset=0):
        self._name = name
        self._check_halfstok = check_halfstok
        self._day_offset = day_offset
        self._is_on = False
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._is_on

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        """Update sensor state asynchronously."""
        vlagdagen = await fetch_vlagdagen()
        vlagdagen.update(get_variable_days(date.today().year))

        target_day = date.today() + timedelta(days=self._day_offset)
        key = target_day.strftime("%d-%m")
        dag = vlagdagen.get(key)

        if dag:
            self._attributes = {"reason": dag.get("name"), "date": target_day.isoformat()}

            if self._check_halfstok:
                # Special rule: May 4th -> only until 18:00
                if target_day.day == 4 and target_day.month == 5 and self._day_offset == 0:
                    now = datetime.now().time()
                    self._is_on = dag.get("halfstok", False) and now < time(18, 0)
                else:
                    self._is_on = dag.get("halfstok", False)
            else:
                # Uithangen sensor
                self._is_on = True
        else:
            self._is_on = False
            self._attributes = {"date": target_day.isoformat()}

# Vandaag
class VlagUithangenTodaySensor(VlagBinaryBase):
    def __init__(self):
        super().__init__("vlag_uithangen_today", check_halfstok=False, day_offset=0)

class VlagHalfstokTodaySensor(VlagBinaryBase):
    def __init__(self):
        super().__init__("vlag_halfstok_today", check_halfstok=True, day_offset=0)

# Morgen
class VlagUithangenTomorrowSensor(VlagBinaryBase):
    def __init__(self):
        super().__init__("vlag_uithangen_tomorrow", check_halfstok=False, day_offset=1)

class VlagHalfstokTomorrowSensor(VlagBinaryBase):
    def __init__(self):
        super().__init__("vlag_halfstok_tomorrow", check_halfstok=True, day_offset=1)
