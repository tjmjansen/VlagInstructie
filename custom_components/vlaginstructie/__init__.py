"""VlagInstructie integration."""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from . import sensor

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up is not used because this integration uses config flow."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up VlagInstructie from a config entry."""
    # registreer de sensors
    await sensor.async_setup_entry(hass, entry, hass.async_add_entities)
    return True