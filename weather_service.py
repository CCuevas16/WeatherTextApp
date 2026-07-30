# Imports tools for environment variables
import os

# Imports tools for sending emails
import smtplib

# Imports tools for working with dates and time zones
from datetime import datetime, timedelta, timezone

# Used to create the email message
from email.message import EmailMessage

# Used to make API requests
import requests

# Loads variables from the .env file
from dotenv import load_dotenv

# Loads the .env file
load_dotenv()

# OpenWeather API endpoints
GEOCODING_ENDPOINT = "https://api.openweathermap.org/geo/1.0/direct"
FORECAST_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"


# Function to get latitude and longitude
def get_coordinates(city: str, state: str) -> tuple[float, float]:

    # Gets API key from .env
    api_key = os.getenv("WEATHER_API_KEY")

    # Checks that the API key exists
    if not api_key:
        raise ValueError("WEATHER_API_KEY is not configured.")

    # Information sent to the geocoding API
    params = {
        "q": f"{city},{state},US",
        "limit": 1,
        "appid": api_key
    }

    # Sends request to OpenWeather
    response = requests.get(
        GEOCODING_ENDPOINT,
        params=params,
        timeout=10
    )

    # Raises an error if request fails
    response.raise_for_status()

    # Converts API response into Python data
    locations = response.json()

    # Checks if the location was found
    if not locations:
        raise ValueError(f"Location not found: {city}, {state}")

    # Returns latitude and longitude
    return locations[0]["lat"], locations[0]["lon"]


# Function to get weather data
def get_weather(city: str, state: str) -> list[dict]:

    # Gets API key from .env
    api_key = os.getenv("WEATHER_API_KEY")

    # Checks that the API key exists
    if not api_key:
        raise ValueError("WEATHER_API_KEY is not configured.")

    # Gets coordinates for the user's city
    latitude, longitude = get_coordinates(city, state)

    # Information sent to the forecast API
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "units": "imperial",
        "cnt": 5
    }

    # Requests forecast data
    response = requests.get(
        FORECAST_ENDPOINT,
        params=params,
        timeout=10
    )

    # Raises an error if request fails
    response.raise_for_status()

    # Converts response into Python data
    weather_data = response.json()

    # Gets the location's UTC offset in seconds
    timezone_offset = weather_data["city"]["timezone"]

    # Creates the location's time zone
    local_timezone = timezone(
        timedelta(seconds=timezone_offset)
    )

    # List that will store each forecast
    forecast_intervals = []

    # Loops through the 5 forecast intervals
    for forecast in weather_data["list"]:

        # Converts forecast time to local time
        local_time = datetime.fromtimestamp(
            forecast["dt"],
            tz=timezone.utc
        ).astimezone(local_timezone)

        # Gets the OpenWeather weather condition ID
        weather_id = forecast["weather"][0]["id"]

        # Adds formatted weather data to the list
        forecast_intervals.append({
            "time": local_time.strftime("%A, %B %d at %I:%M %p"),
            "temperature": round(forecast["main"]["temp"]),
            "humidity": forecast["main"]["humidity"],
            "feels_like": round(forecast["main"]["feels_like"]),
            "description": forecast["weather"][0]["description"],
            "rain_expected": "Yes" if weather_id < 700 else "No"
        })

    # Returns the completed forecast list
    return forecast_intervals


# Function to send the weather email
def send_email(
    receiver: str,
    city: str,
    state: str,
    forecast_intervals: list[dict]
) -> None:

    # Gets email login information from .env
    sender = os.getenv("EMAIL_SENDER")
    app_password = os.getenv("APP_PASSWORD")

    # Checks that email credentials exist
    if not sender or not app_password:
        raise ValueError("Email credentials are not configured.")

    # Stores the formatted forecast sections
    forecast_sections = []

    # Loops through each forecast
    for interval in forecast_intervals:

        # Formats one forecast section
        section = (
            f"Forecast time: {interval['time']}\n"
            f"Weather: {interval['description'].title()}\n"
            f"Temperature: {interval['temperature']}°F\n"
            f"Humidity: {interval['humidity']}%\n"
            f"Feels like: {interval['feels_like']}°F\n"
            f"Rain expected: {interval['rain_expected']}\n"
            f"{'-' * 30}"
        )

        # Adds section to the list
        forecast_sections.append(section)

    # Combines all forecast sections
    forecast_text = "\n\n".join(forecast_sections)

    # Creates a new email
    message = EmailMessage()

    # Sets email information
    message["Subject"] = f"15-Hour Forecast for {city}, {state}"
    message["From"] = sender
    message["To"] = receiver

    # Creates the body of the email
    message.set_content(
        f"""Good morning!

Here is your weather forecast for {city}, {state}.

{forecast_text}

Have a great day!
"""
    )

    # Connects securely to Gmail's SMTP server
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

        # Logs into Gmail
        smtp.login(sender, app_password)

        # Sends the email
        smtp.send_message(message)