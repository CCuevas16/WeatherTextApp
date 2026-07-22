from user_database import get_subscribed_users
from weather_service import get_weather, send_email


def run_forecast_job() -> None:

    subscribed_users = get_subscribed_users()

    if not subscribed_users:
        print("No subscribed users were found.")
        return

    successful_sends = 0
    failed_sends = 0

    for user in subscribed_users:
        email = user.get("email", "").strip()
        state = user.get("state", "").strip()
        city = user.get("city", "").strip()

        if not email or not state or not city:
            print("Skipping incomplete user record:", user)
            failed_sends += 1
            continue

        try:
            forecast_intervals = get_weather(city, state)

            send_email(
                email,
                city,
                state,
                forecast_intervals
            )

            successful_sends += 1
            print(f"Forecast sent to {email}.")

        except Exception as error:
            failed_sends += 1
            print(f"Unable to send forecast to {email}: {error}")

    print(
        "Forecast job complete. "
        f"Successful: {successful_sends}. "
        f"Failed: {failed_sends}."
    )


if __name__ == "__main__":
    run_forecast_job()