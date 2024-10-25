import hashlib


class Transaction:
    def __init__(self, sender_id, recipient_id, amount):
        self.sender_id = sender_id  # Unique ID for the sender (acting as a public key)
        self.recipient_id = recipient_id  # Unique ID for the recipient
        self.amount = amount  # Amount of currency being sent
        self.signature = None  # Placeholder for a "digital signature"

    def calculate_hash(self):
        """
        Calculate a simple SHA-256 hash of the transaction contents.
        """
        data = f"{self.sender_id}{self.recipient_id}{self.amount}"
        return hashlib.sha256(data.encode()).hexdigest()

    def sign_transaction(self, private_key):
        """
        Sign the transaction using a simulated 'private key' (for demonstration only).
        Here, we simply hash the transaction data with a 'private key' string.
        """
        if not private_key:
            raise ValueError("Private key is required for signing a transaction.")

        # Simple signature simulation using hash (for educational purposes)
        hash_value = self.calculate_hash()
        self.signature = hashlib.sha256((hash_value + private_key).encode()).hexdigest()

    def verify_signature(self, public_key):
        """
        Verify the transaction's "signature" using the public key.
        """
        if not self.signature:
            raise ValueError("No signature in this transaction.")

        # Recalculate the hash with the public key and compare
        expected_signature = hashlib.sha256((self.calculate_hash() + public_key).encode()).hexdigest()
        return expected_signature == self.signature
