from datetime import date, timedelta
from homeassistant.helpers.entity import Entity

from .scraper import get_vlagdagen
from .const import get_variable_days


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Vlaginstructie sensors from a config entry."""
    async_add_entities([
        VlagInstructieTodaySensor(),
        VlagInstructieTomorrowSensor(),
        NextFlagDaySensor(),
    ], True)


class VlagInstructieBaseSensor(Entity):
    """Base class for Vlaginstructie sensors with shared logic."""

    def __init__(self, name: str, unique_id: str, target_day: date):
        self._name = name
        self._unique_id = unique_id
        self._target_day = target_day
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

    def _get_instruction(self, day: date):
        """Return flag instruction for a specific day."""
        key = day.strftime("%d-%m")
        vlagdagen = get_vlagdagen()
        vlagdagen.update(get_variable_days(day.year))

        dag = vlagdagen.get(key)
        if dag:
            return dag.get("name"), {
                "reason": dag.get("name"),   # reason attribute
                "scope": dag.get("scope", "all"),
                "wimpel": dag.get("wimpel", False),
                "halfstok": dag.get("halfstok", False),
                "date": day.isoformat(),
            }
        return "No flag instruction", {"date": day.isoformat()}


class VlagInstructieTodaySensor(VlagInstructieBaseSensor):
    """Sensor showing today's flag instruction."""

    def __init__(self):
        super().__init__(
            name="vlaginstructie_today",
            unique_id="vlaginstructie_sensor_today",
            target_day=date.today()
        )

    def update(self):
        self._state, self._attributes =
