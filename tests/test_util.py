"""Tests for OAuth URL and vehicle identity helpers."""

import pytest

from custom_components.hyundai_kia_developers.exceptions import (
    HyundaiKiaOAuthRedirectError,
)
from custom_components.hyundai_kia_developers.util import (
    parse_authorization_redirect,
    vehicle_key,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/redirect?code=secret-code&state=expected",
        (
            "https://example.com/redirect?scope&state=expected"
            "&code=secret-code&result=0000"
        ),
    ],
)
def test_parse_authorization_redirect(url: str) -> None:
    """A matching redirect returns only its one-time code."""
    assert (
        parse_authorization_redirect(
            url,
            "https://example.com/redirect",
            "expected",
        )
        == "secret-code"
    )


@pytest.mark.parametrize(
    ("url", "error_key"),
    [
        (
            "https://wrong.example/redirect?code=code&state=expected",
            "oauth_redirect_mismatch",
        ),
        (
            "https://example.com/redirect?code=code&state=wrong",
            "oauth_state_mismatch",
        ),
        (
            "https://example.com/redirect?state=expected",
            "oauth_missing_code",
        ),
        (
            "https://example.com/redirect?error=access_denied&state=expected",
            "oauth_provider_error",
        ),
        (
            "https://example.com/redirect?result=9001&message=invalid",
            "oauth_provider_error",
        ),
    ],
)
def test_parse_authorization_redirect_rejects_invalid_input(
    url: str, error_key: str
) -> None:
    """Invalid redirects expose an actionable key without retaining the URL."""
    with pytest.raises(HyundaiKiaOAuthRedirectError) as exc_info:
        parse_authorization_redirect(
            url,
            "https://example.com/redirect",
            "expected",
        )
    assert exc_info.value.error_key == error_key
    assert url not in str(exc_info.value)


def test_vehicle_key_is_stable_and_brand_scoped() -> None:
    """Vehicle registry identifiers are stable without exposing car IDs."""
    key = vehicle_key("kia", "sensitive-car-id")
    assert key == vehicle_key("kia", "sensitive-car-id")
    assert key != vehicle_key("hyundai", "sensitive-car-id")
    assert "sensitive-car-id" not in key
