import time
import threading

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from utils.logging_utils import setup_basic_logger
from database_manager import DatabaseManager
from user_manager import UserManager
from user_session_manager import UserSessionManager

logger = setup_basic_logger()

ALLOWED_ORIGINS = {"http://localhost:3000", "https://localhost:3000"}

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=list(ALLOWED_ORIGINS),
    allow_headers=["Content-Type", "Session-Id"],
    methods=["GET", "POST", "OPTIONS"]
)


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
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
    """Authenticate user and create persistent session."""
    try:
        data = request.get_json(force=True)
        username, password = data.get("username"), data.get("password")
        logger.info(f"User login attempt: {username}")

        response, status = UserManager.authenticate_user(username, password)

        if status == 200:
            session_id = response.get("session_id")
            # Retrieve the pre-loaded user instance from the global registry.
            user_instance = UserManager.all_users.get(username)
            if not user_instance:
                user_row = UserManager.get_user_by_username(username)
                if user_row:
                    user_instance = UserManager.create_user_instance(user_row)
                    UserManager.all_users[username] = user_instance
            UserSessionManager.get_instance().add_user(session_id, user_instance)

        logger.info(f"Login response: {response}")
        return jsonify(response), status
    except Exception as e:
        logger.error(f"Error in /login: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/logout", methods=["POST"])
def logout():
    """Clear session and cleanup user instance."""
    try:
        data = request.get_json(force=True)
        session_id = data.get("session_id")
        logger.info(f"Logging out user with session ID: {session_id}")

        # Remove user instance first.
        UserSessionManager.get_instance().remove_user(session_id)

        # Then clear session from database.
        response, status = UserManager.logout_user(session_id)
        logger.info(f"Logout response: {response}")
        return jsonify(response), status
    except Exception as e:
        logger.error(f"Error in /logout: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/transactions", methods=["GET", "POST", "OPTIONS"])
@cross_origin()
def transactions():
    """Handle transactions using UserManager."""
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200

    session_id = request.headers.get("Session-Id")
    if not session_id:
        return jsonify({"error": "Session ID missing"}), 401

    try:
        if request.method == "GET":
            response, status = UserManager.handle_transactions(session_id, "GET")
        elif request.method == "POST":
            data = request.get_json(force=True)
            response, status = UserManager.handle_transactions(session_id, "POST", data)

        return jsonify(response), status
    except Exception as e:
        logger.error(f"Error handling transaction: {e}")
        return jsonify({"error": "Transaction processing failed"}), 500


@app.route("/connected-users", methods=["GET"])
def get_connected_users():
    """Fetch connected users from active sessions."""
    try:
        session_id = request.headers.get("Session-Id")
        logger.info(f"Fetching connected users for session: {session_id}")

        user_instance = UserSessionManager.get_instance().get_user(session_id)
        if not user_instance:
            return jsonify({"error": "Invalid or expired session"}), 401

        # Get connected users from the persistent instance.
        connected_users = list(user_instance.nodes_names_addresses.keys())
        logger.info(f"Connected users fetched: {connected_users}")
        return jsonify(connected_users), 200
    except Exception as e:
        logger.error(f"Error in /connected-users: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    """Keep user session alive."""
    try:
        session_id = request.headers.get("Session-Id")
        if not session_id:
            return jsonify({"error": "Session ID missing"}), 401

        user_instance = UserSessionManager.get_instance().get_user(session_id)
        if not user_instance:
            return jsonify({"error": "Invalid or expired session"}), 401

        return jsonify({"status": "alive"}), 200
    except Exception as e:
        logger.error(f"Error in heartbeat: {e}")
        return jsonify({"error": "Internal server error"}), 500


def cleanup_task():
    """Periodic task to clean up inactive sessions."""
    while True:
        try:
            UserSessionManager.get_instance().cleanup_inactive_sessions()
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
        time.sleep(60)  # Run every minute


if __name__ == "__main__":
    # Start cleanup thread.
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()

    # Initialize database and then load all user objects from the database.
    with app.app_context():
        DatabaseManager.init_db()
        UserManager.initialize_users()

    logger.info("Starting backend server on port 8000!")
    app.run(
        debug=True,
        host="0.0.0.0",  # Accept connections from any IP
        port=8000,
        ssl_context=('ssl/cert.pem', 'ssl/key.pem')
    )
