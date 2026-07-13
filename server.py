from flask import Flask, jsonify
from database import db, User

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"


db.init_app(app)


@app.route("/")
def home():
    return "Weather Forecast Server is running!"


@app.route("/forecast")
def forecast():
    weather = {
        "temperature": 78,
        "feels_like": 76,
        "rain_expected": "No"
    }

    return jsonify(weather)

@app.route("/users/create")
def create_user():
    existing_user = db.session.execute(
        db.select(User).where(User.email == "cacuevas21@gmail.com")
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({
            "message": "User already exists",
            "user_id": existing_user.id
        }), 409

    new_user = User(
        name="Carlos",
        email="cacuevas21@gmail.com"
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    }), 201


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
