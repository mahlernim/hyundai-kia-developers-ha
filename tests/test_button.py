"""Tests for the account-level vehicle data refresh button."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.const import Platform
from homeassistant.helpers.entity import EntityCategory

from custom_components.hyundai_kia_developers.button import (
    HyundaiKiaRefreshVehicleDataButton,
    async_setup_entry,
)
from custom_components.hyundai_kia_developers.const import PLATFORMS


@pytest.mark.asyncio
async def test_setup_creates_one_account_refresh_button() -> None:
    """One button is created for the account rather than for each vehicle."""
    coordinator = SimpleNamespace(async_request_refresh=AsyncMock())
    entry = SimpleNamespace(
        unique_id="kia:account-1",
        entry_id="entry-1",
        runtime_data=SimpleNamespace(coordinator=coordinator),
        subentries={"vehicle-1": object(), "vehicle-2": object()},
    )
    async_add_entities = Mock()

    await async_setup_entry(SimpleNamespace(), entry, async_add_entities)

    entities = async_add_entities.call_args.args[0]
    assert len(entities) == 1
    assert entities[0].unique_id == "kia:account-1_refresh_vehicle_data"


@pytest.mark.asyncio
async def test_button_requests_one_account_refresh() -> None:
    """Pressing the button delegates to the existing account coordinator."""
    coordinator = SimpleNamespace(async_request_refresh=AsyncMock())
    entry = SimpleNamespace(unique_id="kia:account-1", entry_id="entry-1")
    entity = HyundaiKiaRefreshVehicleDataButton(entry, coordinator)

    await entity.async_press()

    coordinator.async_request_refresh.assert_awaited_once_with()
    assert entity.available
    assert entity.device_info is None
    assert entity.entity_category is EntityCategory.DIAGNOSTIC
    assert entity.device_class is None


def test_button_platform_is_loaded() -> None:
    """The config entry forwards setup and unload to the button platform."""
    assert Platform.BUTTON in PLATFORMS
