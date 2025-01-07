from cryptography.hazmat.primitives import serialization
from datetime import datetime
from utils.logging_utils import setup_basic_logger
from utils.config import BlockChainSettings
from core.transaction import Transaction, get_sk_pk_pair
from core.block import Block
import random
# Setup logger for the file
logger = setup_basic_logger()


class Wallet:
    """
    A lightweight blockchain representation for managing a user's transactions and balance.

    :param owner_pk: Public key of the blockchain owner
    :param balance: Initial balance of the owner, default is 0
    :param transactions: List of transactions associated with the blockchain
    :param latest_hash: Hash of the latest block added to the blockchain
    """
    def __init__(self, owner_pk, balance=0, transactions=None, latest_hash=None):
        self.owner_pk = owner_pk
        self.balance = balance
        self.pending_transactions = {}  # dictionary of transaction -> time
        self.transactions = transactions if transactions is not None else {}
        self.latest_hash = latest_hash if latest_hash else BlockChainSettings.FIRST_HASH

    def add_pending_transaction(self, transaction):
        """
        Place a transaction in the pending pool with a timestamp.
        """
        self.pending_transactions[transaction] = datetime.now()

    def filter_and_add_transaction(self, transaction):
        """
        Filters a transaction to determine if it is relevant and updates the balance accordingly.

        :param transaction: A transaction object containing sender, recipient, and amount details
        :return: False if the transaction is not relevant, otherwise True
        """
        if transaction.sender_pk == self.owner_pk:
            self.balance -= transaction.amount
            self.balance -= transaction.tip
        elif transaction.recipient_pk == self.owner_pk:
            self.balance += transaction.amount
        else:
            logger.info(f"Irrelevant transaction detected: {transaction}")
            return False

        self.transactions[transaction] = datetime.now()
        if transaction in self.pending_transactions:
            self.pending_transactions.pop(transaction)
        logger.info(f"Transaction added: {transaction}")
        return True

    def filter_and_add_block(self, block):
        """
        Filters and adds a block to the blockchain if it is valid.

        :param block: A block object containing transactions and hash details
        :return: False if the block is new, otherwise True
        """
        if block.previous_hash != self.latest_hash:
            logger.info(f"Block rejected due to mismatched hash: {block}")
            return True

        self.latest_hash = block.hash
        for transaction in block.transactions:
            self.filter_and_add_transaction(transaction)

        logger.info(f"Block added: {block}")
        return False

    def to_dict(self):
        """
        Convert this LightBlockchain object into a dictionary for serialization.
        Since self.transactions and self.pending_transactions store timestamps,
        convert them to a serializable format.
        """
        return {
            "owner_pk": self.owner_pk.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode(),
            "balance": self.balance,
            "transactions": [
                {"transaction": transaction.to_dict(), "timestamp": timestamp.isoformat()}
                for transaction, timestamp in self.transactions.items()
            ],
            "pending_transactions": [
                {"transaction": transaction.to_dict(), "timestamp": timestamp.isoformat()}
                for transaction, timestamp in self.pending_transactions.items()
            ],
            "latest_hash": self.latest_hash if self.latest_hash else None
        }

    @classmethod
    def from_dict(cls, data):
        """
        Reconstruct a LightBlockchain from a dictionary. Both finalized and pending transactions
        are reconstructed with their associated timestamps.
        """
        owner_pk = serialization.load_pem_public_key(data["owner_pk"].encode())
        balance = data["balance"]

        # Rebuild finalized transactions
        transactions = {}
        for item in data["transactions"]:
            transaction = Transaction.from_dict(item["transaction"])
            timestamp = datetime.fromisoformat(item["timestamp"])
            transactions[transaction] = timestamp

        # Rebuild pending transactions
        pending_transactions = {}
        for item in data["pending_transactions"]:
            transaction = Transaction.from_dict(item["transaction"])
            timestamp = datetime.fromisoformat(item["timestamp"])
            pending_transactions[transaction] = timestamp

        latest_hash = data["latest_hash"] if data["latest_hash"] else None
        light_blockchain = cls(owner_pk, balance, transactions, latest_hash)
        light_blockchain.pending_transactions = pending_transactions
        return light_blockchain

    def get_recent_transactions(self, num):
        """
        Return the most recent `num` transactions, merging both finalized and pending transactions,
        sorted by timestamp descending.
        """
        # Combine both finalized and pending transactions into one list
        all_transactions = list(self.transactions.items()) + list(self.pending_transactions.items())

        # Sort by timestamp descending
        sorted_by_time = sorted(all_transactions, key=lambda item: item[1], reverse=True)

        # Extract the transaction objects from the sorted list
        if num > len(sorted_by_time) or num == -1:
            return sorted_by_time
        recent_transactions = [tx for tx, ts in sorted_by_time[:num]]

        return recent_transactions


def create_sample_light_blockchain(
        public_key,
        secret_key,
        other_public_key=None,
        starting_balance=0,
        transaction_nums=None,
        latest_hash=None
):
    """
    Creates a sample LightBlockchain instance with a few random transactions
    (some incoming, some outgoing).
    """
    other_public_key = get_sk_pk_pair()[1] if not other_public_key else other_public_key

    if transaction_nums is None:
        transaction_nums = [30, 20, 10, 40]

    blockchain = Wallet(public_key, balance=starting_balance, latest_hash=latest_hash)

    for i in range(len(transaction_nums)):
        if random.randint(0, 2) == 1:
            transaction = Transaction(public_key, other_public_key, transaction_nums[i])
        else:
            transaction = Transaction(other_public_key, public_key, transaction_nums[i])

        transaction.sign_transaction(secret_key)
        blockchain.filter_and_add_transaction(transaction)

    return blockchain


def assertion_check():
    """
    Performs assertion checks to validate the functionality of the LightBlockchain class.
    """

    # Create a blockchain instance
    my_sk, my_pk = get_sk_pk_pair()
    other_sk, other_pk = get_sk_pk_pair()
    blockchain = Wallet(owner_pk=my_pk, balance=100)

    # Test transactions
    transaction1 = Transaction(sender_pk=my_pk, recipient_pk=other_pk, amount=50)
    transaction2 = Transaction(sender_pk=other_pk, recipient_pk=my_pk, amount=30)

    blockchain.filter_and_add_transaction(transaction1)

    assert blockchain.balance == 50, "Balance calculation error after transactions"

    # Test blocks
    block = Block(previous_hash=None, transactions=[transaction1, transaction2], block_hash="hash123")
    blockchain.latest_hash = None  # Setting the latest hash for validation
    blockchain.filter_and_add_block(block)

    assert blockchain.latest_hash == "hash123", "Block hash mismatch after adding block"
    assert len(blockchain.transactions) == 2, "Transaction count mismatch after adding block"

    transaction1.sign_transaction(my_sk)
    blockchain.latest_hash = transaction1.signature
    blockchain_dict = blockchain.to_dict()
    duplicate_blockchain = Wallet.from_dict(blockchain_dict)
    assert duplicate_blockchain.to_dict() == blockchain.to_dict()


if __name__ == "__main__":
    assertion_check()
