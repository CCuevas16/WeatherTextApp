import json
from pathlib import Path

USERS_FILE = Path(__file__).with_name("users.json")


def _load_data() -> dict:

    if not USERS_FILE.exists():
        return {"users": []}

    try:
        with USERS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return {"users": []}

    if "users" not in data or not isinstance(data["users"], list):
        return {"users": []}

    return data


def _save_data(data: dict) -> None:

    with USERS_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def save_user(email: str, state: str, city: str) -> str:

    data = _load_data()

    normalized_email = email.strip().lower()
    state = state.strip()
    city = city.strip()

    for user in data["users"]:
        if user.get("email", "").strip().lower() == normalized_email:
            user["state"] = state
            user["city"] = city
            user["subscribed"] = True

            _save_data(data)
            return "updated"

    new_user = {
        "email": normalized_email,
        "state": state,
        "city": city,
        "subscribed": True
    }

    data["users"].append(new_user)
    _save_data(data)

    return "created"


def get_users() -> list[dict]:

    return _load_data()["users"]


def get_subscribed_users() -> list[dict]:

    return [
        user
        for user in get_users()
        if user.get("subscribed") is True
    ]


def unsubscribe_user(email: str) -> bool:

    data = _load_data()
    normalized_email = email.strip().lower()

    for user in data["users"]:
        if user.get("email", "").strip().lower() == normalized_email:
            user["subscribed"] = False
            _save_data(data)
            return True

    return False
