"""Tests for combined warning coordination."""

from custom_components.hyundai_kia_developers.const import (
    DEFAULT_ENTITY_KEYS,
    ENTITY_ENDPOINT,
    WARNING_ENTITY_KEYS,
    EntityKey,
)
from custom_components.hyundai_kia_developers.coordinator import (
    endpoint_jobs,
    vehicle_warning_result,
    warning_summary,
)
from custom_components.hyundai_kia_developers.models import EntityResult, EntityValue


def warning_results(value: bool = False) -> dict[EntityKey, EntityResult]:
    """Return a complete set of synthetic warning results."""
    return {
        key: EntityResult(key=key, value=EntityValue(value))
        for key in WARNING_ENTITY_KEYS
    }


def test_default_context_includes_combined_warning() -> None:
    """The initial refresh includes the enabled combined warning entity."""
    assert EntityKey.VEHICLE_WARNING in DEFAULT_ENTITY_KEYS


def test_default_context_includes_connected_service_contract() -> None:
    """The initial refresh includes the enabled contract sensor."""
    key = EntityKey.CONNECTED_SERVICE_FREE_DAYS_REMAINING

    assert key in DEFAULT_ENTITY_KEYS
    assert endpoint_jobs({("vehicle-1", key)}) == {
        ("vehicle-1", ENTITY_ENDPOINT[key]): {key}
    }


def test_contract_jobs_are_distinct_for_each_vehicle() -> None:
    """Each enabled vehicle receives one contract request per refresh."""
    key = EntityKey.CONNECTED_SERVICE_FREE_DAYS_REMAINING

    jobs = endpoint_jobs({("vehicle-1", key), ("vehicle-2", key)})

    assert set(jobs) == {
        ("vehicle-1", ENTITY_ENDPOINT[key]),
        ("vehicle-2", ENTITY_ENDPOINT[key]),
    }


def test_combined_warning_expands_to_all_warning_endpoints() -> None:
    """One combined context schedules every warning endpoint."""
    jobs = endpoint_jobs({("vehicle-1", EntityKey.VEHICLE_WARNING)})

    assert set(jobs) == {
        ("vehicle-1", ENTITY_ENDPOINT[key]) for key in WARNING_ENTITY_KEYS
    }
    assert {key for requested in jobs.values() for key in requested} == set(
        WARNING_ENTITY_KEYS
    )


def test_combined_and_individual_warning_requests_are_deduplicated() -> None:
    """An individual entity reuses the job already needed by the combined one."""
    jobs = endpoint_jobs(
        {
            ("vehicle-1", EntityKey.VEHICLE_WARNING),
            ("vehicle-1", EntityKey.LOW_FUEL_WARNING),
        }
    )

    assert len(jobs) == len(WARNING_ENTITY_KEYS)
    assert jobs[("vehicle-1", ENTITY_ENDPOINT[EntityKey.LOW_FUEL_WARNING])] == {
        EntityKey.LOW_FUEL_WARNING
    }


def test_warning_summary_reports_normal_vehicle() -> None:
    """A complete inactive warning set produces a normal combined result."""
    results = warning_results()

    assert warning_summary(results) == ((), ())
    assert vehicle_warning_result(results).value.value is False


def test_warning_summary_keeps_confirmed_warning_during_partial_failure() -> None:
    """A confirmed warning remains on when another warning endpoint fails."""
    results = warning_results()
    results[EntityKey.LOW_FUEL_WARNING] = EntityResult(
        key=EntityKey.LOW_FUEL_WARNING, value=EntityValue(True)
    )
    results[EntityKey.WASHER_FLUID_WARNING] = EntityResult(
        key=EntityKey.WASHER_FLUID_WARNING,
        value=None,
        error="HyundaiKiaVehicleError",
    )

    assert warning_summary(results) == (
        ("low_fuel_warning",),
        ("washer_fluid_warning",),
    )
    assert vehicle_warning_result(results).value.value is True


def test_warning_summary_reports_multiple_active_warnings() -> None:
    """The summary sorts multiple confirmed warnings deterministically."""
    results = warning_results()
    results[EntityKey.TIRE_PRESSURE_WARNING] = EntityResult(
        key=EntityKey.TIRE_PRESSURE_WARNING, value=EntityValue(True)
    )
    results[EntityKey.LOW_FUEL_WARNING] = EntityResult(
        key=EntityKey.LOW_FUEL_WARNING, value=EntityValue(True)
    )

    active, unavailable = warning_summary(results)

    assert active == ("low_fuel_warning", "tire_pressure_warning")
    assert unavailable == ()
    assert vehicle_warning_result(results).value.value is True


def test_warning_summary_uses_best_effort_for_partial_failures() -> None:
    """Failed warning endpoints remain visible without forcing the master on."""
    results = warning_results()
    results[EntityKey.BRAKE_FLUID_WARNING] = EntityResult(
        key=EntityKey.BRAKE_FLUID_WARNING,
        value=None,
        error="HyundaiKiaVehicleError",
    )
    results.pop(EntityKey.ENGINE_OIL_WARNING)

    active, unavailable = warning_summary(results)

    assert active == ()
    assert unavailable == ("brake_fluid_warning", "engine_oil_warning")
    assert vehicle_warning_result(results).value.value is False


def test_all_warning_failures_still_produce_best_effort_off() -> None:
    """All warning failures remain an off result when the coordinator succeeds."""
    results = {
        key: EntityResult(key=key, value=None, error="HyundaiKiaVehicleError")
        for key in WARNING_ENTITY_KEYS
    }

    active, unavailable = warning_summary(results)

    assert active == ()
    assert unavailable == tuple(sorted(key.value for key in WARNING_ENTITY_KEYS))
    assert vehicle_warning_result(results).value.value is False
