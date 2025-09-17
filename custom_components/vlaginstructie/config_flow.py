import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class VlaginstructieConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for VlagInstructie."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Vlaginstructie Nederland", data={})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    async def async_get_options_flow(self, config_entry):
        return VlaginstructieOptionsFlowHandler(config_entry)


class VlaginstructieOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for VlagInstructie."""
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(step_id="init", data_schema=vol.Schema({}))
