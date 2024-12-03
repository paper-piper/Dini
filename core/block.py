import hashlib
import time
from core.transaction import Transaction, create_sample_transaction, get_sk_pk_pair
from utils.logging_utils import setup_logger
from utils.config import MinerSettings, BlockSettings

# Setup logger for file
logger = setup_logger()

# Constants for assertion error messages
HASH_VALIDATION_ERROR = "Calculated hash should match the expected hash"
MINE_SUCCESS_ERROR = "Mined block hash should meet difficulty target"
NONCE_INCREMENT_ERROR = "Nonce should increment in the mining process"


class Block:
    """
    Represents a single block in the blockchain. Each block contains a list of transactions,
    a reference to the previous block's hash, a timestamp, a nonce for Proof of Work, and a hash.
    """

    def __init__(
            self,
            previous_hash,
            transactions,
            difficulty=MinerSettings.DIFFICULTY_LEVEL,
            timestamp=None,
            nonce=0,
            block_hash=None
    ):
        """
        Initialize a Block instance with a previous block's hash, a list of transactions,
        and an optional timestamp.
        :param previous_hash: The hash of the previous block in the chain.
        :param transactions: A list of Transaction objects included in this block.
        :param timestamp: The time when the block is created, defaults to current time.
        """
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.difficulty = difficulty
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.hash = block_hash  # Initially None to avoid confusion before mining
        logger.info("Block created with previous hash: %s, transactions: %s", previous_hash, transactions)

    def to_dict(self):
        return {
            "previous_hash": self.previous_hash,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "difficulty": self.difficulty,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data):
        transactions = [Transaction.from_dict(tx_data) for tx_data in data["transactions"]]
        return cls(
            previous_hash=data["previous_hash"],
            transactions=transactions,
            difficulty=data["difficulty"],
            timestamp=data["timestamp"],
            nonce=data["nonce"],
            block_hash=data["hash"],
        )

    def __repr__(self):
        """
        Provides a readable string representation of the block.

        :return: A string representation of the block.
        """
        transaction_reprs = ", ".join(repr(tx) for tx in self.transactions)
        str_value = (f"Block(Previous Hash: {self.previous_hash[:6] if self.previous_hash else 'None'}..., "
                     f"Hash: {self.hash[:6]}..., "
                     f"Nonce: {self.nonce}, "
                     f"Difficulty: {self.difficulty}, "
                     f"Transactions: [{transaction_reprs if len(self.transactions) < 5 else len(self.transactions)}])")
        return str_value

    def calculate_hash(self):
        """
        Calculate an SHA-256 hash based on the block contents.

        :return: A string representing the hash of the block.
        """
        # Serialize transactions to strings using repr
        serialized_transactions = ''.join(repr(tx) for tx in self.transactions)
        data = f"{self.previous_hash}{serialized_transactions}{self.difficulty}{self.timestamp}{self.nonce}"
        block_hash = hashlib.sha256(data.encode()).hexdigest()
        return block_hash

    def validate_block(self):
        """
        Validates each transaction in the block to ensure integrity.

        :return: True if all transactions are valid, False otherwise.
        """
        # skip the first transaction, since it is not signed
        tips_sum = 0
        for transaction in self.transactions[1:]:
            if transaction.amount <= 0:
                logger.warning(f"Invalid transaction amount ({transaction.amount}) in transaction: {transaction}")
                return False
            if not transaction.verify_signature():
                logger.warning("Invalid transaction detected: %s", transaction)
                return False
            tips_sum += transaction.tip

        # ensure the tips sum match the actual first transaction
        if tips_sum != self.transactions[0].amount:
            logger.warning(f"sum of tips does not match the tipping transaction."
                           f" tips sum: {self.transactions[0].amount}. actual amount: {tips_sum}")
            return False

        # TODO: check for one bonus transaction
        logger.info("All transactions validated successfully for block: %s", self)
        return True

    def add_tipping_transaction(self, public_key):
        tips_sum = 0
        for transaction in self.transactions:
            tips_sum += transaction.tip

        bonus_transaction = Transaction(BlockSettings.TIPPING_PK, public_key, tips_sum)
        self.transactions.insert(0, bonus_transaction)


def assertion_check():
    """
    Performs various assertions to verify the functionality of the Block class using Transaction objects.
    :return: None
    """
    logger.info("Starting assertions check for Block class...")

    # Create sample Transaction objects
    test_block = create_sample_block()

    # Verify the hash calculation before mining
    initial_hash = test_block.calculate_hash()
    assert test_block.hash is None, HASH_VALIDATION_ERROR  # Ensure no hash is set initially
    assert initial_hash == test_block.calculate_hash(), HASH_VALIDATION_ERROR
    assert test_block.validate_block()
    logger.info("All assertions passed for Block class.")


def create_sample_block(
        transactions_num=2,
        transactions_amounts=None,
        previews_hash="0" * 64,
        difficulty=MinerSettings.DIFFICULTY_LEVEL
):
    if transactions_amounts is None:
        transactions_amounts = [10, 20]
    if len(transactions_amounts) != transactions_num:
        raise "transaction num does not much the transaction amounts"
    transactions = []
    for i in range(transactions_num):
        transaction = create_sample_transaction(transactions_amounts[i])
        transactions.append(transaction)

    block = Block(previews_hash, transactions, difficulty)
    block.add_tipping_transaction(get_sk_pk_pair()[1])
    return block


if __name__ == "__main__":
    assertion_check()
