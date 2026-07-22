"""Tests for revised onboarding helpers and compatibility."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET

from custom_components.hyundai_kia_developers.config_flow import (
    HyundaiKiaConfigFlow,
    VehicleSubentryFlowHandler,
    _credentials_schema,
    _next_account_title,
    _prepare_credentials,
    _provider_error_details,
    _vehicle_label,
)
from custom_components.hyundai_kia_developers.const import (
    CONF_BRAND,
    CONF_REDIRECT_URI,
    CONF_REDIRECT_URL,
    Brand,
    EndpointKey,
)
from custom_components.hyundai_kia_developers.exceptions import (
    HyundaiKiaAuthenticationError,
    HyundaiKiaVehicleError,
)
from custom_components.hyundai_kia_developers.models import VehicleProfile

VALID_CLIENT_ID = "d15b2425-15f5-4a9b-a5a7-d312896b9aa6"
VALID_CLIENT_SECRET = "m1TvYmRA4LAhj7SQLnLPpaqc23AA09N3EWHay3o41aaEaX71"
VALID_REDIRECT_URI = "https://example.com/redirect"


def _credential_input(
    client_id: str = VALID_CLIENT_ID,
    client_secret: str = VALID_CLIENT_SECRET,
    redirect_uri: str = VALID_REDIRECT_URI,
) -> dict[str, str]:
    """Return synthetic developer credentials for config-flow tests."""
    return {
        CONF_BRAND: Brand.HYUNDAI,
        CONF_CLIENT_ID: client_id,
        CONF_CLIENT_SECRET: client_secret,
        CONF_REDIRECT_URI: redirect_uri,
    }


def test_credentials_are_trimmed_without_changing_internal_characters() -> None:
    """Only surrounding whitespace is removed from submitted values."""
    prepared, errors, format_warning = _prepare_credentials(
        _credential_input(
            f" \t{VALID_CLIENT_ID.upper()}\n",
            f" \n{VALID_CLIENT_SECRET}\t",
            f" \t{VALID_REDIRECT_URI}\n",
        )
    )

    assert errors == {}
    assert format_warning is False
    assert prepared[CONF_CLIENT_ID] == VALID_CLIENT_ID.upper()
    assert prepared[CONF_CLIENT_SECRET] == VALID_CLIENT_SECRET
    assert prepared[CONF_REDIRECT_URI] == VALID_REDIRECT_URI


def test_client_id_shape_does_not_enforce_a_uuid_version() -> None:
    """Any canonical hexadecimal UUID shape satisfies the advisory check."""
    prepared, errors, format_warning = _prepare_credentials(
        _credential_input("d15b2425-15f5-0a9b-f5a7-d312896b9aa6")
    )

    assert prepared[CONF_CLIENT_ID] == "d15b2425-15f5-0a9b-f5a7-d312896b9aa6"
    assert errors == {}
    assert format_warning is False


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        (CONF_CLIENT_ID, "  ", "required"),
        (CONF_CLIENT_ID, "CLIENTID", "invalid_client_id"),
        (CONF_CLIENT_ID, "{your_client_id}", "invalid_client_id"),
        (CONF_CLIENT_ID, '"YOUR_CLIENT_ID"', "invalid_client_id"),
        (CONF_CLIENT_SECRET, "\n", "required"),
        (CONF_CLIENT_SECRET, "ClientSecret", "invalid_client_secret"),
        (CONF_CLIENT_SECRET, "{YOUR_CLIENT_SECRET}", "invalid_client_secret"),
        (CONF_CLIENT_SECRET, "<YOUR_CLIENT_SECRET>", "invalid_client_secret"),
    ],
)
def test_blank_and_placeholder_credentials_are_rejected(
    field: str, value: str, error: str
) -> None:
    """Definite credential input mistakes produce field-level errors."""
    user_input = _credential_input()
    user_input[field] = value

    _prepared, errors, _format_warning = _prepare_credentials(user_input)

    assert errors[field] == error


@pytest.mark.parametrize(
    ("client_id", "client_secret"),
    [
        ("not-a-uuid", VALID_CLIENT_SECRET),
        (VALID_CLIENT_ID, "short"),
        (VALID_CLIENT_ID, "é" * 48),
        (VALID_CLIENT_ID, "A" * 47 + "-"),
    ],
)
def test_unusual_credential_formats_are_advisory(
    client_id: str, client_secret: str
) -> None:
    """Nonempty unusual formats warn without becoming validation errors."""
    _prepared, errors, format_warning = _prepare_credentials(
        _credential_input(client_id, client_secret)
    )

    assert errors == {}
    assert format_warning is True


async def test_matching_credentials_start_authorization_with_normalized_values() -> (
    None
):
    """Expected credential shapes skip the warning and retain normalized values."""
    flow = HyundaiKiaConfigFlow()
    flow._start_authorization = AsyncMock(return_value={"step_id": "authorize"})
    flow.async_step_credential_warning = AsyncMock(
        return_value={"step_id": "credential_warning"}
    )

    result = await flow.async_step_user(
        _credential_input(
            f" {VALID_CLIENT_ID} ",
            f"\t{VALID_CLIENT_SECRET}\n",
            f" {VALID_REDIRECT_URI} ",
        )
    )

    assert result == {"step_id": "authorize"}
    assert flow._pending[CONF_CLIENT_ID] == VALID_CLIENT_ID
    assert flow._pending[CONF_CLIENT_SECRET] == VALID_CLIENT_SECRET
    assert flow._pending[CONF_REDIRECT_URI] == VALID_REDIRECT_URI
    flow._start_authorization.assert_awaited_once_with()
    flow.async_step_credential_warning.assert_not_awaited()


async def test_placeholder_credentials_stop_before_warning_or_authorization() -> None:
    """Blocking input mistakes remain on the credential form."""
    flow = HyundaiKiaConfigFlow()
    flow.async_show_form = MagicMock(return_value={"step_id": "user"})
    flow._start_authorization = AsyncMock(return_value={"step_id": "authorize"})
    flow.async_step_credential_warning = AsyncMock(
        return_value={"step_id": "credential_warning"}
    )

    result = await flow.async_step_user(_credential_input(client_id=" YOUR_CLIENT_ID "))

    assert result == {"step_id": "user"}
    flow._start_authorization.assert_not_awaited()
    flow.async_step_credential_warning.assert_not_awaited()
    assert flow.async_show_form.call_args.kwargs["errors"] == {
        CONF_CLIENT_ID: "invalid_client_id"
    }


async def test_unusual_credentials_warn_then_continue_unchanged() -> None:
    """The advisory step preserves and then authorizes unusual credentials."""
    flow = HyundaiKiaConfigFlow()
    flow.async_step_credential_warning = AsyncMock(
        return_value={"step_id": "credential_warning"}
    )

    result = await flow.async_step_user(
        _credential_input("unusual Client ID", "unusual-secret")
    )

    assert result == {"step_id": "credential_warning"}
    assert flow._pending[CONF_CLIENT_ID] == "unusual Client ID"
    assert flow._pending[CONF_CLIENT_SECRET] == "unusual-secret"

    del flow.async_step_credential_warning
    flow._start_authorization = AsyncMock(return_value={"step_id": "authorize"})
    result = await flow.async_step_credential_warning({})

    assert result == {"step_id": "authorize"}
    flow._start_authorization.assert_awaited_once_with()


async def test_edited_credentials_are_checked_again_after_a_warning() -> None:
    """Returning to the input step reevaluates replacement credentials."""
    flow = HyundaiKiaConfigFlow()
    flow.async_step_credential_warning = AsyncMock(
        return_value={"step_id": "credential_warning"}
    )
    flow._start_authorization = AsyncMock(return_value={"step_id": "authorize"})

    await flow.async_step_user(_credential_input("unusual", "short"))
    result = await flow.async_step_user(_credential_input())

    assert result == {"step_id": "authorize"}
    assert flow._pending[CONF_CLIENT_ID] == VALID_CLIENT_ID
    assert flow._pending[CONF_CLIENT_SECRET] == VALID_CLIENT_SECRET
    flow.async_step_credential_warning.assert_awaited_once_with()
    flow._start_authorization.assert_awaited_once_with()


async def test_reconfigure_retains_an_omitted_secret_without_warning() -> None:
    """An omitted replacement secret is retained and not shape checked."""
    flow = HyundaiKiaConfigFlow()
    entry = SimpleNamespace(
        data={
            **_credential_input(),
            CONF_CLIENT_SECRET: "existing-secret-in-an-older-format",
        }
    )
    flow._get_reconfigure_entry = MagicMock(return_value=entry)
    flow._start_authorization = AsyncMock(return_value={"step_id": "authorize"})
    flow.async_step_credential_warning = AsyncMock(
        return_value={"step_id": "credential_warning"}
    )

    user_input = _credential_input(client_secret="   ")
    user_input.pop(CONF_BRAND)
    result = await flow.async_step_reconfigure(user_input)

    assert result == {"step_id": "authorize"}
    assert flow._pending[CONF_CLIENT_SECRET] == "existing-secret-in-an-older-format"
    flow.async_step_credential_warning.assert_not_awaited()


async def test_reconfigure_warns_for_an_unusual_replacement_secret() -> None:
    """A supplied replacement secret participates in advisory checking."""
    flow = HyundaiKiaConfigFlow()
    entry = SimpleNamespace(data=_credential_input())
    flow._get_reconfigure_entry = MagicMock(return_value=entry)
    flow.async_step_credential_warning = AsyncMock(
        return_value={"step_id": "credential_warning"}
    )

    user_input = _credential_input(client_secret="replacement-secret")
    user_input.pop(CONF_BRAND)
    result = await flow.async_step_reconfigure(user_input)

    assert result == {"step_id": "credential_warning"}
    assert flow._pending[CONF_CLIENT_SECRET] == "replacement-secret"


def test_vehicle_label_and_suggested_name() -> None:
    """Discovery suggests the nickname but still disambiguates the selector."""
    profile = VehicleProfile("sensitive-car-1234", "My Niro", "HEV", "DE", "Niro")
    assert profile.suggested_name == "My Niro"
    label = _vehicle_label(profile)
    assert label == "My Niro — Niro (••••1234)"
    assert "sensitive-car" not in label


def test_suggested_name_fallbacks() -> None:
    """Sales model and model code are deterministic naming fallbacks."""
    assert VehicleProfile("1", "", "EV", "CV", "EV6").suggested_name == "EV6"
    assert VehicleProfile("1", "", "EV", "CV", "").suggested_name == "CV"


@pytest.mark.parametrize(
    ("error_code", "error_key"),
    [
        ("4002", "vehicle_invalid_request"),
        ("5005", "vehicle_agreement_required"),
        ("5006", "vehicle_permission_required"),
        ("5032", "vehicle_service_unavailable"),
        ("9999", "vehicle_provider_undefined_error"),
    ],
)
def test_provider_errors_have_actionable_config_flow_messages(
    error_code: str, error_key: str
) -> None:
    """Known provider codes select specific guidance and safe endpoint context."""
    error = HyundaiKiaVehicleError(
        "request failed",
        error_code=error_code,
        operation=EndpointKey.DISTANCE_TO_EMPTY.value,
    )

    assert _provider_error_details(error) == (error_key, {"operation": "DTE"})


def test_account_titles_are_generated_per_brand() -> None:
    """Same-brand entries receive a numeric suffix regardless of custom titles."""
    hass = MagicMock()
    hass.config_entries.async_entries.return_value = [
        SimpleNamespace(data={CONF_BRAND: Brand.KIA}),
        SimpleNamespace(data={CONF_BRAND: Brand.HYUNDAI}),
    ]
    assert _next_account_title(hass, Brand.KIA) == "Kia 2"
    assert _next_account_title(hass, Brand.HYUNDAI) == "Hyundai 2"
    assert _next_account_title(hass, Brand.GENESIS) == "Genesis"


def test_reconfigure_schema_cannot_change_brand() -> None:
    """Reconfiguration exposes credentials but keeps the existing brand immutable."""
    schema = _credentials_schema(
        {
            CONF_BRAND: Brand.KIA,
            CONF_CLIENT_ID: "client",
            CONF_CLIENT_SECRET: "secret",
            CONF_REDIRECT_URI: "https://example.com/redirect",
        },
        include_brand=False,
        require_secret=False,
    )
    keys = {marker.schema for marker in schema.schema}
    assert CONF_BRAND not in keys
    assert keys == {CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_REDIRECT_URI}


def test_authorize_form_supplies_registered_redirect_placeholder() -> None:
    """Authorization guidance can safely reference the configured redirect URI."""
    flow = HyundaiKiaConfigFlow()
    flow._pending = {
        CONF_BRAND: Brand.HYUNDAI,
        CONF_REDIRECT_URI: VALID_REDIRECT_URI,
    }
    flow._oauth_state = "state"
    flow._api = MagicMock()
    flow._api.authorization_url.return_value = "https://authorize.example"
    flow.async_show_form = MagicMock(return_value={"step_id": "authorize"})

    result = flow._show_authorize_form({"base": "oauth_missing_code"})

    assert result == {"step_id": "authorize"}
    assert flow.async_show_form.call_args.kwargs["description_placeholders"] == {
        "authorization_url": "https://authorize.example",
        "brand": "Hyundai",
        "redirect_uri": VALID_REDIRECT_URI,
    }


def test_recovery_menu_steps_have_handlers() -> None:
    """Home Assistant can route both discovery recovery menus."""
    for handler in (HyundaiKiaConfigFlow, VehicleSubentryFlowHandler):
        assert hasattr(handler, "async_step_vehicle_discovery_failed")
        assert hasattr(handler, "async_step_no_vehicles")
        assert hasattr(handler, "async_step_retry")
        assert hasattr(handler, "async_step_manual")


async def test_authorize_reports_redirect_validation_reason() -> None:
    """The flow preserves a safe, actionable redirect-validation reason."""
    flow = HyundaiKiaConfigFlow()
    flow._pending = {CONF_REDIRECT_URI: "https://example.com/redirect"}
    flow._oauth_state = "expected"
    flow._api = MagicMock()
    flow._show_authorize_form = MagicMock(side_effect=lambda errors: errors)

    result = await flow.async_step_authorize(
        {
            CONF_REDIRECT_URL: (
                "https://wrong.example/redirect?code=secret&state=expected"
            )
        }
    )

    assert result == {"base": "oauth_redirect_mismatch"}
    flow._api.async_exchange_authorization_code.assert_not_called()


async def test_authorize_reports_token_exchange_failure() -> None:
    """A rejected code is distinguished from a malformed redirect."""
    flow = HyundaiKiaConfigFlow()
    flow._pending = {CONF_REDIRECT_URI: "https://example.com/redirect"}
    flow._oauth_state = "expected"
    flow._api = MagicMock()
    flow._api.async_exchange_authorization_code = AsyncMock(
        side_effect=HyundaiKiaAuthenticationError
    )
    flow._show_authorize_form = MagicMock(side_effect=lambda errors: errors)

    result = await flow.async_step_authorize(
        {CONF_REDIRECT_URL: ("https://example.com/redirect?code=secret&state=expected")}
    )

    assert result == {"base": "oauth_token_exchange_failed"}


async def test_authorize_reports_missing_refresh_token() -> None:
    """A successful but unusable token response has its own recovery advice."""
    flow = HyundaiKiaConfigFlow()
    flow._pending = {CONF_REDIRECT_URI: "https://example.com/redirect"}
    flow._oauth_state = "expected"
    flow._api = MagicMock()
    flow._api.async_exchange_authorization_code = AsyncMock(
        return_value=SimpleNamespace(refresh_token=None)
    )
    flow._show_authorize_form = MagicMock(side_effect=lambda errors: errors)

    result = await flow.async_step_authorize(
        {CONF_REDIRECT_URL: ("https://example.com/redirect?code=secret&state=expected")}
    )

    assert result == {"base": "oauth_missing_refresh_token"}
