import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
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
    Represents a transaction in the cryptocurrency network, with a sender, recipient,
    amount, and a digital signature for validation using an actual PK-SK system.
    """

    def __init__(self, sender_pk, recipient_pk, amount):
        """
        Initialize a Transaction instance with the sender's and recipient's public keys and the amount.
        :param sender_pk: RSA public key object representing the sender's public key.
        :param recipient_pk: RSA public key object representing the recipient's public key.
        :param amount: The amount of currency to be transferred.
        """
        self.sender_pk = sender_pk
        self.recipient_pk = recipient_pk
        self.amount = amount
        self.signature = None
        logger.info("Transaction created: Sender: %s, Recipient: %s, Amount: %s",
                    str(self.sender_pk.public_numbers().n)[:3] + "...",
                    str(self.recipient_pk.public_numbers().n)[:3] + "...",
                    self.amount)

    def __repr__(self):
        """
        Provide a readable string representation of the transaction for debugging.
        :return: A string representation of the transaction, including sender, recipient, and amount.
        """
        sender_id = str(self.sender_pk.public_numbers().n)[:3]
        recipient_id = str(self.recipient_pk.public_numbers().n)[:3]
        return f"Transaction(Sender: {sender_id}..., Recipient: {recipient_id}..., Amount: {self.amount})"

    def calculate_hash(self):
        """
        Calculate a SHA-256 hash of the transaction contents.

        :return: Hash string representing the transaction.
        """
        data = f"{self.sender_pk.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)}" \
               f"{self.recipient_pk.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)}" \
               f"{self.amount}"
        transaction_hash = hashlib.sha256(data.encode()).hexdigest()
        logger.debug("Transaction hash calculated: %s", transaction_hash[:5] + "...")
        return transaction_hash

    def sign_transaction(self, private_key):
        """
        Sign the transaction using the sender's private key.

        :param private_key: RSA private key object representing the sender's private key.
        :return: None
        """
        if not private_key:
            logger.error("Failed to sign transaction: Missing private key.")
            raise ValueError("Private key is required for signing a transaction.")

        # Calculate hash and sign it
        hash_value = self.calculate_hash().encode()
        self.signature = private_key.sign(
            hash_value,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        logger.info("Transaction signed. Signature: %s", str(self.signature)[:5] + "...")

    def verify_signature(self):
        """
        Verify the transaction's signature using the sender's public key.

        :return: True if the signature is valid, False otherwise.
        """
        if not self.signature:
            logger.error("Verification failed: No signature present in transaction.")
            raise ValueError("No signature in this transaction.")

        hash_value = self.calculate_hash().encode()
        try:
            self.sender_pk.verify(
                self.signature,
                hash_value,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            logger.debug("Signature verification succeeded")
            return True
        except InvalidSignature:
            logger.debug("Signature verification failed")
            return False


def get_sk_pk_pair():
    ps = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return ps, ps.public_key()


def assertion_check():
    """
    Performs various assertions to verify the functionality of the Transaction class using actual PK-SK signing.
    :return: None
    """
    logger.info("Starting assertions check for Transaction class...")

    # Generate a test private and public key for signing and verification
    sender_private_key, sender_public_key = get_sk_pk_pair()
    _, recipient_public_key = get_sk_pk_pair()

    # Create a test transaction
    transaction = Transaction(sender_public_key, recipient_public_key, 10)

    # Calculate hash and verify expected hash structure
    assert len(transaction.calculate_hash()) == 64, HASH_LENGTH_ERROR

    # Sign transaction and verify signature is created
    transaction.sign_transaction(sender_private_key)
    assert transaction.signature is not None, SIGNATURE_CREATION_ERROR

    # Verify the signature - should return True with correct public key
    assert transaction.verify_signature(), VERIFICATION_SUCCESS_ERROR

    # Modify the amount and check that verification fails
    transaction.amount = 20
    assert not transaction.verify_signature(), VERIFICATION_FAIL_ERROR

    logger.info("All assertions passed for Transaction class.")


if __name__ == "__main__":
    assertion_check()
