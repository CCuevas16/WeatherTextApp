import os
from dotenv import load_dotenv
import requests
import smtplib
from email.message import EmailMessage

load_dotenv()

OPENWEATHER_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"


def get_weather():
    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        raise ValueError("WEATHER_API_KEY is not set.")

    weather_params = {
        "lat": 39.768402,
        "lon": -86.158066,
        "appid": api_key,
        "units": "imperial",
        "cnt": 5
    }

    response = requests.get(
        OPENWEATHER_ENDPOINT,
        params=weather_params,
        timeout=10
    )
    response.raise_for_status()

    weather_data = response.json()

    rain_expected = will_it_rain(weather_data)

    return {
        "temperature": weather_data["list"][0]["main"]["temp"],
        "feels_like": weather_data["list"][0]["main"]["feels_like"],
        "description": weather_data["list"][0]["weather"][0]["description"],
        "rain_expected": rain_expected
    }


def will_it_rain(weather_data):
    for forecast in weather_data["list"]:
        weather_id = forecast["weather"][0]["id"]

        if weather_id < 700:
            return "Yes"

    return "No"


def sending_email(receiver, weather):
    sender = os.getenv("EMAIL_SENDER")
    app_password = os.getenv("APP_PASSWORD")

    if not sender or not app_password:
        raise ValueError("Email credentials are not configured.")

    msg = EmailMessage()
    msg["Subject"] = "Today's Weather Forecast"
    msg["From"] = sender
    msg["To"] = receiver

    msg.set_content(
        f"""Good morning!

Current weather: {weather["description"].title()}
Temperature: {weather["temperature"]}°F
Feels like: {weather["feels_like"]}°F
Rain expected: {weather["rain_expected"]}
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)

print(get_weather())
sending_email("cacuevas21@gmail.com", get_weather())