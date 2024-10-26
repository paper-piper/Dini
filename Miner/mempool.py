from logging_utils import setup_logger

# Setup logger for file
logger = setup_logger("mempool_module")


class Mempool:
    def __init__(self, transactions=None):
        if transactions is None:
            transactions = []
        self.transactions = transactions

    def select_transactions(self):
        """
        Selects transactions from the mempool. Future tipping system support can prioritize transactions with tips.
        :return: A list of selected transactions for mining.
        """
        selected_transactions = sorted(self.transactions, key=lambda tx: tx.priority, reverse=True)[:10]
        return selected_transactions

    def update(self, transactions):
        processed_tx_hashes = {tx.calculate_hash() for tx in transactions}
        self.transactions = [tx for tx in self.transactions if tx.calculate_hash() not in processed_tx_hashes]

