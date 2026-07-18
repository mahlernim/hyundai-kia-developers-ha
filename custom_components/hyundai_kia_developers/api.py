"""Asynchronous Korean Hyundai/Kia connected-car API client."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import urlencode

from aiohttp import ClientError, ClientResponse, ClientSession, encode_basic_auth

from .const import (
    BRAND_ENDPOINTS,
    REQUEST_TIMEOUT_SECONDS,
    TOKEN_REFRESH_MARGIN_SECONDS,
    Brand,
    Metric,
)
from .exceptions import (
    HyundaiKiaAuthenticationError,
    HyundaiKiaConnectionError,
    HyundaiKiaRateLimitError,
    HyundaiKiaVehicleError,
)
from .models import MetricValue, TokenResponse

RefreshTokenCallback = Callable[[str], None]


class HyundaiKiaApiClient:
    """Client for the matching Hyundai and Kia Korean developer APIs."""

    def __init__(
        self,
        session: ClientSession,
        brand: Brand,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        refresh_token: str | None = None,
        on_refresh_token: RefreshTokenCallback | None = None,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self.brand = brand
        self._client_id = client_id
        self._client_secret = client_secret
        self.redirect_uri = redirect_uri
        self._refresh_token = refresh_token
        self._on_refresh_token = on_refresh_token
        self._access_token: str | None = None
        self._access_token_expires_at = 0.0
        self._token_lock = asyncio.Lock()

    @property
    def refresh_token(self) -> str | None:
        """Return the current refresh token."""
        return self._refresh_token

    def authorization_url(self, state: str) -> str:
        """Build the interactive OAuth authorization URL."""
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self._client_id,
                "redirect_uri": self.redirect_uri,
                "state": state,
            }
        )
        return f"{BRAND_ENDPOINTS[self.brand].authorize_url}?{query}"

    async def async_exchange_authorization_code(self, code: str) -> TokenResponse:
        """Exchange a one-time authorization code and activate the token set."""
        token = await self._async_token_request(
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
        )
        self._activate_token(token)
        return token

    async def async_ensure_access_token(self, *, force: bool = False) -> str:
        """Return a usable access token, refreshing it when needed."""
        if not force and self._access_token_is_valid():
            return self._access_token  # type: ignore[return-value]

        async with self._token_lock:
            if not force and self._access_token_is_valid():
                return self._access_token  # type: ignore[return-value]
            if not self._refresh_token:
                raise HyundaiKiaAuthenticationError("No refresh token is available")

            token = await self._async_token_request(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                    "redirect_uri": self.redirect_uri,
                }
            )
            self._activate_token(token)
            return token.access_token

    async def async_get_metric(self, car_id: str, metric: Metric) -> MetricValue:
        """Fetch one metric, retrying once after an authorization rejection."""
        endpoint = "dte" if metric is Metric.DISTANCE_TO_EMPTY else "odometer"
        url = (
            f"{BRAND_ENDPOINTS[self.brand].vehicle_base}"
            f"/api/v1/car/status/{car_id}/{endpoint}"
        )

        for attempt in range(2):
            access_token = await self.async_ensure_access_token(force=attempt == 1)
            response = await self._async_get(
                url, headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status in (401, 403):
                response.release()
                self._access_token = None
                self._access_token_expires_at = 0.0
                if attempt == 0:
                    continue
                raise HyundaiKiaAuthenticationError(
                    "Vehicle API rejected refreshed credentials"
                )
            if response.status == 429:
                response.release()
                raise HyundaiKiaRateLimitError("Vehicle API rate limit reached")
            if response.status >= 400:
                status = response.status
                response.release()
                raise HyundaiKiaVehicleError(
                    f"Vehicle API rejected {metric.value} with HTTP {status}"
                )

            payload = await self._async_json(response)
            return self._parse_metric(metric, payload)

        raise HyundaiKiaAuthenticationError("Unable to authenticate vehicle request")

    async def async_validate_vehicle(self, car_id: str) -> dict[Metric, MetricValue]:
        """Validate a car ID by fetching every v1 metric."""
        values = await asyncio.gather(
            self.async_get_metric(car_id, Metric.DISTANCE_TO_EMPTY),
            self.async_get_metric(car_id, Metric.ODOMETER),
        )
        return dict(zip(Metric, values, strict=True))

    def _access_token_is_valid(self) -> bool:
        """Return whether the in-memory access token has adequate lifetime."""
        return bool(
            self._access_token
            and self._access_token_expires_at
            > time.time() + TOKEN_REFRESH_MARGIN_SECONDS
        )

    def _activate_token(self, token: TokenResponse) -> None:
        """Activate token data and persist a rotated refresh token."""
        self._access_token = token.access_token
        self._access_token_expires_at = time.time() + token.expires_in
        if token.refresh_token and token.refresh_token != self._refresh_token:
            self._refresh_token = token.refresh_token
            if self._on_refresh_token:
                self._on_refresh_token(token.refresh_token)

    async def _async_token_request(self, data: dict[str, str]) -> TokenResponse:
        """Make a provider-specific OAuth token request."""
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT_SECONDS):
                response = await self._session.post(
                    BRAND_ENDPOINTS[self.brand].token_url,
                    headers={
                        "Accept": "application/json",
                        "Authorization": encode_basic_auth(
                            self._client_id, self._client_secret
                        ),
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data=data,
                )
        except (TimeoutError, ClientError) as err:
            raise HyundaiKiaConnectionError("OAuth token request failed") from err

        payload = await self._async_json(response)
        if response.status >= 400:
            error_code = str(
                payload.get(
                    "errCode",
                    payload.get("resCode", payload.get("error", "unknown")),
                )
            )
            if response.status in (400, 401, 403) or error_code == "4002":
                raise HyundaiKiaAuthenticationError(
                    f"OAuth token request was rejected ({error_code})"
                )
            if response.status == 429:
                raise HyundaiKiaRateLimitError("OAuth token rate limit reached")
            raise HyundaiKiaConnectionError(
                f"OAuth token endpoint returned HTTP {response.status}"
            )

        try:
            return TokenResponse(
                access_token=str(payload["access_token"]),
                refresh_token=(
                    str(payload["refresh_token"])
                    if payload.get("refresh_token")
                    else None
                ),
                expires_in=int(payload["expires_in"]),
                token_type=str(payload.get("token_type", "Bearer")),
            )
        except (KeyError, TypeError, ValueError) as err:
            raise HyundaiKiaConnectionError(
                "OAuth token response was incomplete"
            ) from err

    async def _async_get(self, url: str, *, headers: dict[str, str]) -> ClientResponse:
        """Make a bounded GET request."""
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT_SECONDS):
                return await self._session.get(
                    url, headers={"Accept": "application/json", **headers}
                )
        except (TimeoutError, ClientError) as err:
            raise HyundaiKiaConnectionError("Vehicle API request failed") from err

    @staticmethod
    async def _async_json(response: ClientResponse) -> dict[str, Any]:
        """Decode a JSON response without trusting its content type."""
        try:
            payload = await response.json(content_type=None)
        except (ClientError, json.JSONDecodeError, ValueError) as err:
            raise HyundaiKiaConnectionError("API returned invalid JSON") from err
        if not isinstance(payload, dict):
            raise HyundaiKiaConnectionError("API returned an unexpected JSON value")
        return payload

    @staticmethod
    def _parse_metric(metric: Metric, payload: dict[str, Any]) -> MetricValue:
        """Parse one metric response."""
        try:
            if metric is Metric.DISTANCE_TO_EMPTY:
                return MetricValue(
                    value=float(payload["value"]),
                    timestamp=(
                        str(payload["timestamp"]) if payload.get("timestamp") else None
                    ),
                )

            odometers = payload["odometers"]
            if not isinstance(odometers, list) or not odometers:
                raise ValueError("No odometer values")
            odometer = odometers[0]
            return MetricValue(
                value=float(odometer["value"]),
                timestamp=(
                    str(odometer["timestamp"]) if odometer.get("timestamp") else None
                ),
            )
        except (KeyError, TypeError, ValueError, IndexError) as err:
            raise HyundaiKiaVehicleError(
                f"Vehicle API returned invalid {metric.value} data"
            ) from err
