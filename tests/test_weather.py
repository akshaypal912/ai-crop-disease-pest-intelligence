"""
Tests for src/weather/service.py

Tests:
- Missing API key → weather_available=False, no exception
- Invalid city name → graceful error dict (not an exception)
- Return schema when mocked with a valid API response
- reset_weather_service() re-reads environment
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.weather.service import WeatherService, get_weather_service, reset_weather_service

# ---------------------------------------------------------------------------
# Minimal valid OpenWeatherMap API response structure for mocking
# ---------------------------------------------------------------------------
MOCK_OWM_RESPONSE = {
    "name": "TestCity",
    "sys": {"country": "IN"},
    "main": {
        "temp": 28.5,
        "feels_like": 30.0,
        "humidity": 82,
        "pressure": 1008,
    },
    "wind": {"speed": 3.2, "deg": 180},
    "rain": {"1h": 2.5},
    "clouds": {"all": 75},
    "weather": [{"main": "Rain", "description": "moderate rain"}],
    "visibility": 8000,
}

EXPECTED_WEATHER_KEYS = {
    "weather_available",
    "location_name",
    "country",
    "temperature_c",
    "humidity_pct",
    "rainfall_mm",
    "wind_speed_ms",
    "condition",
    "description",
    "error",
}


# ---------------------------------------------------------------------------
# Test: Missing API key (no environment variable set)
# ---------------------------------------------------------------------------

class TestMissingApiKey:
    """When OPENWEATHER_API_KEY is absent, service returns not-configured result."""

    def setup_method(self):
        reset_weather_service()

    def teardown_method(self):
        reset_weather_service()

    def test_not_configured_when_key_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            # Make sure the key is absent
            os.environ.pop("OPENWEATHER_API_KEY", None)
            svc = WeatherService()
            assert not svc.is_configured

    def test_get_weather_returns_not_available_when_key_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENWEATHER_API_KEY", None)
            svc = WeatherService()
            result = svc.get_weather(lat=19.0, lon=72.8)
            assert result["weather_available"] is False
            assert "error" in result
            assert isinstance(result["error"], str)

    def test_get_weather_by_city_returns_not_available_when_key_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENWEATHER_API_KEY", None)
            svc = WeatherService()
            result = svc.get_weather_by_city("Mumbai")
            assert result["weather_available"] is False
            assert "error" in result

    def test_missing_key_does_not_raise_exception(self):
        """Critical: missing key must NEVER crash the application."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENWEATHER_API_KEY", None)
            svc = WeatherService()
            try:
                result = svc.get_weather_by_city("AnyCity")
                assert isinstance(result, dict)
            except Exception as exc:
                pytest.fail(
                    f"WeatherService raised an exception when key is missing: {exc}"
                )


# ---------------------------------------------------------------------------
# Test: Empty / invalid city name
# ---------------------------------------------------------------------------

class TestInvalidCity:

    def test_empty_city_name_returns_error_dict(self):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake-key-for-test"}):
            reset_weather_service()
            svc = WeatherService()
            result = svc.get_weather_by_city("   ")
            assert result["weather_available"] is False
            assert "error" in result

    def test_whitespace_city_name_returns_error_dict(self):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake-key-for-test"}):
            reset_weather_service()
            svc = WeatherService()
            result = svc.get_weather_by_city("")
            assert result["weather_available"] is False


# ---------------------------------------------------------------------------
# Test: Mocked successful API response schema
# ---------------------------------------------------------------------------

class TestMockedSuccessResponse:
    """Mock the HTTP call to validate parsing and schema."""

    def _make_mock_response(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_OWM_RESPONSE
        mock_resp.raise_for_status = MagicMock(return_value=None)
        mock_resp.status_code = 200
        return mock_resp

    def test_parsed_response_schema(self):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake-key-for-test"}):
            reset_weather_service()
            svc = WeatherService()
            with patch("requests.get", return_value=self._make_mock_response()):
                result = svc.get_weather_by_city("TestCity")

        assert result["weather_available"] is True
        for key in EXPECTED_WEATHER_KEYS:
            assert key in result, f"Missing key in weather result: '{key}'"

    def test_temperature_is_float(self):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake-key-for-test"}):
            reset_weather_service()
            svc = WeatherService()
            with patch("requests.get", return_value=self._make_mock_response()):
                result = svc.get_weather_by_city("TestCity")
        assert isinstance(result["temperature_c"], (int, float))
        assert result["temperature_c"] == pytest.approx(28.5)

    def test_humidity_is_int_or_float(self):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake-key-for-test"}):
            reset_weather_service()
            svc = WeatherService()
            with patch("requests.get", return_value=self._make_mock_response()):
                result = svc.get_weather_by_city("TestCity")
        assert result["humidity_pct"] == 82

    def test_rainfall_parsed_from_rain_1h(self):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake-key-for-test"}):
            reset_weather_service()
            svc = WeatherService()
            with patch("requests.get", return_value=self._make_mock_response()):
                result = svc.get_weather_by_city("TestCity")
        assert result["rainfall_mm"] == pytest.approx(2.5)

    def test_location_name_parsed(self):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake-key-for-test"}):
            reset_weather_service()
            svc = WeatherService()
            with patch("requests.get", return_value=self._make_mock_response()):
                result = svc.get_weather_by_city("TestCity")
        assert result["location_name"] == "TestCity"


# ---------------------------------------------------------------------------
# Test: Network timeout / HTTP error handling
# ---------------------------------------------------------------------------

class TestNetworkErrors:

    def test_timeout_returns_error_dict(self):
        import requests as req
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake-key-for-test"}):
            reset_weather_service()
            svc = WeatherService()
            with patch("requests.get", side_effect=req.exceptions.Timeout):
                result = svc.get_weather_by_city("Mumbai")
        assert result["weather_available"] is False
        assert "timed out" in result["error"].lower()

    def test_connection_error_returns_error_dict(self):
        import requests as req
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake-key-for-test"}):
            reset_weather_service()
            svc = WeatherService()
            with patch("requests.get", side_effect=req.exceptions.ConnectionError):
                result = svc.get_weather_by_city("Mumbai")
        assert result["weather_available"] is False
        assert "network" in result["error"].lower() or "connection" in result["error"].lower()

    def test_401_returns_error_dict(self):
        import requests as req
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        http_error = req.exceptions.HTTPError(response=mock_resp)
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "bad-key"}):
            reset_weather_service()
            svc = WeatherService()
            with patch("requests.get", side_effect=http_error):
                result = svc.get_weather_by_city("Mumbai")
        assert result["weather_available"] is False

    def test_404_city_not_found(self):
        import requests as req
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        http_error = req.exceptions.HTTPError(response=mock_resp)
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "fake-key-for-test"}):
            reset_weather_service()
            svc = WeatherService()
            with patch("requests.get", side_effect=http_error):
                result = svc.get_weather_by_city("NonExistentCityXYZ")
        assert result["weather_available"] is False
        assert "404" in result["error"] or "not found" in result["error"].lower()


# ---------------------------------------------------------------------------
# Test: Singleton reset
# ---------------------------------------------------------------------------

class TestSingletonReset:

    def test_reset_creates_new_instance(self):
        reset_weather_service()
        svc1 = get_weather_service()
        reset_weather_service()
        svc2 = get_weather_service()
        assert svc1 is not svc2

    def teardown_method(self):
        reset_weather_service()
