"""Tests for entity applicability and polling groups."""

from types import SimpleNamespace

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTime

from custom_components.hyundai_kia_developers.binary_sensor import (
    BINARY_SENSOR_DESCRIPTIONS,
    HyundaiKiaBinarySensor,
)
from custom_components.hyundai_kia_developers.const import (
    DEFAULT_ENTITY_KEYS,
    ENTITY_ENDPOINT,
    EV_VEHICLE_TYPES,
    WARNING_ENTITY_KEYS,
    EndpointKey,
    EntityKey,
    VehicleType,
)
from custom_components.hyundai_kia_developers.models import EntityResult, EntityValue
from custom_components.hyundai_kia_developers.sensor import (
    SENSOR_DESCRIPTIONS,
    HyundaiKiaSensor,
)


def test_existing_entity_keys_remain_stable() -> None:
    """Existing unique-ID suffixes do not change."""
    assert EntityKey.DISTANCE_TO_EMPTY.value == "distance_to_empty"
    assert EntityKey.ODOMETER.value == "odometer"
    assert [key.value for key in WARNING_ENTITY_KEYS] == [
        "low_fuel_warning",
        "tire_pressure_warning",
        "lamp_wire_warning",
        "smart_key_battery_warning",
        "washer_fluid_warning",
        "brake_fluid_warning",
        "engine_oil_warning",
    ]


def test_hev_does_not_support_ev_entities() -> None:
    """EV-only descriptions exclude the live Niro HEV vehicle type."""
    ev_sensor_descriptions = [
        description
        for description in SENSOR_DESCRIPTIONS
        if description.applicable_types == EV_VEHICLE_TYPES
    ]
    ev_binary_descriptions = [
        description
        for description in BINARY_SENSOR_DESCRIPTIONS
        if description.applicable_types == EV_VEHICLE_TYPES
    ]
    assert ev_sensor_descriptions
    assert ev_binary_descriptions
    assert VehicleType.HYBRID not in EV_VEHICLE_TYPES


def test_new_entity_defaults() -> None:
    """The combined warning is enabled while detailed entities remain optional."""
    sensors = {
        description.entity_key: description for description in SENSOR_DESCRIPTIONS
    }
    binary = {
        description.entity_key: description
        for description in BINARY_SENSOR_DESCRIPTIONS
    }
    assert sensors[EntityKey.EV_BATTERY_LEVEL].entity_registry_enabled_default
    assert binary[EntityKey.CHARGING].entity_registry_enabled_default
    assert binary[EntityKey.VEHICLE_WARNING].entity_registry_enabled_default
    contract = sensors[EntityKey.CONNECTED_SERVICE_FREE_DAYS_REMAINING]
    assert contract.entity_registry_enabled_default
    assert contract.device_class is SensorDeviceClass.DURATION
    assert contract.native_unit_of_measurement is UnitOfTime.DAYS
    assert contract.state_class is None
    assert not sensors[EntityKey.CHARGER_TYPE].entity_registry_enabled_default
    assert not binary[EntityKey.LOW_FUEL_WARNING].entity_registry_enabled_default
    assert EntityKey.VEHICLE_WARNING in DEFAULT_ENTITY_KEYS


def test_charging_entities_share_one_endpoint() -> None:
    """Enabling several charging entities still requires one HTTP endpoint."""
    keys = {
        EntityKey.CHARGING,
        EntityKey.CHARGING_CABLE_CONNECTED,
        EntityKey.CHARGER_TYPE,
        EntityKey.TARGET_STATE_OF_CHARGE,
        EntityKey.REMAINING_CHARGING_TIME,
    }
    assert {ENTITY_ENDPOINT[key] for key in keys} == {EndpointKey.EV_CHARGING}


def test_vehicle_warning_attributes_are_stable() -> None:
    """Combined warning attributes expose sorted stable identifiers."""
    results = {
        key: EntityResult(key=key, value=EntityValue(False))
        for key in WARNING_ENTITY_KEYS
    }
    results[EntityKey.LOW_FUEL_WARNING] = EntityResult(
        key=EntityKey.LOW_FUEL_WARNING, value=EntityValue(True)
    )
    results[EntityKey.ENGINE_OIL_WARNING] = EntityResult(
        key=EntityKey.ENGINE_OIL_WARNING,
        value=None,
        error="HyundaiKiaVehicleError",
    )
    entity = object.__new__(HyundaiKiaBinarySensor)
    entity._entity_key = EntityKey.VEHICLE_WARNING
    entity._subentry_id = "vehicle-1"
    entity.coordinator = SimpleNamespace(data={"vehicle-1": results})

    assert entity.extra_state_attributes == {
        "warning_count": 1,
        "active_warnings": ["low_fuel_warning"],
        "unavailable_warnings": ["engine_oil_warning"],
    }


def test_contract_sensor_attributes_are_stable() -> None:
    """Contract sensor attributes retain their automation-facing names."""
    attributes = {
        "subscription_date": "2024-01-15",
        "free_service_end_date": "2026-08-01",
        "expired": False,
    }
    key = EntityKey.CONNECTED_SERVICE_FREE_DAYS_REMAINING
    entity = object.__new__(HyundaiKiaSensor)
    entity._entity_key = key
    entity._subentry_id = "vehicle-1"
    entity.coordinator = SimpleNamespace(
        data={
            "vehicle-1": {
                key: EntityResult(key=key, value=EntityValue(5, attributes=attributes))
            }
        }
    )

    assert entity.native_value == 5
    assert entity.extra_state_attributes == attributes
