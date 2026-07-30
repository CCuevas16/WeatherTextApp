# Imports function for getting subscribed users
from user_database import get_subscribed_users

# Imports functions for getting weather and sending emails
from weather_service import get_weather, send_email


# Function that runs the forecast email job
def run_forecast_job() -> None:

    # Gets all users who are currently subscribed
    subscribed_users = get_subscribed_users()

    # Stops the program if there are no subscribed users
    if not subscribed_users:
        print("No subscribed users were found.")
        return

    # Keeps track of successful and failed emails
    successful_sends = 0
    failed_sends = 0

    # Loops through each subscribed user
    for user in subscribed_users:

        # Gets the user's information
        email = user.get("email", "").strip()
        state = user.get("state", "").strip()
        city = user.get("city", "").strip()

        # Skips users with missing information
        if not email or not state or not city:
            print("Skipping incomplete user record:", user)
            failed_sends += 1
            continue

        try:
            # Gets the weather for the user's location
            forecast_intervals = get_weather(city, state)

            # Sends the forecast to the user's email
            send_email(
                email,
                city,
                state,
                forecast_intervals
            )

            # Records a successful email
            successful_sends += 1
            print(f"Forecast sent to {email}.")

        # Handles errors without stopping the entire job
        except Exception as error:
            failed_sends += 1
            print(f"Unable to send forecast to {email}: {error}")

    # Displays the final results of the forecast job
    print(
        "Forecast job complete. "
        f"Successful: {successful_sends}. "
        f"Failed: {failed_sends}."
    )


# Runs the forecast job when this file is executed directly
if __name__ == "__main__":
    run_forecast_job()