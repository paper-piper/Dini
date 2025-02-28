import uuid
from network.user import User
from core.transaction import get_sk_pk_pair
from utils.logging_utils import setup_basic_logger
from database_manager import DatabaseManager

logger = setup_basic_logger()


class UserManager:
    """Manages user authentication and cryptocurrency operations."""

    @staticmethod
    def create_session():
        """Generates a new session ID using UUID."""
        return str(uuid.uuid4())

    @staticmethod
    def get_user_by_username(username):
        """Retrieves a user row by username."""
        query = "SELECT * FROM users WHERE username = ?"
        return DatabaseManager.execute_query(query, (username,), fetchone=True)

    @staticmethod
    def get_user_by_session(session_id):
        """Retrieves a user row by session ID."""
        query = "SELECT * FROM users WHERE session_id = ?"
        return DatabaseManager.execute_query(query, (session_id,), fetchone=True)

    @staticmethod
    def create_user(username, password):
        """Creates a new user with a generated key pair and session ID."""
        if UserManager.get_user_by_username(username):
            return {"error": "Username already exists"}, 400

        sk, pk = get_sk_pk_pair()
        session_id = UserManager.create_session()

        query = "INSERT INTO users (username, password, pk, sk, session_id) VALUES (?, ?, ?, ?, ?)"
        if DatabaseManager.execute_query(query, (username, password, pk, sk, session_id)):
            logger.info(f"User {username} registered successfully.")
            return {"message": "Registration successful", "session_id": session_id}, 201
        else:
            return {"error": "Registration failed"}, 500

    @staticmethod
    def authenticate_user(username, password):
        """Verifies login credentials and returns a session ID."""
        user = UserManager.get_user_by_username(username)
        if not user or user["password"] != password:
            return {"error": "Invalid username or password"}, 401

        session_id = UserManager.create_session()
        query = "UPDATE users SET session_id = ? WHERE username = ?"
        if DatabaseManager.execute_query(query, (session_id, username)):
            logger.info(f"User {username} logged in successfully.")
            return {"message": "Login successful", "session_id": session_id}, 200
        else:
            return {"error": "Login failed"}, 500

    @staticmethod
    def logout_user(session_id):
        """Clears the session ID for logout."""
        query = "UPDATE users SET session_id = NULL WHERE session_id = ?"
        if DatabaseManager.execute_query(query, (session_id,)):
            logger.info(f"User logged out successfully. Session ID: {session_id}")
            return {"message": "Logout successful"}, 200
        else:
            return {"error": "Logout failed"}, 500

    @staticmethod
    def create_user_instance(user_row):
        """Creates a User instance from database row."""
        ip = "127.0.0.1"
        pk = user_row["pk"]
        sk = user_row["sk"]
        return User(pk, sk, ip=ip)
