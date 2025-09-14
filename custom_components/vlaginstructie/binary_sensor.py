from datetime import date
from homeassistant.components.binary_sensor import BinarySensorEntity
from .scraper import get_vlagdagen
from .const import get_variable_days

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([VlagDagBinarySensor(), HalfstokBinarySensor()], True)

async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([VlagDagBinarySensor(), HalfstokBinarySensor()], True)


class VlagDagBinarySensor(BinarySensorEntity):
    """True als vandaag een vlagdag is (vol of halfstok)."""

    def __init__(self):
        self._is_on = False
        self._attributes = {}

    @property
    def name(self):
        return "vlag_uithangen_today"

    @property
    def is_on(self):
        return self._is_on

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        today = date.today()
        key = today.strftime("%d-%m")

        vlagdagen = get_vlagdagen()
        vlagdagen.update(get_variable_days(today.year))

        dag = vlagdagen.get(key)
        if dag:
            self._is_on = True
            self._attributes = dag
        else:
            self._is_on = False
            self._attributes = {}


class HalfstokBinarySensor(BinarySensorEntity):
    """True als vandaag halfstok moet worden gevlagd."""

    def __init__(self):
        self._is_on = False
        self._attributes = {}

    @property
    def name(self):
        return "vlag_halfstok_today"

    @property
    def is_on(self):
        return self._is_on

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        today = date.today()
        key = today.strftime("%d-%m")

        vlagdagen = get_vlagdagen()
        vlagdagen.update(get_variable_days(today.year))

        dag = vlagdagen.get(key)
        if dag and dag.get("halfstok", False):
            self._is_on = True
            self._attributes = dag
        else:
            self._is_on = False
            self._attributes = {}
