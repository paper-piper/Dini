from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from network.user import User
from core.transaction import get_sk_pk_pair
from utils.config import ActionSettings, ActionType

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for all routes

# Assume the `User` class is fully implemented with methods like:
# add_transaction, update_transaction_status, get_transaction, list_all_transactions, etc.

# Create a mock user instance
sk, pk = get_sk_pk_pair()
user = User(pk, sk)  # Assume `User` is already implemented


@app.route("/transactions", methods=["GET", "POST", "OPTIONS"])
def handle_transactions():
    """
    Handles:
    - GET /transactions: Lists all transactions
    - POST /transactions: Creates a new transaction
    - OPTIONS /transactions: Handles CORS preflight
    """
    if request.method == "OPTIONS":
        # Let Flask-CORS handle the preflight request automatically
        return jsonify(success=True), 200

    if request.method == "GET":
        # Use the User class's method to retrieve all transactions
        actions = user.get_recent_transactions(-1)  # get all transactions
        # Convert the transactions to a list (if they aren't already)
        response = [
            {
                "id": str(action.signature)[:ActionSettings.ID_LENGTH],
                "type": action.type,
                "amount": action.amount,
                "status": action.status,
                "timestamp": action.timestamp,
                "details": action.details or "",
            }
            for action, timestamp in actions.items()
        ]
        return jsonify(response), 200

    if request.method == "POST":
        data = request.get_json()
        # Validate the required fields
        action_type = data.get("type")
        amount = data.get("amount", 0)
        details = data.get("details", "")
        status = data.get("status", "pending")

        if action_type not in ActionType.__dict__.values():
            return jsonify({"error": "Invalid transaction type"}), 400

        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        # post the transaction
        if action_type == ActionType.BUY:
            action_id = user.buy_dinis(amount)
        elif action_type == ActionType.SELL:
            action_id = user.sell_dinis(amount)
        else:  # action_type == ActionType.TRANSFER:
            action_id = user.add_transaction(details, amount)

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
        return jsonify(new_tx_response), 201


if __name__ == "__main__":
    # Run the Flask server on port 8000
    print("Starting backend!")
    app.run(debug=True, port=8000)