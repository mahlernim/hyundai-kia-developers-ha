"""Button platform for Hyundai Kia Developers."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import HyundaiKiaDataUpdateCoordinator
from .models import HyundaiKiaConfigEntry

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HyundaiKiaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up one account-level refresh button."""
    async_add_entities(
        [HyundaiKiaRefreshVehicleDataButton(entry, entry.runtime_data.coordinator)]
    )


class HyundaiKiaRefreshVehicleDataButton(ButtonEntity):
    """Refresh all enabled vehicle data for one configured account."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True
    _attr_icon = "mdi:refresh"
    _attr_translation_key = "refresh_vehicle_data"

    def __init__(
        self,
        entry: HyundaiKiaConfigEntry,
        coordinator: HyundaiKiaDataUpdateCoordinator,
    ) -> None:
        """Initialize the account refresh button."""
        account_id = entry.unique_id or entry.entry_id
        self._attr_unique_id = f"{account_id}_refresh_vehicle_data"
        self._coordinator = coordinator

    async def async_press(self) -> None:
        """Request an immediate refresh of every enabled account endpoint."""
        await self._coordinator.async_request_refresh()
