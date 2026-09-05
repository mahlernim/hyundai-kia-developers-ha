"""Regression tests for exceptional setup paths and unchanged successful setup."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.hyundai_kia_developers import config_flow as flow_module
from custom_components.hyundai_kia_developers.config_flow import (
    HyundaiKiaConfigFlow,
    VehicleSubentryFlowHandler,
)
from custom_components.hyundai_kia_developers.const import (
    CONF_BRAND,
    CONF_CAR_ID,
    CONF_CAR_NAME,
    CONF_REDIRECT_URL,
    CONF_REFRESH_TOKEN,
    CONF_VEHICLE,
    SUBENTRY_TYPE_VEHICLE,
)
from custom_components.hyundai_kia_developers.exceptions import (
    HyundaiKiaConnectionError,
    HyundaiKiaRateLimitError,
    HyundaiKiaVehicleError,
)
from custom_components.hyundai_kia_developers.models import (
    TokenResponse,
    VehicleProfile,
)

from .test_config_flow import _credential_input


def make_flow(*, subentry=False):
    """Use real flow steps with only HA persistence and the provider mocked."""
    flow = VehicleSubentryFlowHandler() if subentry else HyundaiKiaConfigFlow()
    flow.hass = MagicMock()
    flow.hass.config_entries.async_entries.return_value = []
    flow.async_show_form = MagicMock(side_effect=lambda **kwargs: kwargs)
    flow.async_create_entry = MagicMock(side_effect=lambda **kwargs: kwargs)
    flow.async_abort = MagicMock(side_effect=lambda **kwargs: kwargs)
    flow._api = MagicMock()
    flow._api.refresh_token = "fresh-refresh"
    flow._api.async_get_vehicles = AsyncMock(return_value=[profile("car-1")])
    flow._api.async_validate_vehicle = AsyncMock(return_value=True)
    flow._api.async_exchange_authorization_code = AsyncMock(
        return_value=TokenResponse("access", "fresh-refresh", 3600)
    )
    if subentry:
        flow._get_entry = MagicMock(
            return_value=SimpleNamespace(
                data=_credential_input(), async_start_reauth_if_available=MagicMock()
            )
        )
    else:
        flow._pending = _credential_input()
        flow._oauth_state = "expected"
        flow._token = TokenResponse("access", "fresh-refresh", 3600)
        flow.async_set_unique_id = AsyncMock()
    return flow


def profile(car_id):
    return VehicleProfile(car_id, "Family car", "EV", "CV", "EV6")


@pytest.mark.parametrize("subentry", [False, True])
async def test_success_keeps_steps_and_request_count(subentry):
    """Success needs one list and one validation, with no recovery screen."""
    flow = make_flow(subentry=subentry)
    if subentry:
        result = await flow.async_step_user()
    else:
        result = await flow.async_step_authorize(
            {CONF_REDIRECT_URL: "https://example.com/redirect?code=code&state=expected"}
        )
        flow._api.async_exchange_authorization_code.assert_awaited_once_with("code")
    assert result["step_id"] == "vehicle"
    result = await flow.async_step_vehicle({CONF_VEHICLE: "car-1"})
    assert result["step_id"] == "vehicle_name"
    result = await flow.async_step_vehicle_name({CONF_CAR_NAME: "My name"})
    assert result["title"] == ("My name" if subentry else "Hyundai")
    flow._api.async_get_vehicles.assert_awaited_once()
    flow._api.async_validate_vehicle.assert_awaited_once_with("car-1")
    assert "recovery" not in [
        call.kwargs["step_id"] for call in flow.async_show_form.call_args_list
    ]


async def test_provider_help_does_not_request_tokens_or_vehicles():
    flow = make_flow()
    result = await flow.async_step_authorize({"authorization_help": True})
    assert result["errors"] == {"base": "provider_authorization_help"}
    assert (
        "stage=provider_authorization"
        in result["description_placeholders"]["diagnostic"]
    )
    assert flow._recovery_retry is None
    assert not flow._recovery_manual
    flow._api.async_get_vehicles.assert_not_awaited()
    flow._api.async_exchange_authorization_code.assert_not_awaited()


@pytest.mark.parametrize("subentry", [False, True])
@pytest.mark.parametrize("step", ["vehicle", "vehicle_name", "manual"])
async def test_rate_limit_blocks_repeated_requests_then_retries_saved_input(
    monkeypatch, subentry, step
):
    flow = make_flow(subentry=subentry)
    flow._selected_vehicle = profile("car-1")
    now = [100.0]
    monkeypatch.setattr(flow_module.time, "monotonic", lambda: now[0])
    method = (
        flow._api.async_get_vehicles
        if step == "vehicle"
        else flow._api.async_validate_vehicle
    )
    success = [profile("car-1")] if step == "vehicle" else True
    method.side_effect = [HyundaiKiaRateLimitError(status=429, retry_after=30), success]
    values = (
        None
        if step == "vehicle"
        else {CONF_CAR_NAME: "Keep this name", CONF_CAR_ID: "car-1"}
    )
    result = await getattr(flow, f"async_step_{step}")(values)
    assert result["step_id"] == "recovery"
    assert result["errors"]["base"] == "rate_limited"
    result = await flow.async_step_recovery({"recovery_action": "retry"})
    assert result["description_placeholders"]["seconds"] == "30"
    method.assert_awaited_once()
    now[0] += 31
    result = await flow.async_step_recovery({"recovery_action": "retry"})
    assert method.await_count == 2
    if step != "vehicle":
        name = result["title"] if subentry else result["subentries"][0]["title"]
        assert name == "Keep this name"


@pytest.mark.parametrize(
    "failure",
    [
        HyundaiKiaRateLimitError(status=429, retry_after=10),
        HyundaiKiaConnectionError("private response"),
    ],
)
async def test_failed_code_exchange_requires_fresh_authorization(failure):
    flow = make_flow()
    old_api = flow._api
    old_api.async_exchange_authorization_code.side_effect = failure
    result = await flow.async_step_authorize(
        {CONF_REDIRECT_URL: "https://example.com/redirect?code=code&state=expected"}
    )
    assert result["step_id"] == "recovery"
    assert flow._oauth_state != "expected"
    assert flow._recovery_retry is None
    assert flow._token is None
    flow._retry_at = 0
    new_api = MagicMock()
    flow._build_api = MagicMock(return_value=new_api)
    await flow.async_step_recovery({"recovery_action": "restart"})
    assert flow._api is new_api
    old_api.async_exchange_authorization_code.assert_awaited_once()


@pytest.mark.parametrize("subentry", [False, True])
@pytest.mark.parametrize(
    "code,manual", [("4045", True), ("4046", False), ("5005", False), ("5006", False)]
)
async def test_discovery_error_preserves_code_and_limits_manual_recovery(
    subentry, code, manual
):
    flow = make_flow(subentry=subentry)
    flow._api.async_get_vehicles.side_effect = HyundaiKiaVehicleError(
        "private account and token",
        error_code=code,
        status=403,
        operation="Vehicle list",
    )
    result = await flow.async_step_vehicle()
    report = result["description_placeholders"]["diagnostic"]
    assert f"provider_code={code}" in report
    assert "http_status=403" in report
    assert "private" not in report
    assert flow._recovery_manual is manual


async def test_unknown_provider_fields_cannot_enter_setup_report():
    flow = make_flow()
    flow._api.async_get_vehicles.side_effect = HyundaiKiaVehicleError(
        "private-message",
        error_code="secret-token",
        status="private-status",
        operation="private-url",
    )
    result = await flow.async_step_vehicle()
    placeholders = str(result["description_placeholders"])
    assert "private" not in placeholders
    assert "secret-token" not in placeholders
    assert "provider_code=unknown" in placeholders


def existing_flow():
    flow = make_flow()
    flow._flow_mode = "reauth"
    flow._target_entry = SimpleNamespace(
        data={CONF_REFRESH_TOKEN: "original-refresh", CONF_BRAND: "hyundai"},
        subentries={
            car: SimpleNamespace(
                subentry_type=SUBENTRY_TYPE_VEHICLE, data={CONF_CAR_ID: car}
            )
            for car in ["car-1", "car-2"]
        },
    )
    flow.async_update_reload_and_abort = MagicMock(
        return_value={"reason": "reauth_successful"}
    )
    return flow


@pytest.mark.parametrize(
    "response",
    [
        [],
        HyundaiKiaVehicleError(error_code="4045"),
        HyundaiKiaRateLimitError(status=429),
    ],
)
async def test_inconclusive_reauthentication_keeps_saved_account(response):
    flow = existing_flow()
    if isinstance(response, Exception):
        flow._api.async_get_vehicles.side_effect = response
    else:
        flow._api.async_get_vehicles.return_value = response
    result = await flow._finish_existing_authorization()
    assert result["step_id"] == "recovery"
    assert result["errors"]["base"] != "account_mismatch"
    flow.async_update_reload_and_abort.assert_not_called()
    assert flow._target_entry.data[CONF_REFRESH_TOKEN] == "original-refresh"
    assert len(flow._target_entry.subentries) == 2


async def test_reauthentication_retry_reuses_token_and_updates_only_after_full_match():
    flow = existing_flow()
    flow._api.async_get_vehicles.side_effect = [
        [],
        [profile("car-1"), profile("car-2")],
    ]
    api = flow._api
    await flow._finish_existing_authorization()
    result = await flow.async_step_recovery({"recovery_action": "retry"})
    assert result == {"reason": "reauth_successful"}
    assert flow._api is api
    updates = flow.async_update_reload_and_abort.call_args.kwargs["data_updates"]
    assert updates[CONF_REFRESH_TOKEN] == "fresh-refresh"
    assert api.async_get_vehicles.await_count == 2
    api.async_exchange_authorization_code.assert_not_awaited()


@pytest.mark.parametrize("accept", [False, True])
async def test_partial_access_requires_choice_and_preserves_vehicle_entries(accept):
    flow = existing_flow()
    result = await flow._finish_existing_authorization()
    assert result["step_id"] == "partial_authorization"
    assert result["description_placeholders"]["count"] == "1"
    flow.async_update_reload_and_abort.assert_not_called()
    flow._start_authorization = AsyncMock(return_value={"step_id": "authorize"})
    await flow.async_step_partial_authorization({"keep_partial_authorization": accept})
    assert flow.async_update_reload_and_abort.called is accept
    assert flow._start_authorization.called is not accept
    assert len(flow._target_entry.subentries) == 2
    flow._api.async_get_vehicles.assert_awaited_once()


@pytest.mark.parametrize("subentry", [False, True])
async def test_manual_id_needs_data_while_discovered_vehicle_can_wait(subentry):
    flow = make_flow(subentry=subentry)
    flow._api.async_validate_vehicle.return_value = False
    result = await flow.async_step_manual(
        {CONF_CAR_ID: "unknown-car", CONF_CAR_NAME: "Manual"}
    )
    assert result["errors"]["base"] == "manual_unconfirmed"
    flow.async_create_entry.assert_not_called()
    flow._selected_vehicle = profile("car-1")
    await flow.async_step_vehicle_name({CONF_CAR_NAME: "Discovered"})
    flow.async_create_entry.assert_called_once()


@pytest.mark.parametrize("subentry", [False, True])
async def test_recovery_renders_real_home_assistant_form(subentry):
    """The recovery schema and inherited handler work with HA form rendering."""
    flow = make_flow(subentry=subentry)
    del flow.async_show_form
    flow._api.async_get_vehicles.return_value = []
    result = await flow.async_step_vehicle()
    assert result["step_id"] == "recovery"
    assert result["data_schema"]({"recovery_action": "manual"}) == {
        "recovery_action": "manual"
    }
    assert result["errors"] == {"base": "no_vehicles_returned"}
