# Imports tools for working with JSON files
import json

# imports Path for working with file paths
from pathlib import Path


# Creates the path to the users.json file
USERS_FILE = Path(__file__).with_name("users.json")


# Function to load user data from the JSON file
def _load_data() -> dict:

    # Returns an empty user list if the file does not exist
    if not USERS_FILE.exists():
        return {"users": []}

    try:
        # Opens the JSON file for reading
        with USERS_FILE.open("r", encoding="utf-8") as file:

            # Converts JSON data into Python data
            data = json.load(file)

    # Handles invalid JSON or file errors
    except (json.JSONDecodeError, OSError):
        return {"users": []}

    # makes sure the users list exists and is valid
    if "users" not in data or not isinstance(data["users"], list):
        return {"users": []}

    # Returns the loaded data
    return data


# Function to save data to the JSON file
def _save_data(data: dict) -> None:

    # Opns the JSON file for writing
    with USERS_FILE.open("w", encoding="utf-8") as file:

        # Saves Python data as formatted JSON
        json.dump(data, file, indent=4)


# Function to create or update a user
def save_user(email: str, state: str, city: str) -> str:

    # Loads existing user data
    data = _load_data()

    # Cleans and standardizes user input
    normalized_email = email.strip().lower()
    state = state.strip()
    city = city.strip()

    # Loops through existing users
    for user in data["users"]:

        # Checks if the email already exists
        if user.get("email", "").strip().lower() == normalized_email:

            # Updates the existing user's information
            user["state"] = state
            user["city"] = city
            user["subscribed"] = True

            # Saves the updated data
            _save_data(data)

            # Tells the program the user was updated
            return "updated"

    # Creates a new user
    new_user = {
        "email": normalized_email,
        "state": state,
        "city": city,
        "subscribed": True
    }

    # Adds the new user to the list
    data["users"].append(new_user)

    # Saves the updated user list
    _save_data(data)

    # Tells the program a new user was created
    return "created"


# Function to get all users
def get_users() -> list[dict]:

    # Returns the users list from the JSON file
    return _load_data()["users"]


# Function to get only subscribed users
def get_subscribed_users() -> list[dict]:

    # Returns users whose subscribed value is True
    return [
        user
        for user in get_users()
        if user.get("subscribed") is True
    ]


# Function to unsubscribe a user
def unsubscribe_user(email: str) -> bool:

    # Loads existing user data
    data = _load_data()

    # Cleans and standardizes the email
    normalized_email = email.strip().lower()

    # Searches for the user's email
    for user in data["users"]:

        # Checks if the email matches
        if user.get("email", "").strip().lower() == normalized_email:

            # Changes the user's subscription status
            user["subscribed"] = False

            # Saves the change
            _save_data(data)

            # Returns True if the user was found
            return True

    # Returns False if the user was not found
    return False
