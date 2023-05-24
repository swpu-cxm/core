"""Tests for the Airzone integration."""

from typing import Any
from unittest.mock import patch

from aioairzone_cloud.const import (
    API_AZ_SYSTEM,
    API_AZ_ZONE,
    API_CELSIUS,
    API_CONFIG,
    API_CONNECTION_DATE,
    API_DEVICE_ID,
    API_DEVICES,
    API_DISCONNECTION_DATE,
    API_FAH,
    API_GROUPS,
    API_HUMIDITY,
    API_INSTALLATION_ID,
    API_INSTALLATIONS,
    API_IS_CONNECTED,
    API_LOCAL_TEMP,
    API_META,
    API_NAME,
    API_STAT_AP_MAC,
    API_STAT_CHANNEL,
    API_STAT_QUALITY,
    API_STAT_SSID,
    API_STATUS,
    API_SYSTEM_NUMBER,
    API_TYPE,
    API_WS_FW,
    API_WS_ID,
    API_WS_IDS,
    API_WS_TYPE,
    API_ZONE_NUMBER,
)
from aioairzone_cloud.device import Device

from homeassistant.components.airzone_cloud import DOMAIN
from homeassistant.const import CONF_ID, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry

WS_ID = "11:22:33:44:55:66"

CONFIG = {
    CONF_ID: "inst1",
    CONF_USERNAME: "user",
    CONF_PASSWORD: "pass",
}

GET_INSTALLATION_MOCK = {
    API_GROUPS: [
        {
            API_NAME: "Group",
            API_DEVICES: [
                {
                    API_DEVICE_ID: "system1",
                    API_TYPE: API_AZ_SYSTEM,
                    API_META: {
                        API_SYSTEM_NUMBER: 1,
                    },
                    API_WS_ID: WS_ID,
                },
                {
                    API_DEVICE_ID: "zone1",
                    API_NAME: "Salon",
                    API_TYPE: API_AZ_ZONE,
                    API_META: {
                        API_SYSTEM_NUMBER: 1,
                        API_ZONE_NUMBER: 1,
                    },
                    API_WS_ID: WS_ID,
                },
                {
                    API_DEVICE_ID: "zone2",
                    API_NAME: "Dormitorio",
                    API_TYPE: API_AZ_ZONE,
                    API_META: {
                        API_SYSTEM_NUMBER: 1,
                        API_ZONE_NUMBER: 2,
                    },
                    API_WS_ID: WS_ID,
                },
            ],
        },
    ],
}

GET_INSTALLATIONS_MOCK = {
    API_INSTALLATIONS: [
        {
            API_INSTALLATION_ID: CONFIG[CONF_ID],
            API_NAME: "House",
            API_WS_IDS: [
                WS_ID,
            ],
        },
    ],
}

GET_WEBSERVER_MOCK = {
    API_WS_TYPE: "ws_az",
    API_CONFIG: {
        API_WS_FW: "3.44",
        API_STAT_SSID: "Wifi",
        API_STAT_CHANNEL: 36,
        API_STAT_AP_MAC: "00:00:00:00:00:00",
    },
    API_STATUS: {
        API_IS_CONNECTED: True,
        API_STAT_QUALITY: 4,
        API_CONNECTION_DATE: "2023-05-07T12:55:51.000Z",
        API_DISCONNECTION_DATE: "2023-01-01T22:26:55.376Z",
    },
}


def mock_get_device_status(device: Device) -> dict[str, Any]:
    """Mock API device status."""

    if device.get_id() == "system1":
        return {
            API_IS_CONNECTED: True,
        }
    if device.get_id() == "zone2":
        return {
            API_HUMIDITY: 24,
            API_IS_CONNECTED: True,
            API_LOCAL_TEMP: {
                API_FAH: 77,
                API_CELSIUS: 25,
            },
        }
    return {
        API_HUMIDITY: 30,
        API_IS_CONNECTED: True,
        API_LOCAL_TEMP: {
            API_FAH: 68,
            API_CELSIUS: 20,
        },
    }


async def async_init_integration(
    hass: HomeAssistant,
) -> None:
    """Set up the Airzone integration in Home Assistant."""

    config_entry = MockConfigEntry(
        data=CONFIG,
        domain=DOMAIN,
        unique_id="airzone_cloud_unique_id",
    )
    config_entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.airzone_cloud.AirzoneCloudApi.api_get_device_status",
        side_effect=mock_get_device_status,
    ), patch(
        "homeassistant.components.airzone_cloud.AirzoneCloudApi.api_get_installation",
        return_value=GET_INSTALLATION_MOCK,
    ), patch(
        "homeassistant.components.airzone_cloud.AirzoneCloudApi.api_get_installations",
        return_value=GET_INSTALLATIONS_MOCK,
    ), patch(
        "homeassistant.components.airzone_cloud.AirzoneCloudApi.api_get_webserver",
        return_value=GET_WEBSERVER_MOCK,
    ), patch(
        "homeassistant.components.airzone_cloud.AirzoneCloudApi.login",
        return_value=None,
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()