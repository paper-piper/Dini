import hashlib
import time
from transaction import Transaction, get_sk_pk_pair
from logging_utils import setup_logger

# Setup logger for file
logger = setup_logger("block_module")

# Constants for assertion error messages
HASH_VALIDATION_ERROR = "Calculated hash should match the expected hash"
MINE_SUCCESS_ERROR = "Mined block hash should meet difficulty target"
NONCE_INCREMENT_ERROR = "Nonce should increment in the mining process"


class Block:
    """
    Represents a single block in the blockchain. Each block contains a list of transactions,
    a reference to the previous block's hash, a timestamp, a nonce for Proof of Work, and a hash.
    """

    def __init__(self, previous_hash, transactions, timestamp=None):
        """
        Initialize a Block instance with a previous block's hash, a list of transactions,
        and an optional timestamp.
        :param previous_hash: The hash of the previous block in the chain.
        :param transactions: A list of Transaction objects included in this block.
        :param timestamp: The time when the block is created, defaults to current time.
        """
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.nonce = 0
        self.hash = None  # Initially None to avoid confusion before mining
        logger.info("Block created with previous hash: %s, transactions: %s", previous_hash, transactions)

    def calculate_hash(self):
        """
        Calculate an SHA-256 hash based on the block contents.

        :return: A string representing the hash of the block.
        """
        # Serialize transactions to strings using repr
        serialized_transactions = ''.join(repr(tx) for tx in self.transactions)
        data = f"{self.previous_hash}{serialized_transactions}{self.timestamp}{self.nonce}"
        block_hash = hashlib.sha256(data.encode()).hexdigest()
        return block_hash

    def validate_transactions(self):
        """
        Validates each transaction in the block to ensure integrity.

        :return: True if all transactions are valid, False otherwise.
        """
        for transaction in self.transactions:
            if not transaction.verify_signature():
                logger.warning("Invalid transaction detected: %s", transaction)
                return False
        logger.info("All transactions validated successfully for block: %s", self)
        return True

    def __repr__(self):
        """
        Provides a readable string representation of the block.

        :return: A string representation of the block.
        """
        if len(self.transactions) < 5:
            transaction_reprs = ", ".join(repr(tx) for tx in self.transactions)
            return (f"Block(Previous Hash: {self.previous_hash[:6]}..., Hash: {self.hash[:6]}...,"
                    f" Nonce: {self.nonce}, Transactions: [{transaction_reprs}])")
        else:
            return (f"Block(Previous Hash: {self.previous_hash[:6]}..., Hash: {self.hash[:6]}...,"
                    f" Nonce: {self.nonce}, Transactions: {len(self.transactions)})")


def assertion_check():
    """
    Performs various assertions to verify the functionality of the Block class using Transaction objects.
    :return: None
    """
    logger.info("Starting assertions check for Block class...")

    # Create sample Transaction objects
    sender_private_key, sender_public_key = get_sk_pk_pair()
    _, recipient_public_key = get_sk_pk_pair()

    transaction1 = Transaction(sender_public_key, recipient_public_key, 10)
    transaction1.sign_transaction(sender_private_key)

    transaction2 = Transaction(sender_public_key, recipient_public_key, 20)
    transaction2.sign_transaction(sender_private_key)

    # Create a test block with transactions
    test_block = Block("0" * 64, [transaction1, transaction2])

    # Verify the hash calculation before mining
    initial_hash = test_block.calculate_hash()
    assert test_block.hash is None, HASH_VALIDATION_ERROR  # Ensure no hash is set initially
    assert initial_hash == test_block.calculate_hash(), HASH_VALIDATION_ERROR

    logger.info("All assertions passed for Block class.")


if __name__ == "__main__":
    assertion_check()
