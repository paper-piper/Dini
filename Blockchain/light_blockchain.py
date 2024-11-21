class LightBlockchain:
    def __init__(self, owner_pk, balance=0, transactions=None, latest_hash=None):
        self.owner_pk = owner_pk
        self.balance = balance
        self.transactions = transactions
        self.latest_hash = latest_hash

    def filter_and_add_transaction(self, transaction):
        # check if a transaction is relevant and add it
        if transaction.sender_pk == self.owner_pk:
            self.balance -= transaction.amount
        elif transaction.recipient_pk is not self.owner_pk:
            self.balance += transaction.amount
        else:
            # else, the transaction is relevant
            return False

        self.transactions.append(transaction)

    def filter_and_add_block(self, block):
        # check if block is the next block. if so, add all relevant transactions
        if block.previous_hash != self.latest_hash:
            return False

        self.latest_hash = block.hash
        for transaction in block.transactions:
            self.filter_and_add_transaction(transaction)
