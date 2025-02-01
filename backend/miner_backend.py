from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from network.miner.miner import Miner
from core.transaction import get_sk_pk_pair
from utils.config import ActionSettings, ActionType
from utils.logging_utils import setup_basic_logger

logger = setup_basic_logger()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Create User instance
ip = "127.0.0.1"
sk, pk = get_sk_pk_pair()
miner_port = 8003
miner = Miner(pk, sk, ip=ip, port=miner_port)


def fetch_connected_users(user_instance):
    """
    Fetch the list of connected usernames from the User instance.
    """
    try:
        logger.debug("Fetching connected user names.")
        return list(user_instance.nodes_names_addresses.keys())
    except Exception as e:
        logger.error(f"Error while fetching connected users: {e}")
        # Re-raise so that the caller can handle this exception
        raise


def handle_get_all_transactions(user_instance):
    """
    Retrieve all recent transactions from the user instance.
    Returns a list of dictionaries representing each transaction.
    """
    try:
        logger.debug("Retrieving all transactions.")
        actions = user_instance.get_recent_transactions(-1)  # get all transactions
        logger.debug(f"Fetched {len(actions)} transactions from user.")
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
        return response
    except Exception as e:
        logger.error(f"Error while retrieving transactions: {e}")
        raise


def handle_create_transaction(user_instance, data):
    """
    Create a new transaction (BUY, SELL, or TRANSFER) based on the provided data.
    Returns a dictionary with the newly created transaction details.
    """
    action_type = data.get("type")
    amount = data.get("amount", 0)
    details = data.get("details", "")
    status = data.get("status", "pending")

    logger.info("Processing POST request with data: %s", data)

    # Validate the required fields
    if action_type not in ActionType.__dict__.values():
        logger.error("Invalid transaction type received: %s", action_type)
        raise ValueError("Invalid transaction type")

    if amount <= 0:
        logger.error("Invalid amount received: %s", amount)
        raise ValueError("Invalid amount")

    try:
        logger.debug("Creating transaction of type '%s' for amount '%s'", action_type, amount)
        if action_type == ActionType.BUY:
            action_id = user_instance.buy_dinis(amount)
        elif action_type == ActionType.SELL:
            action_id = user_instance.sell_dinis(amount)
        else:  # ActionType.TRANSFER
            action_id = user_instance.add_transaction(details, amount)

        action_id = str(action_id)
        logger.debug("Transaction successfully created with ID: %s", action_id)

        # Build the transaction object to return
        action_data = {
            "id": action_id,
            "type": action_type,
            "amount": amount,
            "status": status,
            "timestamp": datetime.now(),
            "details": details,
        }
        return action_data
    except Exception as e:
        logger.error(f"Error processing transaction creation: {e}")
        raise


@app.route("/connected-users", methods=["GET"])
def get_connected_users():
    """
    Returns the list of connected usernames (dictionary keys).
    """
    try:
        connected_user_names = fetch_connected_users(miner)
        return jsonify(connected_user_names), 200
    except Exception as e:
        # Error already logged in helper function
        return jsonify({"error": f"Internal server error - {e}"}), 500


@app.route("/transactions", methods=["GET", "POST", "OPTIONS"])
def handle_transactions():
    """
    Handles:
    - GET /transactions: Lists all transactions
    - POST /transactions: Creates a new transaction
    - OPTIONS /transactions: Handles CORS preflight
    """
    logger.info(f"Received {request.method} request at /transactions")

    if request.method == "OPTIONS":
        logger.debug("Handling CORS preflight request.")
        return jsonify({"success": True}), 200

    elif request.method == "GET":
        logger.info("Processing GET request for all transactions.")
        try:
            transactions = handle_get_all_transactions(miner)
            logger.info(f"Successfully fetched {len(transactions)} transactions.")
            return jsonify(transactions), 200
        except Exception as e:
            return jsonify({"error": f"Internal server error - {e}"}), 500

    elif request.method == "POST":
        try:
            data = request.get_json(force=True)
            new_transaction = handle_create_transaction(miner, data)
            logger.info(f"Transaction created: {new_transaction}")
            return jsonify(new_transaction), 201
        except ValueError as val_err:
            # Handle known invalid input errors
            logger.warning(f"Invalid transaction data: {val_err}")
            return jsonify({"error": str(val_err)}), 400
        except Exception as e:
            return jsonify({"error": f"Internal server error - {e}"}), 500


if __name__ == "__main__":
    logger.info("Starting backend server on port 8000!")
    app.run(debug=True, port=8000)
