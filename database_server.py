from flask import Flask, request, jsonify
from flask_cors import CORS
from user_database import save_user, unsubscribe_user

app = Flask(__name__)
CORS(app)


@app.route("/save-user", methods=["POST"])
def receive_user():
    user = request.get_json()

    if not user:
        return jsonify({
            "success": False,
            "message": "No user data received."
        }), 400

    print("User received:", user)

    save_user(
        user["email"],
        user["state"],
        user["city"]
    )

    return jsonify({
        "success": True,
        "message": "User saved successfully."
    })


@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No email received."
        }), 400

    email = data.get("email", "").strip()

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400

    user_found = unsubscribe_user(email)

    if not user_found:
        return jsonify({
            "success": False,
            "message": "Email not found."
        }), 404

    return jsonify({
        "success": True,
        "message": "You have been unsubscribed successfully."
    })


if __name__ == "__main__":
    app.run(port=5001, debug=True)
