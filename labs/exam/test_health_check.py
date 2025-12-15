import pytest
from health_checker import HealthChecker, HealthCheckError


def test_service_is_healthy():
    checker = HealthChecker(db_available=True)

    result = checker.check_service()

    assert result["ok"] is True
    assert result["details"]["database"] == "ok"


def test_service_is_unhealthy():
    checker = HealthChecker(db_available=False)

    result = checker.check_service()

    assert result["ok"] is False
    assert result["details"]["database"] == "down"


def test_invalid_config_raises_error():
    checker = HealthChecker(db_available="yes")

    with pytest.raises(HealthCheckError):
        checker.check_service()