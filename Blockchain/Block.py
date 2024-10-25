import hashlib
import time


class Block:
    def __init__(self, previous_hash, transactions, timestamp=None):
        self.previous_hash = previous_hash    # Hash of the previous block in the chain
        self.transactions = transactions      # List of transactions in the block
        self.timestamp = timestamp or time.time()  # Block timestamp
        self.nonce = 0                        # Nonce for Proof of Work
        self.hash = self.calculate_hash()     # Current block hash based on contents

    def calculate_hash(self):
        """
        Calculate an SHA-256 hash based on block contents.
        """
        data = f"{self.previous_hash}{self.transactions}{self.timestamp}{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()

    def mine_block(self, difficulty):
        """
        Perform Proof of Work by finding a hash that starts with a certain number of zeros.
        """
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined! Nonce: {self.nonce}, Hash: {self.hash}")

