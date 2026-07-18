"""Constants for Hyundai Kia Developers."""

from dataclasses import dataclass
from enum import StrEnum

from homeassistant.const import Platform

DOMAIN = "hyundai_kia_developers"
PLATFORMS = [Platform.SENSOR]

CONF_ACCOUNT_ID = "account_id"
CONF_ACCOUNT_NAME = "account_name"
CONF_BRAND = "brand"
CONF_CAR_ID = "car_id"
CONF_CAR_NAME = "car_name"
CONF_REDIRECT_URI = "redirect_uri"
CONF_REDIRECT_URL = "redirect_url"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_SCAN_INTERVAL = "scan_interval"

SUBENTRY_TYPE_VEHICLE = "vehicle"

DEFAULT_REDIRECT_URI = "https://example.com/redirect"
DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 30
MAX_SCAN_INTERVAL = 1440

TOKEN_REFRESH_MARGIN_SECONDS = 300
REQUEST_TIMEOUT_SECONDS = 30
MAX_PARALLEL_REQUESTS = 2


class Brand(StrEnum):
    """Supported vehicle brands."""

    HYUNDAI = "hyundai"
    KIA = "kia"


class Metric(StrEnum):
    """Supported vehicle metrics."""

    DISTANCE_TO_EMPTY = "distance_to_empty"
    ODOMETER = "odometer"


@dataclass(frozen=True, slots=True)
class BrandEndpoints:
    """API endpoints for a vehicle brand."""

    auth_base: str
    vehicle_base: str

    @property
    def authorize_url(self) -> str:
        """Return the authorization URL."""
        return f"{self.auth_base}/api/v1/user/oauth2/authorize"

    @property
    def token_url(self) -> str:
        """Return the token URL."""
        return f"{self.auth_base}/api/v1/user/oauth2/token"


BRAND_ENDPOINTS: dict[Brand, BrandEndpoints] = {
    Brand.HYUNDAI: BrandEndpoints(
        auth_base="https://prd.kr-ccapi.hyundai.com",
        vehicle_base="https://dev.kr-ccapi.hyundai.com",
    ),
    Brand.KIA: BrandEndpoints(
        auth_base="https://prd.kr-ccapi.kia.com",
        vehicle_base="https://dev.kr-ccapi.kia.com",
    ),
}
