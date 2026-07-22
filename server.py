import re

import requests
from flask import Flask, jsonify, render_template, request

from user_database import save_user, unsubscribe_user
from weather_service import get_weather, send_email

app = Flask(__name__)

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/api/health")
def health():

    return jsonify({
        "status": "running",
        "message": "Weather Forecast Server is running."
    }), 200


@app.route("/api/forecast")
def forecast():

    city = request.args.get("city", "").strip()
    state = request.args.get("state", "").strip()

    if not city or not state:
        return jsonify({
            "success": False,
            "message": "City and state are required."
        }), 400

    try:
        forecast_intervals = get_weather(city, state)

        return jsonify({
            "success": True,
            "location": {
                "city": city,
                "state": state
            },
            "forecast": forecast_intervals
        }), 200

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except requests.RequestException as error:
        print("Weather service error:", error)

        return jsonify({
            "success": False,
            "message": "The weather service could not be reached."
        }), 502

    except Exception as error:
        print("Forecast error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to retrieve the forecast."
        }), 500


@app.route("/api/signup", methods=["POST"])
def signup():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No signup information was received."
        }), 400

    email = data.get("email", "").strip().lower()
    state = data.get("state", "").strip()
    city = data.get("city", "").strip()

    if not email or not state or not city:
        return jsonify({
            "success": False,
            "message": "Email, state, and city are required."
        }), 400

    if not EMAIL_PATTERN.match(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    result = save_user(email, state, city)

    if result == "created":
        message = "You have successfully signed up."
        status_code = 201
    else:
        message = "Your subscription has been updated."
        status_code = 200

    return jsonify({
        "success": True,
        "message": message,
        "user": {
            "email": email,
            "state": state,
            "city": city
        }
    }), status_code


@app.route("/api/unsubscribe", methods=["POST"])
def unsubscribe():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No email address was received."
        }), 400

    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400

    if not EMAIL_PATTERN.match(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    if not unsubscribe_user(email):
        return jsonify({
            "success": False,
            "message": "That email address was not found."
        }), 404

    return jsonify({
        "success": True,
        "message": "You have been unsubscribed successfully."
    }), 200


@app.route("/api/send-email", methods=["POST"])
def send_weather_email():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No email information was received."
        }), 400

    email = data.get("email", "").strip().lower()
    state = data.get("state", "").strip()
    city = data.get("city", "").strip()

    if not email or not state or not city:
        return jsonify({
            "success": False,
            "message": "Email, state, and city are required."
        }), 400

    if not EMAIL_PATTERN.match(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    try:
        forecast_intervals = get_weather(city, state)

        send_email(
            email,
            city,
            state,
            forecast_intervals
        )

        return jsonify({
            "success": True,
            "message": f"Weather email sent to {email}."
        }), 200

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except requests.RequestException as error:
        print("Weather service error:", error)

        return jsonify({
            "success": False,
            "message": "The weather service could not be reached."
        }), 502

    except Exception as error:
        print("Email error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to send the weather email."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
