import hashlib
from logging_utils import setup_logger

# Setup logger for file
logger = setup_logger("transaction_module")

# Constants for assertion error messages
HASH_LENGTH_ERROR = "Hash length should be 64 characters"
SIGNATURE_CREATION_ERROR = "Signature should be created after signing"
VERIFICATION_SUCCESS_ERROR = "Verification should succeed with correct public key"
VERIFICATION_FAIL_ERROR = "Verification should fail with incorrect public key"


class Transaction:
    """
    Represents a single transaction in the cryptocurrency network. Each transaction includes the sender's
    and recipient's identifiers, the transaction amount, and an optional signature to ensure authenticity.
    """

    def __init__(self, sender_id, recipient_id, amount):
        """
        Initialize a Transaction instance with sender ID, recipient ID, and amount.

        :param sender_id: Unique ID for the sender, simulating a public key.
        :param recipient_id: Unique ID for the recipient.
        :param amount: The amount of currency to be transferred.
        """
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.amount = amount
        self.signature = None
        logger.info("Transaction created: %s -> %s : %s", sender_id, recipient_id, amount)

    def calculate_hash(self):
        """
        Calculate a SHA-256 hash of the transaction details, acting as a unique identifier.

        :return: Hash string representing the transaction.
        """
        data = f"{self.sender_id}{self.recipient_id}{self.amount}"
        transaction_hash = hashlib.sha256(data.encode()).hexdigest()
        logger.debug("Transaction hash calculated: %s", transaction_hash)
        return transaction_hash

    def sign_transaction(self, private_key):
        """
        Simulates signing the transaction using a private key by hashing the transaction with the key.

        :param private_key: String representing the sender's private key.
        :return: None
        """
        if not private_key:
            logger.error("Failed to sign transaction: Missing private key.")
            raise ValueError("Private key is required for signing a transaction.")

        hash_value = self.calculate_hash()
        self.signature = hashlib.sha256((hash_value + private_key).encode()).hexdigest()
        logger.info("Transaction signed. Signature: %s", self.signature)

    def verify_signature(self, public_key):
        """
        Verifies the transaction signature against the provided public key.

        :param public_key: Public key string to verify the transaction.
        :return: True if the signature matches the transaction and public key; otherwise, False.
        """
        if not self.signature:
            logger.error("Verification failed: No signature present in transaction.")
            raise ValueError("No signature in this transaction.")

        expected_signature = hashlib.sha256((self.calculate_hash() + public_key).encode()).hexdigest()
        is_valid = expected_signature == self.signature
        logger.debug("Signature verification %s", "succeeded" if is_valid else "failed")
        return is_valid


def assertion_check():
    """
    Performs various assertions to verify the functionality of the Transaction class.

    :return: None
    """
    # Create a test transaction
    transaction = Transaction("Alice", "Bob", 10)

    # Calculate hash and verify expected hash structure (length)
    assert len(transaction.calculate_hash()) == 64, HASH_LENGTH_ERROR

    # Sign transaction and verify signature is created
    transaction.sign_transaction("alice_private_key")
    assert transaction.signature is not None, SIGNATURE_CREATION_ERROR

    # Verify the signature - should return True with correct 'public key'
    assert transaction.verify_signature("alice_private_key"), VERIFICATION_SUCCESS_ERROR

    # Attempt verification with incorrect public key - should return False
    assert not transaction.verify_signature("wrong_key"), VERIFICATION_FAIL_ERROR

    logger.info("All assertions passed.")


if __name__ == "__main__":
    assertion_check()
