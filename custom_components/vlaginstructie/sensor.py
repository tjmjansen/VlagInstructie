from datetime import date
from homeassistant.helpers.entity import Entity
from .scraper import get_vlagdagen
from .const import get_variable_days

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([VlagInstructieSensor()], True)

async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([VlagInstructieSensor()], True)

class VlagInstructieSensor(Entity):
    def __init__(self):
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return "vlaginstructie"

    @property
    def state(self):
        return self._state

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
            self._state = dag.get("name")
            self._attributes = {
                "scope": dag.get("scope", "alle"),
                "wimpel": dag.get("wimpel", False),
                "halfstok": dag.get("halfstok", False),
                "datum": today.isoformat()
            }
        else:
            self._state = "Geen vlaginstructie"
            self._attributes = {"datum": today.isoformat()}
