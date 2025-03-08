from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from utils.logging_utils import setup_basic_logger
from database_manager import DatabaseManager
from user_manager import UserManager

logger = setup_basic_logger()

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3000"],
    allow_headers=["Content-Type", "Session-Id"],
    methods=["GET", "POST", "OPTIONS"]
)


@app.after_request
def add_cors_headers(response):
    """✅ Manually ensure all responses include CORS headers"""
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Session-Id"
    return response


@app.before_request
def log_request():
    """Logs incoming requests with payload details."""
    logger.info(f"Incoming {request.method} request to {request.path}")
    if request.method in ["POST", "PUT"]:
        logger.info(f"Request Data: {request.get_json(silent=True)}")


@app.teardown_appcontext
def close_connection(exception):
    """Close database connection after request."""
    DatabaseManager.close_connection(exception)


@app.route("/register", methods=["POST"])
def register():
    """Register new users."""
    try:
        data = request.get_json(force=True)
        username, password = data.get("username"), data.get("password")
        logger.info(f"Attempting to register user: {username}")
        response, status = UserManager.create_user(username, password)
        logger.info(f"Registration response: {response}")
        return jsonify(response), status
    except Exception as e:
        logger.error(f"Error in /register: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/login", methods=["POST"])
def login():
    """Authenticate user and return session ID."""
    try:
        data = request.get_json(force=True)
        username, password = data.get("username"), data.get("password")
        logger.info(f"User login attempt: {username}")
        response, status = UserManager.authenticate_user(username, password)
        logger.info(f"Login response: {response}")
        return jsonify(response), status
    except Exception as e:
        logger.error(f"Error in /login: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/logout", methods=["POST"])
def logout():
    """Clear session ID on logout."""
    try:
        data = request.get_json(force=True)
        session_id = data.get("session_id")
        logger.info(f"Logging out user with session ID: {session_id}")
        response, status = UserManager.logout_user(session_id)
        logger.info(f"Logout response: {response}")
        return jsonify(response), status
    except Exception as e:
        logger.error(f"Error in /logout: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/transactions", methods=["GET", "POST", "OPTIONS"])
@cross_origin()
def transactions():
    """Handle transactions (GET, POST) with session-based authentication."""
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200  # ✅ Handle preflight request

    session_id = request.headers.get("Session-Id")
    if not session_id:
        return jsonify({"error": "Session ID missing"}), 401

    if request.method == "GET":
        response, status = UserManager.handle_transactions(session_id, "GET")
    elif request.method == "POST":
        data = request.get_json(force=True)
        response, status = UserManager.handle_transactions(session_id, "POST", data)

    return jsonify(response), status


@app.route("/connected-users", methods=["GET"])
def get_connected_users():
    """Fetch connected users using session ID."""
    try:
        session_id = request.headers.get("Session-Id")
        logger.info(f"Fetching connected users for session: {session_id}")
        user_row = UserManager.get_user_by_session(session_id)
        if not user_row:
            logger.warning("Invalid session ID")
            return jsonify({"error": "Invalid session"}), 401

        user_instance = UserManager.create_user_instance(user_row)
        connected_users = list(user_instance.nodes_names_addresses.keys())
        logger.info(f"Connected users fetched: {connected_users}")
        return jsonify(connected_users), 200
    except Exception as e:
        logger.error(f"Error in /connected-users: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    with app.app_context():
        DatabaseManager.init_db()
    logger.info("Starting backend server on port 8000!")
    app.run(debug=True, port=8000)
