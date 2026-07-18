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
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_PARALLEL_REQUESTS,
    SUBENTRY_TYPE_VEHICLE,
    Metric,
)
from .exceptions import (
    HyundaiKiaAuthenticationError,
    HyundaiKiaError,
)
from .models import HyundaiKiaConfigEntry, MetricResult, MetricValue

type CoordinatorData = dict[str, dict[Metric, MetricResult]]
type MetricContext = tuple[str, Metric]

_LOGGER = logging.getLogger(__name__)


class HyundaiKiaDataUpdateCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Coordinate metric updates for every vehicle on an account."""

    config_entry: HyundaiKiaConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: HyundaiKiaConfigEntry,
        api: HyundaiKiaApiClient,
    ) -> None:
        """Initialize the coordinator."""
        self.api = api
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
        """Fetch metrics requested by enabled entity contexts."""
        vehicles = {
            subentry_id: subentry
            for subentry_id, subentry in self.config_entry.subentries.items()
            if subentry.subentry_type == SUBENTRY_TYPE_VEHICLE
        }
        if not vehicles:
            return {}

        raw_contexts = set(self.async_contexts())
        contexts: set[MetricContext] = {
            context
            for context in raw_contexts
            if isinstance(context, tuple)
            and len(context) == 2
            and context[0] in vehicles
            and isinstance(context[1], Metric)
        }
        if not contexts:
            contexts = {
                (subentry_id, metric) for subentry_id in vehicles for metric in Metric
            }

        tasks = [
            self._async_fetch_metric(vehicles[subentry_id], metric)
            for subentry_id, metric in sorted(
                contexts, key=lambda item: (item[0], item[1].value)
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
        for subentry_id, metric, value, error in results:
            if error is None:
                successes += 1
                data[subentry_id][metric] = MetricResult(metric=metric, value=value)
            else:
                errors.append(error)
                data[subentry_id][metric] = MetricResult(
                    metric=metric,
                    value=None,
                    error=error.__class__.__name__,
                )

        if errors and not successes:
            first_error = errors[0]
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
            ) from first_error
        return data

    async def _async_fetch_metric(
        self, subentry: ConfigSubentry, metric: Metric
    ) -> tuple[str, Metric, MetricValue | None, Exception | None]:
        """Fetch one metric and retain enough context for partial failures."""
        try:
            async with self._request_semaphore:
                value = await self.api.async_get_metric(
                    str(subentry.data[CONF_CAR_ID]), metric
                )
        except HyundaiKiaAuthenticationError:
            raise
        except HyundaiKiaError as err:
            return subentry.subentry_id, metric, None, err
        return subentry.subentry_id, metric, value, None

    def set_scan_interval(self, minutes: int) -> None:
        """Update the polling interval without reloading the integration."""
        self.update_interval = timedelta(minutes=minutes)


def subentry_snapshot(entry: HyundaiKiaConfigEntry) -> tuple[tuple[str, str, str], ...]:
    """Return the vehicle subentry fields that require a platform reload."""
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
