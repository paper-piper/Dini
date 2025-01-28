from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from network.user import User
from core.transaction import get_sk_pk_pair
from utils.config import ActionSettings, ActionType
from utils.logging_utils import setup_basic_logger
logger = setup_basic_logger()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Allow requests from localhost:3000

# Assume the `User` class is fully implemented with methods like:
# add_transaction, update_transaction_status, get_transaction, list_all_transactions, etc.

# Create a mock user instance
ip = "127.0.0.1"
sk, pk = get_sk_pk_pair()
user = User(pk, sk, ip=ip)  # Assume `User` is already implemented


@app.route("/connected-users", methods=["GET"])
def get_connected_users():
    """
    Returns the list of connected user names (dictionary keys).
    """
    try:
        connected_user_names = list(user.nodes_names_addresses.keys())
        return jsonify(connected_user_names), 200
    except Exception as e:
        logger.error(f"Error getting connected users: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/transactions", methods=["GET", "POST", "OPTIONS"])
def handle_transactions():
    """
    Handles:
    - GET /transactions: Lists all transactions
    - POST /transactions: Creates a new transaction
    - OPTIONS /transactions: Handles CORS preflight
    """
    logger.info(f"Received {request.method} request at /transactions",)

    if request.method == "OPTIONS":
        logger.debug("Handling CORS preflight request.")
        # Let Flask-CORS handle the preflight request automatically
        return jsonify(success=True), 200

    if request.method == "GET":
        logger.info("Processing GET request for all transactions.")
        try:

            # Use the User class's method to retrieve all transactions
            actions = user.get_recent_transactions(-1)  # get all transactions
            logger.debug(f"Fetched {len(actions)} transactions")

            # Convert the transactions to a list (if they aren't already)
            response = [
                {
                    "id": str(action.id)[:ActionSettings.ID_LENGTH],
                    "type": action.type,
                    "amount": action.amount,
                    "status": action.status,
                    "timestamp": action.timestamp,
                    "details": action.details or "",
                }
                for action in actions
            ]
            logger.info(f"Successfully processed GET request with {len(response)} transactions")
            return jsonify(response), 200
        except Exception as e:
            logger.error(f"Error processing GET request: {e}")
            return jsonify({"error": "Internal server error"}), 500

    if request.method == "POST":
        data = request.get_json()
        logger.info("Processing POST request with data: %s", data)

        # Validate the required fields
        action_type = data.get("type")
        amount = data.get("amount", 0)
        details = data.get("details", "")
        status = data.get("status", "pending")

        if action_type not in ActionType.__dict__.values():
            logger.error("Invalid transaction type received: %s", action_type)
            return jsonify({"error": "Invalid transaction type"}), 400

        if amount <= 0:
            logger.error("Invalid amount received: %s", amount)
            return jsonify({"error": "Invalid amount"}), 400

        try:
            # post the transaction based on type
            if action_type == ActionType.BUY:
                logger.info("Initiating BUY transaction for amount: %s", amount)
                action_id = user.buy_dinis(amount)
            elif action_type == ActionType.SELL:
                logger.info("Initiating SELL transaction for amount: %s", amount)
                action_id = user.sell_dinis(amount)
            else:  # action_type == ActionType.TRANSFER
                logger.info("Initiating TRANSFER transaction with details: %s and amount: %s", details, amount)
                action_id = user.add_transaction(details, amount)

            action_id = str(action_id)
            logger.debug("Transaction created with ID: %s", action_id)

            # Build the transaction object
            action_data = {
                "type": action_type,
                "amount": amount,
                "status": status,
                "timestamp": datetime.now(),
                "details": details,
            }

            # Respond with the created transaction
            new_tx_response = {
                "id": action_id,
                "type": action_type,
                "amount": amount,
                "status": status,
                "timestamp": action_data["timestamp"],
                "details": details,
            }
            logger.info(f"Successfully created transaction: {new_tx_response}")
            return jsonify(new_tx_response), 201
        except Exception as e:
            logger.error(f"Error processing POST request: {e}")
            return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logger.info("Starting backend server on port 8000!")
    app.run(debug=True, port=8000)
