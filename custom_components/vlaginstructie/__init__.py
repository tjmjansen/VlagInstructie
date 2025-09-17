"""VlagInstructie integration."""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from . import sensor

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up is not used because this integration uses config flow."""
    return True

async def async_setup_entry(hass, entry):
    """Set up VlagInstructie from a config entry."""
    # registreer de sensors via hass.data en hass.helpers.entity_platform
    hass.helpers.discovery.load_platform('sensor', 'vlaginstructie', {}, entry.data)
    return True