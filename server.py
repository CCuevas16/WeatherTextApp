#Imports expression module to check whether an email has a valid format
import re

#Imports the requests library which allows python to communicate with external API's over Http
import requests

#Imports the flask tools needed by our server. Flask creates the web server
#Jsonify converts python dictionaries into JSON responses
#render_template allows flash to load html files
#request allows us to access information sent by the browser/client
from flask import Flask, jsonify, render_template, request

#Imports our dtatbase functions from user_database.py
#save_user() saves or updates a subscriber
from user_database import save_user, unsubscribe_user

#Imports our weather functions from weather_service.py
from weather_service import get_weather, send_email

#creates flash application. __name__ tells flash where this application is located
app = Flask(__name__)

#Creates a regualr expression pattern used to validate email addresses
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

#Creates the route for the main/home page. GET default
@app.route("/")
def home():

    #loads and sends the html page to the browser
    return render_template("index.html")

#Creates an endpoint to check whether the Flask server is working
@app.route("/api/health")
def health():

    #converts python dictionary into JSON and returns the HTTP status code
    return jsonify({
        "status": "running",
        "message": "Weather Forecast Server is running."
    }), 200

# Creates an endpoint used to retrieve a weather forecast. GET default
@app.route("/api/forecast")
def forecast():

    # gets city and state parameter from the URL
    city = request.args.get("city", "").strip()
    state = request.args.get("state", "").strip()

    #Checks to see if the entries were given otherwise it returns an error status in JSON
    if not city or not state:
        return jsonify({
            "success": False,
            "message": "City and state are required."
        }), 400

    #The try block is so that the server continues to execute even if there is an error
    try:
        #calls get_weather() from weather_service.py. The user input of city and state are passed to it.
        #The returned forecast is stored in forecast_intervals
        forecast_intervals = get_weather(city, state)

        #if the request success, this will return a success json data table
        return jsonify({
            "success": True,
            "location": {
                "city": city,
                "state": state
            },
            "forecast": forecast_intervals
        }), 200

    #Handles ValueError exceptions such as a city or state can not be found
    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    #Handles caused by the requests library, so if OpenWeather cannont be reached for whatever reason
    except requests.RequestException as error:
        #Prints the exact error
        print("Weather service error:", error)

        #Secondary message to user
        return jsonify({
            "success": False,
            "message": "The weather service could not be reached."
        }), 502

    #Handles any other error.
    except Exception as error:
        #Prints that error.
        print("Forecast error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to retrieve the forecast."
        }), 500


#Creates a sign up API endpoint and only accepts POST requests since its specified. User will be sending info to server
@app.route("/api/signup", methods=["POST"])
def signup():

    #Reads JSON data sent in the body of a POST request. Silent prevents Flash from throwing an automatic error
    #if the JSON can not be read
    data = request.get_json(silent=True)

    #Checks if any JSON data was received and if not an error message is sent
    if not data:
        return jsonify({
            "success": False,
            "message": "No signup information was received."
        }), 400

    email = data.get("email", "").strip().lower()
    state = data.get("state", "").strip()
    city = data.get("city", "").strip()

    #Checks if one for the of the fields is missing
    if not email or not state or not city:
        return jsonify({
            "success": False,
            "message": "Email, state, and city are required."
        }), 400

    #checks email against our email regular expression
    if not EMAIL_PATTERN.match(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    #calls save_user() from user_database.py and creates subscriber or updates subscriber
    result = save_user(email, state, city)

    #checks if a new subscriber was created or updated
    if result == "created":
        message = "You have successfully signed up."
        status_code = 201
    else:
        message = "Your subscription has been updated."
        status_code = 200

    #Sends that data back as JSON if everything was successful
    return jsonify({
        "success": True,
        "message": message,
        "user": {
            "email": email,
            "state": state,
            "city": city
        }
    }), status_code

#Creates endpoint to unsubscribe someone. Expect POST request
@app.route("/api/unsubscribe", methods=["POST"])
def unsubscribe():

    #reads JSON data sent by browser/client
    data = request.get_json(silent=True)

    #checks whether data was actually received
    if not data:
        return jsonify({
            "success": False,
            "message": "No email address was received."
        }), 400

    email = data.get("email", "").strip().lower()

    #checks to see if an email was specifically received
    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400

    #validates email/ compares email to our expression
    if not EMAIL_PATTERN.match(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    #Calls unsubscribe_user from user_database.py to check if the return is false, if so the email doesn't exist
    if not unsubscribe_user(email):
        return jsonify({
            "success": False,
            "message": "That email address was not found."
        }), 404

    #if success, a JSON success message is returned
    return jsonify({
        "success": True,
        "message": "You have been unsubscribed successfully."
    }), 200

#Creates a send-mail endpoint to immediately send a weather email for testing purposes. accepts POST requests
@app.route("/api/send-email", methods=["POST"])
def send_weather_email():

    #gets weather data from sent by client/browser
    data = request.get_json(silent=True)

    #checks to see if data was given
    if not data:
        return jsonify({
            "success": False,
            "message": "No information was received."
        }), 400

    email = data.get("email", "").strip().lower()
    state = data.get("state", "").strip()
    city = data.get("city", "").strip()

    #checks to see if a field specifically is missing
    if not email or not state or not city:
        return jsonify({
            "success": False,
            "message": "Email, state, and city are required."
        }), 400

    #validates email
    if not EMAIL_PATTERN.match(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    try:
        # calls the get_weather() function from weather_service.py
        forecast_intervals = get_weather(city, state)

        #if success sends email
        send_email(
            email,
            city,
            state,
            forecast_intervals
        )

        #success message in JSON
        return jsonify({
            "success": True,
            "message": f"Weather email sent to {email}."
        }), 200

    #Handles value errors
    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    #handles communication with API errors
    except requests.RequestException as error:
        print("Weather service error:", error)

        return jsonify({
            "success": False,
            "message": "The weather service could not be reached."
        }), 502

    #Handles any other error
    except Exception as error:
        print("Email error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to send the weather email."
        }), 500

# __name__ will equal "__main__" when we run this file directly.
# For example: python server.py
if __name__ == "__main__":
    # Starts Flask's development server.
    # debug=True automatically reloads the server when code changes
    # and provides detailed debugging information during development
    app.run(debug=True)

