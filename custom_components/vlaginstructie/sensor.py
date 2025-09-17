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
                "reason": dag.get("name"),   # ✅ reason attribute
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
        self._state, self._attributes = self._get_instruction(date.today())


class VlagInstructieTomorrowSensor(VlagInstructieBaseSensor):
    """Sensor showing tomorrow's flag instruction."""

    def __init__(self):
        super().__init__(
            name="vlaginstructie_tomorrow",
            unique_id="vlaginstructie_sensor_tomorrow",
            target_day=date.today() + timedelta(days=1)
        )

    def update(self):
        self._state, self._attributes = self._get_instruction(
            date.today() + timedelta(days=1)
        )


class NextFlagDaySensor(Entity):
    """Sensor showing the next upcoming flag day."""

    def __init__(self):
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return "next_flag_day"

    @property
    def unique_id(self):
        return "vlaginstructie_sensor_next_flag_day"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        today = date.today()
        vlagdagen = get_vlagdagen()
        vlagdagen.update(get_variable_days(today.year))
        vlagdagen.update(get_variable_days(today.year + 1))  # cover year change

        # maak lijst van alle toekomstige vlagdagen als echte date objecten
        upcoming = []
        for key, info in vlagdagen.items():
            day, month = map(int, key.split("-"))
            year = today.year
            candidate = date(year, month, day)

            # als datum al geweest is, neem volgend jaar
            if candidate < today:
                candidate = date(year + 1, month, day)

            upcoming.append((candidate, info))

        if upcoming:
            next_day, info = sorted(upcoming, key=lambda x: x[0])[0]
            self._state = info.get("name")
            self._attributes = {
                "reason": info.get("name"),  # ✅ reason attribute
                "date": next_day.isoformat(),
                "scope": info.get("scope", "all"),
                "wimpel": info.get("wimpel", False),
                "halfstok": info.get("halfstok", False),
            }
        else:
            self._state = "No upcoming flag day"
            self._attributes = {}
