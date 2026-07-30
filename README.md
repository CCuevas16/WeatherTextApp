Daily weather forecast app


<img width="1127" height="627" alt="image" src="https://github.com/user-attachments/assets/d3d5bdc7-9880-4097-b0a6-47dcc3e10e18" />


A Flask web application that allows users to sign up to receive a 15-hour weather forecast through email. The application uses the OpenWeather API to retrieve forecast data based on the user's selected city and state.

Features

●	Sign up using an email, state, and city

●	Receive a 15-hour weather forecast

●	View temperature, humidity, and rain expectations

●	Convert forecast times to the user's local timezone

●	Unsubscribe from forecast emails

●	Store subscriber information in JSON

●	Frontend and backend input validation

●	Send forecasts to all active subscribers


Project structure

WeatherProject/

├── server.py

├── weather_service.py

├── user_database.py

├── run_forecast_job.py

├── users.json

├── requirements.txt

├── templates/

│   └── index.html

└── static/

    ├── script.js
    
    ├── style.css
    
    └── locations.json
    
    
How it works

The user enters their email and location on the website. JavaScript sends the information to the Flask server, which saves the user's subscription.
When a forecast is generated, the application sends the city and state to OpenWeather's API to find the latitude and longitude. Those coordinates are then used to retrieve the weather forecast.
The forecast is formatted by Python and sent to subscribed users through Gmail.



