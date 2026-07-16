import json

USERS_FILE = "users.json"


def save_user(email, state, city):
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    normalized_email = email.strip().lower()

    # Check whether the user already exists
    for user in data["users"]:
        if user["email"].strip().lower() == normalized_email:

            # Update the existing record instead of creating a duplicate
            user["state"] = state
            user["city"] = city
            user["subscribed"] = True

            with open(USERS_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            print("Existing user updated and subscribed.")
            return "updated"

    # Create the user only if the email does not exist
    new_user = {
        "email": normalized_email,
        "state": state,
        "city": city,
        "subscribed": True
    }

    data["users"].append(new_user)

    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print("New user saved successfully.")
    return "created"


# save_user(
#     "test@email.com",
#     "Indiana",
#     "Indianapolis"
# )

# if __name__ == "__main__":
#     save_user(
#         "newtest@email.com",
#         "Indiana",
#         "Indianapolis"
#     )
    
#     save_user(
#         "newtest@email.com",
#         "Indiana",
#         "Indianapolis"
#     )

# if __name__ == "__main__":
#     save_user(
#         "seconduser@email.com",
#         "Ohio",
#         "Columbus"
#     )

def get_users():
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["users"]

# if __name__ == "__main__":
#     users = get_users()

#     print("Saved users:")
#     print(users)
    
def get_subscribed_users():
    users = get_users()

    subscribed_users = [
        user for user in users
        if user.get("subscribed") is True
    ]

    return subscribed_users


def unsubscribe_user(email):
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    normalized_email = email.strip().lower()

    for user in data["users"]:
        if user["email"].strip().lower() == normalized_email:
            user["subscribed"] = False

            with open(USERS_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            print("User unsubscribed successfully.")
            return True

    print("User not found.")
    return False


# if __name__ == "__main__":
#     subscribed_users = get_subscribed_users()

#     print("Subscribed users:")
#     print(subscribed_users)

# if __name__ == "__main__":
#     print(get_users())
    
# if __name__ == "__main__":
#     unsubscribe_user("seconduser@email.com")    
