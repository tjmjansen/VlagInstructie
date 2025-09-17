from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

PLATFORMS = ["sensor", "binary_sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up is not used because this integration uses config flow."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up VlagInstructie from a config entry."""
    # Forward setup to sensor platform(s)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
