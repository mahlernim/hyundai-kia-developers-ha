"""Tests for the Hyundai/Kia developer API client."""

from collections import defaultdict, deque
from typing import Any, cast

import pytest
from aiohttp import ClientSession

from custom_components.hyundai_kia_developers.api import HyundaiKiaApiClient
from custom_components.hyundai_kia_developers.const import (
    BRAND_ENDPOINTS,
    Brand,
    Metric,
)
from custom_components.hyundai_kia_developers.exceptions import (
    HyundaiKiaAuthenticationError,
)


class FakeResponse:
    """Minimal aiohttp response used by the API client."""

    def __init__(self, status: int, payload: dict[str, Any]) -> None:
        self.status = status
        self._payload = payload
        self.released = False

    async def json(self, *, content_type: str | None = None) -> dict[str, Any]:
        """Return the prepared JSON body."""
        return self._payload

    def release(self) -> None:
        """Mark this prepared response released."""
        self.released = True


class FakeSession:
    """Queue deterministic responses by method and URL."""

    def __init__(self) -> None:
        self._responses: dict[tuple[str, str], deque[FakeResponse]] = defaultdict(deque)
        self.requests: list[tuple[str, str, dict[str, Any]]] = []

    def add(
        self,
        method: str,
        url: str,
        *,
        status: int = 200,
        payload: dict[str, Any],
    ) -> None:
        """Queue a response."""
        self._responses[(method, url)].append(FakeResponse(status, payload))

    async def post(self, url: str, **kwargs: Any) -> FakeResponse:
        """Return the next POST response."""
        return self._request("POST", url, kwargs)

    async def get(self, url: str, **kwargs: Any) -> FakeResponse:
        """Return the next GET response."""
        return self._request("GET", url, kwargs)

    def _request(self, method: str, url: str, kwargs: dict[str, Any]) -> FakeResponse:
        """Record a request and pop its prepared response."""
        self.requests.append((method, url, kwargs))
        return self._responses[(method, url)].popleft()


@pytest.mark.asyncio
async def test_refresh_and_fetch_both_metrics() -> None:
    """A refresh token is rotated once and both supported metrics parse."""
    endpoints = BRAND_ENDPOINTS[Brand.KIA]
    session = FakeSession()
    session.add(
        "POST",
        endpoints.token_url,
        payload={
            "access_token": "access-1",
            "refresh_token": "refresh-2",
            "expires_in": 3600,
            "token_type": "Bearer",
        },
    )
    session.add(
        "GET",
        f"{endpoints.vehicle_base}/api/v1/car/status/car-1/dte",
        payload={"value": 526},
    )
    session.add(
        "GET",
        f"{endpoints.vehicle_base}/api/v1/car/status/car-1/odometer",
        payload={"odometers": [{"value": 38213}]},
    )
    rotations: list[str] = []
    api = HyundaiKiaApiClient(
        cast(ClientSession, session),
        Brand.KIA,
        "client-id",
        "client-secret",
        "https://example.com/redirect",
        "refresh-1",
        rotations.append,
    )

    values = await api.async_validate_vehicle("car-1")

    assert values[Metric.DISTANCE_TO_EMPTY].value == 526
    assert values[Metric.ODOMETER].value == 38213
    assert rotations == ["refresh-2"]
    assert [method for method, _url, _kwargs in session.requests].count("POST") == 1


@pytest.mark.asyncio
async def test_error_4002_requests_reauthentication() -> None:
    """Provider error 4002 is classified as an authentication failure."""
    session = FakeSession()
    session.add(
        "POST",
        BRAND_ENDPOINTS[Brand.HYUNDAI].token_url,
        status=400,
        payload={"resCode": "4002", "resMsg": "Invalid parameters"},
    )
    api = HyundaiKiaApiClient(
        cast(ClientSession, session),
        Brand.HYUNDAI,
        "client-id",
        "client-secret",
        "https://example.com/redirect",
        "expired-refresh-token",
    )

    with pytest.raises(HyundaiKiaAuthenticationError):
        await api.async_ensure_access_token()
