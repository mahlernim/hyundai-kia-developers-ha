"""Config flows for Hyundai Kia Developers."""

from __future__ import annotations

import secrets
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

import voluptuous as vol
from homeassistant.config_entries import (
    SOURCE_USER,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    FlowType,
    OptionsFlow,
    SubentryFlowContext,
    SubentryFlowResult,
)
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import HyundaiKiaApiClient
from .const import (
    CONF_ACCOUNT_ID,
    CONF_ACCOUNT_NAME,
    CONF_BRAND,
    CONF_CAR_ID,
    CONF_CAR_NAME,
    CONF_REDIRECT_URI,
    CONF_REDIRECT_URL,
    CONF_REFRESH_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_REDIRECT_URI,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    SUBENTRY_TYPE_VEHICLE,
    Brand,
)
from .exceptions import (
    HyundaiKiaAuthenticationError,
    HyundaiKiaConnectionError,
    HyundaiKiaError,
)
from .models import HyundaiKiaConfigEntry, TokenResponse
from .util import parse_authorization_redirect, vehicle_key


def _account_schema(
    values: Mapping[str, Any] | None = None,
    *,
    require_secret: bool = True,
) -> vol.Schema:
    """Return the account configuration schema."""
    values = values or {}
    secret_key: vol.Marker = (
        vol.Required(CONF_CLIENT_SECRET)
        if require_secret
        else vol.Optional(CONF_CLIENT_SECRET)
    )
    return vol.Schema(
        {
            vol.Required(
                CONF_BRAND, default=values.get(CONF_BRAND, Brand.HYUNDAI)
            ): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        SelectOptionDict(value=brand.value, label=brand.value.title())
                        for brand in Brand
                    ],
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_ACCOUNT_NAME, default=values.get(CONF_ACCOUNT_NAME, "")
            ): TextSelector(),
            vol.Required(
                CONF_CLIENT_ID, default=values.get(CONF_CLIENT_ID, "")
            ): TextSelector(),
            secret_key: TextSelector(
                TextSelectorConfig(type=TextSelectorType.PASSWORD)
            ),
            vol.Required(
                CONF_REDIRECT_URI,
                default=values.get(CONF_REDIRECT_URI, DEFAULT_REDIRECT_URI),
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.URL)),
        }
    )


def _vehicle_schema(values: Mapping[str, Any] | None = None) -> vol.Schema:
    """Return the vehicle schema."""
    values = values or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_CAR_NAME, default=values.get(CONF_CAR_NAME, "")
            ): TextSelector(),
            vol.Required(CONF_CAR_ID, default=values.get(CONF_CAR_ID, "")): str,
        }
    )


class HyundaiKiaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle account configuration."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize flow state."""
        self._pending: dict[str, Any] = {}
        self._oauth_state = ""
        self._flow_mode = "user"
        self._target_entry: HyundaiKiaConfigEntry | None = None

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return supported vehicle subentry flows."""
        return {SUBENTRY_TYPE_VEHICLE: VehicleSubentryFlowHandler}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return HyundaiKiaOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect account and developer application details."""
        errors: dict[str, str] = {}
        if user_input is not None:
            redirect = urlparse(str(user_input[CONF_REDIRECT_URI]))
            if redirect.scheme != "https" or not redirect.netloc:
                errors[CONF_REDIRECT_URI] = "invalid_redirect_uri"
            else:
                self._flow_mode = "user"
                self._pending = dict(user_input)
                return await self._start_authorization()

        return self.async_show_form(
            step_id="user",
            data_schema=_account_schema(user_input),
            errors=errors,
        )

    async def async_step_authorize(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Accept and validate the pasted OAuth redirect URL."""
        errors: dict[str, str] = {}
        api = self._build_api(self._pending)
        if user_input is not None:
            try:
                code = parse_authorization_redirect(
                    str(user_input[CONF_REDIRECT_URL]),
                    str(self._pending[CONF_REDIRECT_URI]),
                    self._oauth_state,
                )
                token = await api.async_exchange_authorization_code(code)
                if not token.refresh_token:
                    raise HyundaiKiaAuthenticationError(
                        "Authorization response had no refresh token"
                    )
                return await self._finish_authorization(api, token)
            except HyundaiKiaAuthenticationError:
                errors["base"] = "invalid_auth"
            except HyundaiKiaConnectionError:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="authorize",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_REDIRECT_URL): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.URL)
                    )
                }
            ),
            errors=errors,
            description_placeholders={
                "authorization_url": api.authorization_url(self._oauth_state),
                "brand": Brand(str(self._pending[CONF_BRAND])).value.title(),
            },
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Begin account reauthentication."""
        self._target_entry = self._get_reauth_entry()
        self._flow_mode = "reauth"
        self._pending = {
            **dict(entry_data),
            CONF_ACCOUNT_NAME: self._target_entry.title,
        }
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauthentication before redirecting the user."""
        if user_input is not None:
            return await self._start_authorization()
        return self.async_show_form(
            step_id="reauth_confirm", data_schema=vol.Schema({})
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update developer application credentials and reauthorize."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        current = {
            **dict(entry.data),
            CONF_ACCOUNT_NAME: entry.title,
        }
        if user_input is not None:
            redirect = urlparse(str(user_input[CONF_REDIRECT_URI]))
            if redirect.scheme != "https" or not redirect.netloc:
                errors[CONF_REDIRECT_URI] = "invalid_redirect_uri"
            else:
                self._target_entry = entry
                self._flow_mode = "reconfigure"
                self._pending = {
                    **dict(user_input),
                    CONF_CLIENT_SECRET: (
                        str(user_input.get(CONF_CLIENT_SECRET, ""))
                        or str(entry.data[CONF_CLIENT_SECRET])
                    ),
                    CONF_ACCOUNT_ID: entry.data[CONF_ACCOUNT_ID],
                }
                return await self._start_authorization()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_account_schema(current, require_secret=False),
            errors=errors,
        )

    async def async_on_create_entry(self, result: ConfigFlowResult) -> ConfigFlowResult:
        """Start the initial vehicle subentry flow after account creation."""
        subentry_result = await self.hass.config_entries.subentries.async_init(
            (result["result"].entry_id, SUBENTRY_TYPE_VEHICLE),
            context=SubentryFlowContext(source=SOURCE_USER),
        )
        result["next_flow"] = (
            FlowType.CONFIG_SUBENTRIES_FLOW,
            subentry_result["flow_id"],
        )
        return result

    async def _start_authorization(self) -> ConfigFlowResult:
        """Create a fresh OAuth state and show the authorization step."""
        self._oauth_state = secrets.token_urlsafe(32)
        return await self.async_step_authorize()

    async def _finish_authorization(
        self, api: HyundaiKiaApiClient, token: TokenResponse
    ) -> ConfigFlowResult:
        """Create or update an account after successful authorization."""
        assert token.refresh_token
        updates = {
            CONF_BRAND: str(self._pending[CONF_BRAND]),
            CONF_CLIENT_ID: str(self._pending[CONF_CLIENT_ID]),
            CONF_CLIENT_SECRET: str(self._pending[CONF_CLIENT_SECRET]),
            CONF_REDIRECT_URI: str(self._pending[CONF_REDIRECT_URI]),
            CONF_REFRESH_TOKEN: token.refresh_token,
        }

        if self._flow_mode in ("reauth", "reconfigure"):
            assert self._target_entry
            if self._target_entry.subentries:
                first_vehicle = next(iter(self._target_entry.subentries.values()))
                try:
                    await api.async_validate_vehicle(
                        str(first_vehicle.data[CONF_CAR_ID])
                    )
                except HyundaiKiaAuthenticationError:
                    return self.async_abort(reason="wrong_account")
                except HyundaiKiaConnectionError:
                    return self.async_abort(reason="cannot_connect")
                except HyundaiKiaError:
                    return self.async_abort(reason="wrong_account")
            return self.async_update_reload_and_abort(
                self._target_entry,
                title=str(self._pending[CONF_ACCOUNT_NAME]),
                data_updates=updates,
            )

        account_id = uuid4().hex
        updates[CONF_ACCOUNT_ID] = account_id
        await self.async_set_unique_id(f"{updates[CONF_BRAND]}:{account_id}")
        return self.async_create_entry(
            title=str(self._pending[CONF_ACCOUNT_NAME]),
            data=updates,
            options={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
        )

    def _build_api(self, data: Mapping[str, Any]) -> HyundaiKiaApiClient:
        """Build an API client for config-flow validation."""
        return HyundaiKiaApiClient(
            async_get_clientsession(self.hass),
            Brand(str(data[CONF_BRAND])),
            str(data[CONF_CLIENT_ID]),
            str(data[CONF_CLIENT_SECRET]),
            str(data[CONF_REDIRECT_URI]),
            str(data.get(CONF_REFRESH_TOKEN, "")) or None,
        )


class VehicleSubentryFlowHandler(ConfigSubentryFlow):
    """Add and reconfigure vehicles under an authenticated account."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add a vehicle."""
        errors: dict[str, str] = {}
        if user_input is not None:
            entry = self._get_entry()
            car_id = str(user_input[CONF_CAR_ID]).strip()
            key = vehicle_key(str(entry.data[CONF_BRAND]), car_id)
            if self._vehicle_configured(key):
                return self.async_abort(reason="already_configured")
            try:
                await self._validate_vehicle(entry, car_id)
            except HyundaiKiaAuthenticationError:
                errors["base"] = "invalid_auth"
            except HyundaiKiaConnectionError:
                errors["base"] = "cannot_connect"
            except HyundaiKiaError:
                errors["base"] = "invalid_vehicle"
            else:
                return self.async_create_entry(
                    title=str(user_input[CONF_CAR_NAME]),
                    data={CONF_CAR_ID: car_id},
                    unique_id=key,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_vehicle_schema(user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Rename a vehicle or replace its car ID."""
        entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()
        errors: dict[str, str] = {}
        current = {
            CONF_CAR_NAME: subentry.title,
            CONF_CAR_ID: subentry.data[CONF_CAR_ID],
        }
        if user_input is not None:
            car_id = str(user_input[CONF_CAR_ID]).strip()
            key = vehicle_key(str(entry.data[CONF_BRAND]), car_id)
            if key != subentry.unique_id and self._vehicle_configured(key):
                return self.async_abort(reason="already_configured")
            try:
                await self._validate_vehicle(entry, car_id)
            except HyundaiKiaAuthenticationError:
                errors["base"] = "invalid_auth"
            except HyundaiKiaConnectionError:
                errors["base"] = "cannot_connect"
            except HyundaiKiaError:
                errors["base"] = "invalid_vehicle"
            else:
                return self.async_update_and_abort(
                    entry,
                    subentry,
                    title=str(user_input[CONF_CAR_NAME]),
                    data={CONF_CAR_ID: car_id},
                    unique_id=key,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_vehicle_schema(user_input or current),
            errors=errors,
        )

    def _vehicle_configured(self, key: str) -> bool:
        """Return whether this hashed car ID exists in any account."""
        return any(
            subentry.unique_id == key
            for entry in self.hass.config_entries.async_entries(DOMAIN)
            for subentry in entry.subentries.values()
        )

    async def _validate_vehicle(
        self, entry: HyundaiKiaConfigEntry, car_id: str
    ) -> None:
        """Validate a car and persist token rotation during validation."""

        def persist_refresh_token(refresh_token: str) -> None:
            if refresh_token != entry.data[CONF_REFRESH_TOKEN]:
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={**entry.data, CONF_REFRESH_TOKEN: refresh_token},
                )

        api = HyundaiKiaApiClient(
            async_get_clientsession(self.hass),
            Brand(str(entry.data[CONF_BRAND])),
            str(entry.data[CONF_CLIENT_ID]),
            str(entry.data[CONF_CLIENT_SECRET]),
            str(entry.data[CONF_REDIRECT_URI]),
            str(entry.data[CONF_REFRESH_TOKEN]),
            persist_refresh_token,
        )
        await api.async_validate_vehicle(car_id)


class HyundaiKiaOptionsFlow(OptionsFlow):
    """Manage account polling options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure account options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    )
                }
            ),
        )
