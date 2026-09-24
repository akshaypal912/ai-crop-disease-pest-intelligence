"""
Weather Integration Module — Fetches current weather data via OpenWeatherMap API.

API key must be set in the OPENWEATHER_API_KEY environment variable (or .env file).
If the key is absent or invalid, all weather calls return None gracefully and the
application continues in image-only mode.
"""

from .service import WeatherService, get_weather_service

__all__ = ["WeatherService", "get_weather_service"]
