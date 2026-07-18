"""Sensor platform for Hyundai Kia Developers."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import CONF_CAR_ID, SUBENTRY_TYPE_VEHICLE, Metric
from .coordinator import HyundaiKiaDataUpdateCoordinator
from .entity import HyundaiKiaVehicleEntity
from .models import HyundaiKiaConfigEntry

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class HyundaiKiaSensorEntityDescription(SensorEntityDescription):
    """Describe a Hyundai/Kia sensor."""

    metric: Metric


SENSOR_DESCRIPTIONS: tuple[HyundaiKiaSensorEntityDescription, ...] = (
    HyundaiKiaSensorEntityDescription(
        key=Metric.DISTANCE_TO_EMPTY,
        metric=Metric.DISTANCE_TO_EMPTY,
        translation_key=Metric.DISTANCE_TO_EMPTY,
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    HyundaiKiaSensorEntityDescription(
        key=Metric.ODOMETER,
        metric=Metric.ODOMETER,
        translation_key=Metric.ODOMETER,
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HyundaiKiaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors for every vehicle subentry."""
    coordinator = entry.runtime_data.coordinator
    for subentry_id, subentry in entry.subentries.items():
        if subentry.subentry_type != SUBENTRY_TYPE_VEHICLE:
            continue
        car_id = str(subentry.data[CONF_CAR_ID])
        async_add_entities(
            [
                HyundaiKiaSensor(
                    entry,
                    coordinator,
                    subentry_id,
                    car_id,
                    subentry.title,
                    description,
                )
                for description in SENSOR_DESCRIPTIONS
            ],
            config_subentry_id=subentry_id,
        )


class HyundaiKiaSensor(HyundaiKiaVehicleEntity, SensorEntity):
    """Represent one vehicle metric."""

    entity_description: HyundaiKiaSensorEntityDescription

    def __init__(
        self,
        entry: HyundaiKiaConfigEntry,
        coordinator: HyundaiKiaDataUpdateCoordinator,
        subentry_id: str,
        car_id: str,
        car_name: str,
        description: HyundaiKiaSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            entry,
            coordinator,
            subentry_id,
            car_id,
            car_name,
            description.metric,
        )
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the native metric value."""
        result = self.metric_result
        return result.value.value if result and result.value else None
