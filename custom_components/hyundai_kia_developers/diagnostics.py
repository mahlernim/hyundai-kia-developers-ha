"""Diagnostics support for Hyundai Kia Developers."""

from __future__ import annotations

import re
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant

from .const import (
    CONF_CAR_ID,
    CONF_REDIRECT_URI,
    CONF_REFRESH_TOKEN,
    EntityKey,
)
from .models import EntityResult, HyundaiKiaConfigEntry

TO_REDACT = {
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_REFRESH_TOKEN,
    CONF_REDIRECT_URI,
    CONF_CAR_ID,
}
SAFE_PROVIDER_ERROR_CODE = re.compile(r"^[A-Za-z0-9._-]{1,32}$")


def safe_provider_error_code(value: str | None) -> str | None:
    """Return a bounded provider error identifier without arbitrary text."""
    if value and SAFE_PROVIDER_ERROR_CODE.fullmatch(value):
        return value
    return None


def metric_diagnostics(result: EntityResult | None) -> dict[str, Any]:
    """Return safe diagnostic details for one vehicle metric."""
    available = bool(result and result.value and not result.error)
    return {
        "available": available,
        "value": result.value.value if available and result else None,
        "timestamp": result.value.timestamp if available and result else None,
        "error": result.error if result else None,
        "provider_error_code": (
            safe_provider_error_code(result.error_code) if result else None
        ),
        "operation": result.error_operation if result else None,
        "http_status": result.error_status if result else None,
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: HyundaiKiaConfigEntry
) -> dict[str, Any]:
    """Return redacted diagnostics for a config entry."""
    runtime = entry.runtime_data
    vehicles: list[dict[str, Any]] = []
    for subentry_id, subentry in entry.subentries.items():
        metric_data = runtime.coordinator.data.get(subentry_id, {})
        vehicles.append(
            {
                "title": subentry.title,
                "subentry_type": subentry.subentry_type,
                "data": async_redact_data(dict(subentry.data), TO_REDACT),
                "metrics": {
                    key.value: metric_diagnostics(metric_data.get(key))
                    for key in EntityKey
                },
            }
        )
    return {
        "entry": {
            "title": entry.title,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": runtime.coordinator.last_update_success,
            "vehicle_count": len(vehicles),
            "vehicles": vehicles,
        },
    }
