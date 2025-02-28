from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.logging_utils import setup_basic_logger
from database_manager import DatabaseManager
from user_manager import UserManager

logger = setup_basic_logger()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection after request."""
    DatabaseManager.close_connection(exception)


@app.route("/register", methods=["POST"])
def register():
    """Register new users."""
    data = request.get_json(force=True)
    return jsonify(*UserManager.create_user(data.get("username"), data.get("password")))


@app.route("/login", methods=["POST"])
def login():
    """Authenticate user and return session ID."""
    data = request.get_json(force=True)
    return jsonify(*UserManager.authenticate_user(data.get("username"), data.get("password")))


@app.route("/logout", methods=["POST"])
def logout():
    """Clear session ID on logout."""
    data = request.get_json(force=True)
    return jsonify(*UserManager.logout_user(data.get("session_id")))


@app.route("/connected-users", methods=["GET"])
def get_connected_users():
    """Fetch connected users using session ID."""
    session_id = request.headers.get("Session-Id")
    user_row = UserManager.get_user_by_session(session_id)
    if not user_row:
        return jsonify({"error": "Invalid session"}), 401

    try:
        user_instance = UserManager.create_user_instance(user_row)
        return jsonify(list(user_instance.nodes_names_addresses.keys())), 200
    except Exception as e:
        logger.error(f"Error while fetching connected users: {e}")
        return jsonify({"error": f"Internal server error - {e}"}), 500


if __name__ == "__main__":
    with app.app_context():  # <-- This ensures we have an application context
        DatabaseManager.init_db()
    logger.info("Starting backend server on port 8000!")
    app.run(debug=True, port=8000)
