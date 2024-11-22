from logging_utils import setup_logger
from Blockchain.transaction import Transaction, get_sk_pk_pair
from Blockchain.block import Block
# Setup logger for the file
logger = setup_logger("light_blockchain")


class LightBlockchain:
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
        self.transactions = transactions if transactions is not None else []
        self.latest_hash = latest_hash

    def filter_and_add_transaction(self, transaction):
        """
        Filters a transaction to determine if it is relevant and updates the balance accordingly.

        :param transaction: A transaction object containing sender, recipient, and amount details
        :return: False if the transaction is not relevant, otherwise None
        """
        if transaction.sender_pk == self.owner_pk:
            self.balance -= transaction.amount
        elif transaction.recipient_pk == self.owner_pk:
            self.balance += transaction.amount
        else:
            logger.info(f"Irrelevant transaction detected: {transaction}")
            return False

        self.transactions.append(transaction)
        logger.info(f"Transaction added: {transaction}")

    def filter_and_add_block(self, block):
        """
        Filters and adds a block to the blockchain if it is valid.

        :param block: A block object containing transactions and hash details
        :return: False if the block is invalid, otherwise None
        """
        if block.previous_hash != self.latest_hash:
            logger.info(f"Block rejected due to mismatched hash: {block}")
            return False

        self.latest_hash = block.hash
        for transaction in block.transactions:
            self.filter_and_add_transaction(transaction)

        logger.info(f"Block added: {block}")


def assertion_check():
    """
    Performs assertion checks to validate the functionality of the LightBlockchain class.
    """

    # Create a blockchain instance
    my_sk, my_pk = get_sk_pk_pair()
    other_sk, other_pk = get_sk_pk_pair()
    blockchain = LightBlockchain(owner_pk=my_pk, balance=100)

    # Test transactions
    transaction1 = Transaction(sender_pk=my_pk, recipient_pk=other_pk, amount=50)
    transaction2 = Transaction(sender_pk=other_pk, recipient_pk=my_pk, amount=30)

    blockchain.filter_and_add_transaction(transaction1)
    blockchain.filter_and_add_transaction(transaction2)

    assert blockchain.balance == 80, "Balance calculation error after transactions"

    # Test blocks
    block = Block(previous_hash=None, transactions=[transaction1, transaction2], block_hash="hash123")
    blockchain.latest_hash = None  # Setting the latest hash for validation
    blockchain.filter_and_add_block(block)

    assert blockchain.latest_hash == "hash123", "Block hash mismatch after adding block"
    assert len(blockchain.transactions) == 4, "Transaction count mismatch after adding block"


if __name__ == "__main__":
    assertion_check()
