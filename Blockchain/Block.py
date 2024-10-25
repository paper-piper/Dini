import hashlib
import time
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
        :param transactions: A list of transactions included in this block.
        :param timestamp: The time when the block is created, defaults to current time.
        """
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.nonce = 0
        self.hash = self.calculate_hash()
        logger.info("Block created with previous hash: %s, transactions: %s", previous_hash, transactions)

    def calculate_hash(self):
        """
        Calculate an SHA-256 hash based on the block contents.

        :return: A string representing the hash of the block.
        """
        data = f"{self.previous_hash}{self.transactions}{self.timestamp}{self.nonce}"
        block_hash = hashlib.sha256(data.encode()).hexdigest()
        logger.debug("Block hash calculated: %s", block_hash)
        return block_hash

    def mine_block(self, difficulty):
        """
        Perform Proof of Work by finding a hash that meets the difficulty target.

        :param difficulty: The number of leading zeros required in the hash.
        :return: None
        """
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        logger.info("Block mined successfully. Nonce: %d, Hash: %s", self.nonce, self.hash)


def assertion_check():
    """
    Performs various assertions to verify the functionality of the Block class.

    :return: None
    """
    # Create a test block
    test_block = Block("0" * 64, ["transaction1", "transaction2"])

    # Verify the hash calculation
    initial_hash = test_block.calculate_hash()
    assert test_block.hash == initial_hash, HASH_VALIDATION_ERROR

    # Verify that mining works correctly
    difficulty = 2  # Set a small difficulty for testing purposes
    test_block.mine_block(difficulty)
    assert test_block.hash[:difficulty] == "0" * difficulty, MINE_SUCCESS_ERROR
    assert test_block.nonce > 0, NONCE_INCREMENT_ERROR

    logger.info("All assertions passed for Block class.")


if __name__ == "__main__":
    assertion_check()
