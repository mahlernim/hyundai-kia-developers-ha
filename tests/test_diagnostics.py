"""Tests for redacted integration diagnostics."""

from custom_components.hyundai_kia_developers.const import EntityKey
from custom_components.hyundai_kia_developers.diagnostics import (
    metric_diagnostics,
    safe_provider_error_code,
)
from custom_components.hyundai_kia_developers.models import EntityResult, EntityValue


def test_metric_diagnostics_includes_safe_provider_error_context() -> None:
    """Provider codes and endpoint context remain available for support."""
    result = EntityResult(
        key=EntityKey.CHARGING,
        value=None,
        error="HyundaiKiaVehicleError",
        error_code="4045",
        error_operation="ev_charging",
        error_status=200,
    )

    assert metric_diagnostics(result) == {
        "available": False,
        "value": None,
        "timestamp": None,
        "error": "HyundaiKiaVehicleError",
        "provider_error_code": "4045",
        "operation": "ev_charging",
        "http_status": 200,
    }


def test_metric_diagnostics_keeps_successful_metric_shape() -> None:
    """Successful metrics retain their value and timestamp."""
    result = EntityResult(
        key=EntityKey.EV_BATTERY_LEVEL,
        value=EntityValue(80.0, "20260830170050"),
    )

    details = metric_diagnostics(result)

    assert details["available"] is True
    assert details["value"] == 80.0
    assert details["timestamp"] == "20260830170050"
    assert details["error"] is None
    assert details["provider_error_code"] is None
    assert details["operation"] is None
    assert details["http_status"] is None


def test_provider_error_code_rejects_arbitrary_response_text() -> None:
    """Diagnostics never expose an arbitrary value from a provider response."""
    assert safe_provider_error_code("5006") == "5006"
    assert safe_provider_error_code("invalid_request") == "invalid_request"
    assert safe_provider_error_code("private data with spaces") is None
    assert safe_provider_error_code("x" * 33) is None
