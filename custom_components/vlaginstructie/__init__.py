from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from . import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up via configuration.yaml (legacy)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up via UI config entries."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    unload_ok &= await hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")
    return unload_ok