from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import time
import random
from threading import Thread
from network.user import User
from core.transaction import get_sk_pk_pair

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for all routes

# Assume the `User` class is fully implemented with methods like:
# add_transaction, update_transaction_status, get_transaction, list_all_transactions, etc.

# Create a mock user instance
sk, pk = get_sk_pk_pair()
user = User(pk, sk)  # Assume `User` is already implemented


def process_transaction_in_background(txn_id):
    """Simulate a time-consuming transaction, then set 'approved' or 'failed'."""
    time.sleep(5)  # Simulate some delay (e.g., mining, external approval)
    final_status = "failed" if random.randint(1, 5) == 2 else "approved"
    user.update_transaction_status(txn_id, final_status)


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
        transactions = user.get_recent_transactions(-1)  # get all transactions
        # Convert the transactions to a list (if they aren't already)
        response = [
            {
                "id": str(transaction.signature)[:10],
                "type": txn_data["type"],
                "amount": txn_data["amount"],
                "status": txn_data["status"],
                "timestamp": txn_data["timestamp"],
                "details": txn_data.get("details", ""),
            }
            for transaction, timestamp in transactions.items()
        ]
        return jsonify(response), 200

    if request.method == "POST":
        data = request.get_json()
        # Validate the required fields
        txn_type = data.get("type")
        amount = data.get("amount", 0)
        details = data.get("details", "")
        status = data.get("status", "pending")

        if txn_type not in ["buy", "sell", "transfer", "mine"]:
            return jsonify({"error": "Invalid transaction type"}), 400

        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        # Generate a unique transaction ID
        txn_id = str(uuid.uuid4())

        # Build the transaction object
        txn_data = {
            "type": txn_type,
            "amount": amount,
            "status": status,
            "timestamp": time.time(),
            "details": details,
        }

        # Add the transaction using the User class
        user.add_transaction(txn_id, txn_data)

        # Process the transaction asynchronously (e.g., mining, approvals)
        Thread(target=process_transaction_in_background, args=(txn_id,)).start()

        # Respond with the created transaction
        new_tx_response = {
            "id": txn_id,
            "type": txn_type,
            "amount": amount,
            "status": status,
            "timestamp": txn_data["timestamp"],
            "details": details,
        }
        return jsonify(new_tx_response), 201


if __name__ == "__main__":
    # Run the Flask server on port 8000
    print("Starting backend!")
    app.run(debug=True, port=8000)