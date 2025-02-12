from utils.logging_utils import configure_logger
from core.transaction import create_sample_transaction
from utils.config import BlockSettings
# Setup self.mempool_logger for file


class Mempool:
    """
    A class to manage a mempool, which holds unique transactions and provides methods
    to add, remove, and select transactions based on specific criteria.
    """

    def __init__(self, instance_id=None, child_dir="mempool"):
        """
        Initializes the mempool with an empty set to store unique transactions.
        """
        self.transactions = set()
        self.mempool_logger = configure_logger(
            class_name="Mempool",
            child_dir=child_dir,
            instance_id=instance_id
        )

    def add_transactions(self, transactions):
        """
        Adds a list of transactions to the mempool.
        Only transactions not already in the mempool are added.

        :param transactions: List of Transaction objects to add to the mempool
        :return: None
        """
        for tx in transactions:
            if tx not in self.transactions:
                self.mempool_logger.info(f"Adding transaction: {tx}")
                self.transactions.add(tx)

    def remove_transactions(self, transactions):
        """
        Removes a list of transactions from the mempool.
        Transactions not in the mempool are ignored.

        :param transactions: List of Transaction objects to remove from the mempool
        :return: None
        """
        for tx in transactions:
            if tx in self.transactions:
                self.mempool_logger.info(f"Removing transaction: {tx}")
            self.transactions.discard(tx)

    def has_transaction(self, transaction):
        return transaction in self.transactions

    def get_all_transactions(self):
        """
        Returns all transactions currently in the mempool.

        :return: List of Transaction objects currently in the mempool
        """
        self.mempool_logger.info(f"Fetching all transactions. Count: {len(self.transactions)}")
        return list(self.transactions)

    def select_transactions(self, num_transactions=BlockSettings.MAX_TRANSACTIONS):
        """
        Selects the top transactions with the highest 'tip' values.

        :param num_transactions: Number of transactions to select
        :return: List of selected Transaction objects
        """
        try:
            sorted_transactions = sorted(
                self.transactions, key=lambda tx: tx.tip, reverse=True
            )
            if num_transactions > len(sorted_transactions):
                selected = sorted_transactions
            else:
                selected = sorted_transactions[:num_transactions]
            return selected
        except Exception as e:
            self.mempool_logger.error(f"Error while selecting transactions: {e}")
            return []


def assertion_check():
    """
    Tests the Mempool class to ensure its functionality works as expected.

    :return: None
    """

    transactions = []
    for i in range(10):
        transactions.append(create_sample_transaction())

    # Initialize mempool
    mempool = Mempool()

    # Test add_transactions
    mempool.add_transactions(transactions)
    assert len(mempool.get_all_transactions()) == len(transactions), "Add transactions failed."

    # Test remove_transactions
    mempool.remove_transactions([transactions[0]])
    assert len(mempool.get_all_transactions()) == len(transactions) - 1, "Remove transactions failed."

    # Test select_transactions
    selected = mempool.select_transactions(2)
    assert len(selected) == 2, "Select transactions failed."
    assert selected[0].tip >= selected[1].tip, "Transactions not sorted correctly."


if __name__ == "__main__":
    assertion_check()
