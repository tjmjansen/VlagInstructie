"""Data coordinator for the Vlaginstructie integration."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .scraper import fetch_vlagdagen

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=5)


class VlagInstructieDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinate fetching Dutch flag instruction data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch the latest flag instruction data."""
        return await fetch_vlagdagen()
