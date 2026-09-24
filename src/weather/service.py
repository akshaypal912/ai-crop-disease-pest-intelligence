"""
Weather Service — Fetches current weather data via OpenWeatherMap API.

Configuration:
    Set OPENWEATHER_API_KEY in environment variables or a .env file at
    the project root. If the key is missing the service degrades gracefully:
    all calls return None and the rest of the pipeline continues normally.

Usage:
    from src.weather.service import get_weather_service

    svc = get_weather_service()
    data = svc.get_weather_by_city("Mumbai")
    if data and data["weather_available"]:
        print(data["humidity_pct"])

No API keys are ever hard-coded or logged.
"""

import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Environment variable name — never hard-code the key itself
_API_KEY_ENV = "OPENWEATHER_API_KEY"
_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherService:
    """
    Weather data provider backed by OpenWeatherMap current-weather endpoint.

    If OPENWEATHER_API_KEY is not set, all public methods return a
    "not configured" result dict with weather_available=False. The rest of
    the inference pipeline handles this gracefully by skipping weather
    context in risk scoring.
    """

    def __init__(self):
        self._api_key: Optional[str] = os.environ.get(_API_KEY_ENV)
        if not self._api_key:
            logger.info(
                "WeatherService: %s not set. Running in image-only mode. "
                "Set the environment variable (or .env file) to enable weather context.",
                _API_KEY_ENV,
            )

    @property
    def is_configured(self) -> bool:
        """Returns True only when an API key is present in the environment."""
        return bool(self._api_key)

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch current weather for a geographic coordinate.

        Args:
            lat: Latitude in decimal degrees.
            lon: Longitude in decimal degrees.

        Returns:
            Parsed weather dict or a not-available dict.
        """
        if not self.is_configured:
            return self._not_configured_result()
        return self._fetch(params={"lat": lat, "lon": lon})

    def get_weather_by_city(self, city_name: str) -> Dict[str, Any]:
        """
        Fetch current weather for a named city.

        Args:
            city_name: City name string (e.g. "Mumbai", "Nairobi,KE").

        Returns:
            Parsed weather dict or a not-available dict.
        """
        if not self.is_configured:
            return self._not_configured_result()
        if not city_name or not city_name.strip():
            return self._error_result("City name is empty.")
        return self._fetch(params={"q": city_name.strip()})

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls the OpenWeatherMap /weather endpoint with the given params.
        Handles HTTP errors and network failures gracefully.
        """
        try:
            import requests  # lazy import — not mandatory for core platform
        except ImportError:
            logger.warning("requests library not installed. Cannot fetch weather data.")
            return self._error_result("requests library not available.")

        params = dict(params)
        params["appid"] = self._api_key   # key is never logged
        params["units"] = "metric"        # always return °C
        params["lang"] = "en"

        try:
            response = requests.get(_BASE_URL, params=params, timeout=8)
            response.raise_for_status()
            return self._parse_response(response.json())
        except requests.exceptions.Timeout:
            logger.warning("Weather API request timed out.")
            return self._error_result("Weather API request timed out.")
        except requests.exceptions.HTTPError as http_err:
            status = getattr(http_err.response, "status_code", "?")
            if status == 401:
                logger.warning("Weather API: invalid or expired API key (401).")
                return self._error_result("Invalid or expired OPENWEATHER_API_KEY.")
            if status == 404:
                return self._error_result("Location not found (404).")
            logger.warning("Weather API HTTP error %s.", status)
            return self._error_result(f"Weather API error (HTTP {status}).")
        except requests.exceptions.ConnectionError:
            logger.warning("Weather API: network connection failed.")
            return self._error_result("Network connection error. Check internet access.")
        except Exception as exc:
            logger.warning("Weather API unexpected error: %s", exc)
            return self._error_result(f"Unexpected error: {exc}")

    @staticmethod
    def _parse_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract standardised fields from an OpenWeatherMap API response dict.

        OpenWeatherMap API docs: https://openweathermap.org/current
        """
        try:
            rain = data.get("rain", {})
            # "1h" field is rainfall in last 1 hour in mm
            rainfall_mm = rain.get("1h", rain.get("3h", 0.0))

            return {
                "weather_available": True,
                "location_name": data.get("name", "Unknown"),
                "country": data.get("sys", {}).get("country", ""),
                "temperature_c": data.get("main", {}).get("temp"),
                "feels_like_c": data.get("main", {}).get("feels_like"),
                "humidity_pct": data.get("main", {}).get("humidity"),
                "pressure_hpa": data.get("main", {}).get("pressure"),
                "wind_speed_ms": data.get("wind", {}).get("speed"),
                "wind_direction_deg": data.get("wind", {}).get("deg"),
                "rainfall_mm": float(rainfall_mm),
                "cloud_cover_pct": data.get("clouds", {}).get("all"),
                "condition": data.get("weather", [{}])[0].get("main", "Unknown"),
                "description": data.get("weather", [{}])[0].get("description", ""),
                "visibility_m": data.get("visibility"),
                "error": None,
            }
        except Exception as exc:
            logger.warning("Failed to parse weather API response: %s", exc)
            return WeatherService._error_result(f"Response parse error: {exc}")

    @staticmethod
    def _not_configured_result() -> Dict[str, Any]:
        """Returned when API key is not configured."""
        return {
            "weather_available": False,
            "error": (
                f"Weather service not configured. Set the {_API_KEY_ENV} "
                "environment variable to enable weather context."
            ),
        }

    @staticmethod
    def _error_result(message: str) -> Dict[str, Any]:
        """Returned on any API/network error."""
        return {
            "weather_available": False,
            "error": message,
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_service_instance: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """
    Singleton getter for WeatherService.

    The singleton is intentionally NOT cached across environment changes
    (e.g., tests that dynamically set/unset the API key) — it re-reads
    the env var on each process start.
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = WeatherService()
    return _service_instance


def reset_weather_service() -> None:
    """Force re-initialisation of the singleton (useful for tests)."""
    global _service_instance
    _service_instance = None
