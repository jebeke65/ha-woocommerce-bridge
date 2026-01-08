from __future__ import annotations

import asyncio

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_ENDPOINT,
    CONF_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)


async def _test_connection(endpoint: str, token: str) -> None:
    headers = {"Accept": "application/json", "X-HA-Token": token}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            endpoint,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status == 403:
                raise ValueError("forbidden")
            if resp.status >= 400:
                raise ValueError(f"http_{resp.status}")
            await resp.json()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            endpoint = user_input[CONF_ENDPOINT].strip()
            token = user_input[CONF_TOKEN].strip()

            try:
                await _test_connection(endpoint, token)
            except ValueError as e:
                if str(e) == "forbidden":
                    errors["base"] = "forbidden"
                else:
                    errors["base"] = "cannot_connect"
            except (aiohttp.ClientError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title="WooCommerce Bridge",
                    data={
                        CONF_ENDPOINT: endpoint,
                        CONF_TOKEN: token,
                        CONF_SCAN_INTERVAL: user_input.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_ENDPOINT,
                    default="https://jouwdomein.be/wp-json/wp-ha/v1/open-orders",
                ): str,
                vol.Required(CONF_TOKEN): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.Coerce(int),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        errors = {}

        current_endpoint = self.config_entry.options.get(CONF_ENDPOINT, self.config_entry.data.get(CONF_ENDPOINT))
        current_token = self.config_entry.options.get(CONF_TOKEN, self.config_entry.data.get(CONF_TOKEN))
        current_scan = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        if user_input is not None:
            endpoint = user_input[CONF_ENDPOINT].strip()
            token = user_input[CONF_TOKEN].strip()

            try:
                await _test_connection(endpoint, token)
            except ValueError as e:
                if str(e) == "forbidden":
                    errors["base"] = "forbidden"
                else:
                    errors["base"] = "cannot_connect"
            except (aiohttp.ClientError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_ENDPOINT, default=current_endpoint): str,
                vol.Required(CONF_TOKEN, default=current_token): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=current_scan): vol.Coerce(int),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
