import uuid
from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from network.user import User
from core.transaction import get_sk_pk_pair
from utils.logging_utils import setup_basic_logger
from database_manager import DatabaseManager
from cryptography.hazmat.primitives import serialization

logger = setup_basic_logger()
logger.info("UserManager initializing")


class UserManager:
    """Manages user authentication and cryptocurrency operations."""
    # Global registry of user objects (keyed by username)
    all_users = {}

    @classmethod
    def initialize_users(cls):
        """Initializes all user instances from the database."""
        query = "SELECT * FROM users"
        user_rows = DatabaseManager.execute_query(query, fetchall=True)
        if user_rows:
            for row in user_rows:
                username = row["username"]
                user_instance = cls.create_user_instance(row)
                cls.all_users[username] = user_instance
            logger.info(f"Initialized users: {', '.join(cls.all_users.keys())}")
        else:
            logger.info("No users found in database to initialize.")

    @staticmethod
    def handle_transactions(session_id, method, request_data=None):
        """Handles fetching or creating transactions for an authenticated user."""
        from user_session_manager import UserSessionManager

        # Try to fetch the active user from the session manager first.
        user_instance = UserSessionManager.get_instance().get_user(session_id)

        # If not active, look up the session in the database and get from the global registry.
        if not user_instance:
            user_row = UserManager.get_user_by_session(session_id)
            if not user_row:
                logger.warning("Invalid session ID in transaction request")
                return {"error": "Invalid session"}, 401
            username = user_row["username"]
            user_instance = UserManager.all_users.get(username)
            if not user_instance:
                user_instance = UserManager.create_user_instance(user_row)
                UserManager.all_users[username] = user_instance
            UserSessionManager.get_instance().add_user(session_id, user_instance)

        if method == "GET":
            try:
                actions = user_instance.get_recent_transactions(-1)
                response = [
                    {
                        "id": str(action.id)[:10],
                        "type": action.type,
                        "amount": action.amount,
                        "status": action.status,
                        "timestamp": action.timestamp,
                        "details": action.details or "",
                    }
                    for action in actions
                ]
                logger.info(f"Successfully fetched {len(response)} transactions.")
                return response, 200
            except Exception as e:
                logger.error(f"Error while retrieving transactions: {e}")
                return {"error": f"Internal server error - {e}"}, 500

        elif method == "POST":
            try:
                action_type = request_data.get("type")
                amount = request_data.get("amount", 0)
                details = request_data.get("details", "")
                status = request_data.get("status", "pending")

                if action_type not in ["buy", "sell", "transfer"]:
                    raise ValueError("Invalid transaction type")
                if amount <= 0:
                    raise ValueError("Invalid amount")

                if action_type == "buy":
                    action_id = user_instance.buy_dinis(amount)
                elif action_type == "sell":
                    action_id = user_instance.sell_dinis(amount)
                else:  # transfer
                    action_id = user_instance.add_transaction(details, amount)

                action_data = {
                    "id": str(action_id),
                    "type": action_type,
                    "amount": amount,
                    "status": status,
                    "timestamp": str(datetime.now()),
                    "details": details,
                }

                logger.info(f"Transaction created: {action_data}")
                return action_data, 201
            except ValueError as ve:
                logger.warning(f"Invalid transaction data: {ve}")
                return {"error": str(ve)}, 400
            except Exception as e:
                logger.error(f"Error processing transaction creation: {e}")
                return {"error": f"Internal server error - {e}"}, 500

    @staticmethod
    def create_session():
        """Generates a new session ID using UUID."""
        return str(uuid.uuid4())

    @staticmethod
    def get_user_by_username(username):
        """Retrieves a user row by username."""
        logger.info(f"Fetching user: {username}")
        query = "SELECT * FROM users WHERE username = ?"
        return DatabaseManager.execute_query(query, (username,), fetchone=True)

    @staticmethod
    def get_user_by_session(session_id):
        """Retrieves a user row by session ID."""
        logger.info(f"Fetching user with session: {session_id}")
        query = "SELECT * FROM users WHERE session_id = ?"
        return DatabaseManager.execute_query(query, (session_id,), fetchone=True)

    @staticmethod
    def create_user(username, password):
        """Creates a new user with a generated key pair and session ID."""
        if UserManager.get_user_by_username(username):
            logger.warning(f"Username {username} already exists.")
            return {"error": "Username already exists"}, 400

        sk, pk = get_sk_pk_pair()
        # Convert private key to PEM format string
        sk_pem = sk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()

        # Convert public key to PEM format string
        pk_pem = pk.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        session_id = UserManager.create_session()

        query = "INSERT INTO users (username, password, pk, sk, session_id) VALUES (?, ?, ?, ?, ?)"
        if DatabaseManager.execute_query(query, (username, password, pk_pem, sk_pem, session_id)):
            logger.info(f"User {username} registered successfully.")
            # Retrieve the inserted row and create a user instance.
            user_row = UserManager.get_user_by_username(username)
            if user_row:
                user_instance = UserManager.create_user_instance(user_row)
                UserManager.all_users[username] = user_instance
            return {"message": "Registration successful", "session_id": session_id}, 201
        else:
            logger.error("Database insert failed during registration.")
            return {"error": "Registration failed"}, 500

    @staticmethod
    def authenticate_user(username, password):
        """Verifies login credentials and returns a session ID."""
        user = UserManager.get_user_by_username(username)
        if not user or user["password"] != password:
            logger.warning("Invalid login attempt.")
            return {"error": "Invalid username or password"}, 401

        session_id = UserManager.create_session()
        query = "UPDATE users SET session_id = ? WHERE username = ?"
        if DatabaseManager.execute_query(query, (session_id, username)):
            logger.info(f"User {username} logged in successfully.")
            return {"message": "Login successful", "session_id": session_id}, 200
        else:
            logger.error("Database update failed during login.")
            return {"error": "Login failed"}, 500

    @staticmethod
    def logout_user(session_id):
        """Clears the session ID for logout."""
        query = "UPDATE users SET session_id = NULL WHERE session_id = ?"
        if DatabaseManager.execute_query(query, (session_id,)):
            logger.info(f"User logged out successfully. Session ID: {session_id}")
            return {"message": "Logout successful"}, 200
        else:
            logger.error("Database update failed during logout.")
            return {"error": "Logout failed"}, 500

    @staticmethod
    def create_user_instance(user_row):
        """Creates a User instance from database row."""
        ip = "127.0.0.1"
        pk_pem = user_row["pk"]
        sk_pem = user_row["sk"]
        username = user_row["username"]
        # Convert PEM back to key objects
        pk = load_pem_public_key(pk_pem.encode(), backend=default_backend())
        sk = load_pem_private_key(sk_pem.encode(), password=None, backend=default_backend())
        return User(pk, sk, ip=ip, name=username)

    def cleanup(self):
        """Cleanup user resources before removing the instance."""
        if hasattr(self, 'blockchain_node'):
            self.blockchain_node.close()
        self.nodes_names_addresses = {}
