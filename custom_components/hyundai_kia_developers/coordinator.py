"""Data coordinator for Hyundai Kia Developers."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HyundaiKiaApiClient
from .const import (
    CONF_CAR_ID,
    CONF_CAR_TYPE,
    DEFAULT_ENTITY_KEYS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ENTITY_ENDPOINT,
    EV_DEFAULT_ENTITY_KEYS,
    EV_VEHICLE_TYPES,
    MAX_PARALLEL_REQUESTS,
    SUBENTRY_TYPE_VEHICLE,
    WARNING_ENTITY_KEYS,
    EndpointKey,
    EntityKey,
)
from .exceptions import HyundaiKiaAuthenticationError, HyundaiKiaError
from .models import EntityResult, EntityValue, HyundaiKiaConfigEntry, VehicleProfile

type CoordinatorData = dict[str, dict[EntityKey, EntityResult]]
type EntityContext = tuple[str, EntityKey]
type EndpointJob = tuple[str, EndpointKey]

_LOGGER = logging.getLogger(__name__)


def endpoint_jobs(contexts: set[EntityContext]) -> dict[EndpointJob, set[EntityKey]]:
    """Expand entity contexts into deduplicated endpoint jobs."""
    jobs: dict[EndpointJob, set[EntityKey]] = {}
    for subentry_id, key in contexts:
        requested_keys = (
            WARNING_ENTITY_KEYS if key is EntityKey.VEHICLE_WARNING else (key,)
        )
        for requested_key in requested_keys:
            jobs.setdefault((subentry_id, ENTITY_ENDPOINT[requested_key]), set()).add(
                requested_key
            )
    return jobs


def warning_summary(
    results: dict[EntityKey, EntityResult],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return stable active and unavailable warning identifiers."""
    active: list[str] = []
    unavailable: list[str] = []
    for key in WARNING_ENTITY_KEYS:
        result = results.get(key)
        if not result or not result.value or result.error:
            unavailable.append(key.value)
        elif result.value.value is True:
            active.append(key.value)
    return tuple(sorted(active)), tuple(sorted(unavailable))


def vehicle_warning_result(results: dict[EntityKey, EntityResult]) -> EntityResult:
    """Build the best-effort combined warning result."""
    active, _unavailable = warning_summary(results)
    return EntityResult(
        key=EntityKey.VEHICLE_WARNING,
        value=EntityValue(bool(active)),
    )


class HyundaiKiaDataUpdateCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Coordinate endpoint updates for every vehicle on an account."""

    config_entry: HyundaiKiaConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: HyundaiKiaConfigEntry,
        api: HyundaiKiaApiClient,
        vehicle_profiles: dict[str, VehicleProfile],
    ) -> None:
        """Initialize the coordinator."""
        self.api = api
        self.vehicle_profiles = vehicle_profiles
        self._request_semaphore = asyncio.Semaphore(MAX_PARALLEL_REQUESTS)
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(
                minutes=int(entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL))
            ),
            always_update=False,
        )

    async def _async_update_data(self) -> CoordinatorData:
        """Fetch unique endpoints requested by enabled entity contexts."""
        vehicles = {
            subentry_id: subentry
            for subentry_id, subentry in self.config_entry.subentries.items()
            if subentry.subentry_type == SUBENTRY_TYPE_VEHICLE
        }
        if not vehicles:
            return {}

        contexts = self._valid_contexts(vehicles)
        if not contexts:
            contexts = self._default_contexts(vehicles)

        jobs = endpoint_jobs(contexts)

        tasks = [
            self._async_fetch_endpoint(vehicles[subentry_id], endpoint, requested_keys)
            for (subentry_id, endpoint), requested_keys in sorted(
                jobs.items(), key=lambda item: (item[0][0], item[0][1].value)
            )
        ]
        try:
            results = await asyncio.gather(*tasks)
        except HyundaiKiaAuthenticationError as err:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="invalid_auth",
            ) from err

        previous = self.data or {}
        data: CoordinatorData = {
            subentry_id: dict(previous.get(subentry_id, {})) for subentry_id in vehicles
        }
        successes = 0
        errors: list[Exception] = []
        for subentry_id, values, requested_keys, error in results:
            if error is None:
                successes += 1
                for key, value in values.items():
                    data[subentry_id][key] = EntityResult(key=key, value=value)
                for missing_key in requested_keys - values.keys():
                    data[subentry_id][missing_key] = EntityResult(
                        key=missing_key,
                        value=None,
                        error="DataUnavailable",
                    )
            else:
                errors.append(error)
                for key in requested_keys:
                    data[subentry_id][key] = EntityResult(
                        key=key,
                        value=None,
                        error=error.__class__.__name__,
                    )

        warning_subentries = {
            subentry_id
            for subentry_id, key in contexts
            if key is EntityKey.VEHICLE_WARNING
        }
        for subentry_id in warning_subentries:
            data[subentry_id][EntityKey.VEHICLE_WARNING] = vehicle_warning_result(
                data[subentry_id]
            )

        if errors and not successes:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
            ) from errors[0]
        return data

    def _valid_contexts(
        self, vehicles: dict[str, ConfigSubentry]
    ) -> set[EntityContext]:
        """Return valid entity contexts registered with the coordinator."""
        return {
            context
            for context in set(self.async_contexts())
            if isinstance(context, tuple)
            and len(context) == 2
            and context[0] in vehicles
            and isinstance(context[1], EntityKey)
        }

    def _default_contexts(
        self, vehicles: dict[str, ConfigSubentry]
    ) -> set[EntityContext]:
        """Return initial contexts before entities have been added."""
        contexts = {
            (subentry_id, key)
            for subentry_id in vehicles
            for key in DEFAULT_ENTITY_KEYS
        }
        for subentry_id, subentry in vehicles.items():
            if self.car_type(subentry) in EV_VEHICLE_TYPES:
                contexts.update((subentry_id, key) for key in EV_DEFAULT_ENTITY_KEYS)
        return contexts

    async def _async_fetch_endpoint(
        self,
        subentry: ConfigSubentry,
        endpoint: EndpointKey,
        requested_keys: set[EntityKey],
    ) -> tuple[
        str,
        dict[EntityKey, EntityValue],
        set[EntityKey],
        Exception | None,
    ]:
        """Fetch one endpoint and retain partial-failure context."""
        try:
            async with self._request_semaphore:
                values = await self.api.async_get_endpoint(
                    str(subentry.data[CONF_CAR_ID]), endpoint
                )
        except HyundaiKiaAuthenticationError:
            raise
        except HyundaiKiaError as err:
            return subentry.subentry_id, {}, requested_keys, err
        return subentry.subentry_id, values, requested_keys, None

    def car_type(self, subentry: ConfigSubentry) -> str:
        """Return a vehicle type from live profile data or stored fallback."""
        car_id = str(subentry.data[CONF_CAR_ID])
        if profile := self.vehicle_profiles.get(car_id):
            return profile.car_type
        return str(subentry.data.get(CONF_CAR_TYPE, "")).upper()

    def set_scan_interval(self, minutes: int) -> None:
        """Update the polling interval without reloading the integration."""
        self.update_interval = timedelta(minutes=minutes)


def subentry_snapshot(entry: HyundaiKiaConfigEntry) -> tuple[tuple[str, str, str], ...]:
    """Return vehicle fields that require a platform reload."""
    return tuple(
        sorted(
            (
                subentry.subentry_id,
                subentry.title,
                str(subentry.data.get(CONF_CAR_ID, "")),
            )
            for subentry in entry.subentries.values()
            if subentry.subentry_type == SUBENTRY_TYPE_VEHICLE
        )
    )
