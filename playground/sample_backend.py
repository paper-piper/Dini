from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import time
import random
from threading import Thread

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for all routes


class User:
    def __init__(self, user_id, wallet_balance=1000):
        self.user_id = user_id
        self.wallet_balance = wallet_balance
        # Store transactions in a dict { txn_id: {...transaction data...} }
        self.transactions = {}

    def add_transaction(self, txn_id, txn_data):
        """
        txn_data is a dict like:
        {
          "type": "buy" | "sell" | "transfer",
          "amount": number,
          "status": "pending",
          "timestamp": ...,
          "details": ...
        }
        """
        self.transactions[txn_id] = txn_data

    def update_transaction_status(self, txn_id, new_status):
        """Update the status of a transaction by ID."""
        if txn_id in self.transactions:
            self.transactions[txn_id]["status"] = new_status


# Create a mock user
user = User(user_id="123", wallet_balance=1000)


def process_transaction_in_background(txn_id):
    """Simulate a time-consuming transaction, then set 'approved' or 'failed'."""
    time.sleep(5)  # Wait 5 seconds
    # Randomly mark as approved or failed
    num = random.randint(1,5)
    final_status = "failed" if num == 2 else "approved"
    user.update_transaction_status(txn_id, final_status)


@app.route("/transactions", methods=["GET", "POST", "OPTIONS"])
def handle_transactions():
    """Handles both listing all transactions (GET) and creating a new one (POST)."""
    if request.method == "OPTIONS":
        # Let Flask-CORS handle the preflight automatically
        return jsonify(success=True), 200

    if request.method == "GET":
        # Return all known transactions as a list
        all_txs = []
        for txn_id, data in user.transactions.items():
            # Merge the transaction ID in the response
            tx_response = {
                "id": txn_id,
                "type": data["type"],
                "amount": data["amount"],
                "status": data["status"],
                "timestamp": data["timestamp"],
                "details": data.get("details", ""),  # details might be optional
            }
            all_txs.append(tx_response)
        return jsonify(all_txs), 200

    if request.method == "POST":
        data = request.get_json()
        # data should contain: type, amount, details (optional), status
        # For safety, do some quick validation
        txn_type = data.get("type")
        amount = data.get("amount", 0)
        details = data.get("details", "")
        status = data.get("status", "pending")

        # Basic validation
        if txn_type not in ["buy", "sell", "transfer", "mine"]:
            return jsonify({"error": "Invalid transaction type"}), 400

        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400
        if status not in ["pending"]:
            # The frontend is currently sending "pending", but let's not break if it doesn't
            return jsonify({"error": "Invalid status"}), 400

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

        # Add to the user's transactions
        user.add_transaction(txn_id, txn_data)

        # Process asynchronously to simulate time passing
        Thread(target=process_transaction_in_background, args=(txn_id,)).start()

        # Return the newly created transaction data back
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
    # The React frontend points to http://localhost:8000/transactions
    # so let's run Flask on port 8000
    print("Starting backend!")
    app.run(debug=True, port=8000)
