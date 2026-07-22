import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

import requests
from dotenv import load_dotenv

load_dotenv()

GEOCODING_ENDPOINT = "https://api.openweathermap.org/geo/1.0/direct"
FORECAST_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"


def get_coordinates(city: str, state: str) -> tuple[float, float]:

    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        raise ValueError("WEATHER_API_KEY is not configured.")

    params = {
        "q": f"{city},{state},US",
        "limit": 1,
        "appid": api_key
    }

    response = requests.get(
        GEOCODING_ENDPOINT,
        params=params,
        timeout=10
    )
    response.raise_for_status()

    locations = response.json()

    if not locations:
        raise ValueError(f"Location not found: {city}, {state}")

    return locations[0]["lat"], locations[0]["lon"]


def get_weather(city: str, state: str) -> list[dict]:

    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        raise ValueError("WEATHER_API_KEY is not configured.")

    latitude, longitude = get_coordinates(city, state)

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "units": "imperial",
        "cnt": 5
    }

    response = requests.get(
        FORECAST_ENDPOINT,
        params=params,
        timeout=10
    )
    response.raise_for_status()

    weather_data = response.json()

    timezone_offset = weather_data["city"]["timezone"]
    local_timezone = timezone(
        timedelta(seconds=timezone_offset)
    )

    forecast_intervals = []

    for forecast in weather_data["list"]:
        local_time = datetime.fromtimestamp(
            forecast["dt"],
            tz=timezone.utc
        ).astimezone(local_timezone)

        weather_id = forecast["weather"][0]["id"]

        forecast_intervals.append({
            "time": local_time.strftime("%A, %B %d at %I:%M %p"),
            "temperature": round(forecast["main"]["temp"]),
            "humidity": forecast["main"]["humidity"],
            "feels_like": round(forecast["main"]["feels_like"]),
            "description": forecast["weather"][0]["description"],
            "rain_expected": "Yes" if weather_id < 700 else "No"
        })

    return forecast_intervals


def send_email(
    receiver: str,
    city: str,
    state: str,
    forecast_intervals: list[dict]
) -> None:
    """Send a 15-hour weather forecast email."""

    sender = os.getenv("EMAIL_SENDER")
    app_password = os.getenv("APP_PASSWORD")

    if not sender or not app_password:
        raise ValueError("Email credentials are not configured.")

    forecast_sections = []

    for interval in forecast_intervals:
        section = (
            f"Forecast time: {interval['time']}\n"
            f"Weather: {interval['description'].title()}\n"
            f"Temperature: {interval['temperature']}°F\n"
            f"Humidity: {interval['humidity']}%\n"
            f"Feels like: {interval['feels_like']}°F\n"
            f"Rain expected: {interval['rain_expected']}\n"
            f"{'-' * 30}"
        )

        forecast_sections.append(section)

    forecast_text = "\n\n".join(forecast_sections)

    message = EmailMessage()
    message["Subject"] = f"15-Hour Forecast for {city}, {state}"
    message["From"] = sender
    message["To"] = receiver

    message.set_content(
        f"""Good morning!

Here is your weather forecast for {city}, {state}.

{forecast_text}

Have a great day!
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(message)