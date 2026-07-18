"""Data models for Hyundai Kia Developers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

from .const import Metric

if TYPE_CHECKING:
    from .api import HyundaiKiaApiClient
    from .coordinator import HyundaiKiaDataUpdateCoordinator


@dataclass(frozen=True, slots=True)
class TokenResponse:
    """OAuth token response."""

    access_token: str
    refresh_token: str | None
    expires_in: int
    token_type: str = "Bearer"


@dataclass(frozen=True, slots=True)
class MetricValue:
    """One metric value returned by the vehicle API."""

    value: float
    timestamp: str | None = None


@dataclass(frozen=True, slots=True)
class MetricResult:
    """One coordinator metric result."""

    metric: Metric
    value: MetricValue | None
    error: str | None = None


@dataclass(slots=True)
class HyundaiKiaRuntimeData:
    """Runtime data attached to a config entry."""

    api: "HyundaiKiaApiClient"
    coordinator: "HyundaiKiaDataUpdateCoordinator"
    subentry_snapshot: tuple[tuple[str, str, str], ...]


type HyundaiKiaConfigEntry = ConfigEntry[HyundaiKiaRuntimeData]
