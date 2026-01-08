from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ENDPOINT,
    CONF_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class WooBridgeCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.endpoint = entry.data[CONF_ENDPOINT].rstrip("/")
        self.token = entry.data[CONF_TOKEN]

        scan = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=int(scan)),
        )

    async def _async_update_data(self) -> dict:
        headers = {
            "Accept": "application/json",
            "X-HA-Token": self.token,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.endpoint,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 403:
                        raise UpdateFailed("Forbidden (token incorrect of ontbreekt)")
                    if resp.status >= 400:
                        text = await resp.text()
                        raise UpdateFailed(f"HTTP {resp.status}: {text[:200]}")
                    return await resp.json()
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout contacting Woo endpoint") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
