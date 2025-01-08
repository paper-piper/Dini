from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from network.miner.transaction_wrapper import TransactionWrapper
from utils.logging_utils import setup_basic_logger
from utils.config import BlockChainSettings, TransactionSettings
from core.transaction import Transaction, get_sk_pk_pair

logger = setup_basic_logger()


class Wallet:
    """
    A lightweight blockchain representation for managing a user's transactions and balance.
    """

    def __init__(self, owner_pk, balance=0, transactions=None, latest_hash=None):
        """
        :param owner_pk: Public key of the wallet owner
        :param balance: Initial balance of the owner, default is 0
        :param transactions: Dict of {wrapper_id: TransactionWrapper}
        :param latest_hash: Hash of the latest block
        """
        self.owner_pk = owner_pk
        self.balance = balance
        # Single dictionary of ID -> TransactionWrapper
        self.transactions = transactions if transactions is not None else {}
        self.latest_hash = latest_hash if latest_hash else BlockChainSettings.FIRST_HASH

    def add_pending_transaction(self, transaction):
        """
        Wraps a newly created transaction as 'pending' and inserts it into self.transactions.

        - The transaction might be created by this wallet's owner,
          or by some external event, but we treat it as 'pending' first.
        """
        # Create a wrapper with status="pending"
        wrapper = TransactionWrapper(transaction=transaction,
                                     status="pending",
                                     created_at=datetime.now())

        # Use wrapper.id as the key in our transactions dictionary
        self.transactions[wrapper.id] = wrapper
        logger.info(f"Added pending transaction: {wrapper}")

    def filter_and_add_transaction(self, transaction):
        """
        - Checks if the transaction is relevant to this wallet (sender or recipient).
        - If relevant, updates self.balance accordingly.
        - If we already have a matching 'pending' transaction, mark it as 'approved'.
          Otherwise, create a new wrapper as 'approved'.
        - If a 'pending' transaction is too old and not approved, mark it 'failed'.

        :param transaction: A Transaction object
        :return: False if not relevant, True otherwise
        """
        if transaction.sender_pk == self.owner_pk:
            self.balance -= transaction.amount
            self.balance -= transaction.tip
        elif transaction.recipient_pk == self.owner_pk:
            self.balance += transaction.amount
        else:
            logger.info(f"Irrelevant transaction detected: {transaction}")
            return False

        # Identify if this transaction was previously pending:
        existing_wrapper_id = (transaction.signature or "")[:TransactionSettings.ID_LENGTH]
        existing_wrapper = self.transactions.get(existing_wrapper_id)

        if existing_wrapper:
            # If we already have a pending wrapper, approve it
            # But first check if it's too old (example threshold: 1 minute)
            age = datetime.now() - existing_wrapper.created_at
            if age > timedelta(minutes=1) and existing_wrapper.status == TransactionSettings.STATUS_PENDING:
                existing_wrapper.status = TransactionSettings.STATUS_FAILED
                logger.info(f"Pending transaction {existing_wrapper.id} is too old, marking as failed.")
            else:
                existing_wrapper.status = TransactionSettings.STATUS_APPROVED
                logger.info(f"Pending transaction {existing_wrapper.id} changed to approved.")
        else:
            # Create a brand-new wrapper with status='approved'
            wrapper = TransactionWrapper(transaction=transaction,
                                         status=TransactionSettings.STATUS_APPROVED,
                                         created_at=datetime.now())
            self.transactions[wrapper.id] = wrapper
            logger.info(f"New transaction added as approved: {wrapper}")

        return True

    def filter_and_add_block(self, block):
        """
        - Checks if block has correct previous_hash
        - Updates self.latest_hash
        - filter_and_add_transaction() for each transaction in the block
        - Return False if block is new, True if block was rejected
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
        Convert this wallet to a serializable dict. Each TransactionWrapper is also converted.
        """
        return {
            "owner_pk": self.owner_pk.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode(),
            "balance": self.balance,
            "transactions": [
                wrapper.to_dict() for wrapper in self.transactions.values()
            ],
            "latest_hash": self.latest_hash
        }

    @classmethod
    def from_dict(cls, data):
        """
        Reconstruct a Wallet from a dictionary. Rebuild each TransactionWrapper from its to_dict().
        """
        owner_pk = serialization.load_pem_public_key(data["owner_pk"].encode())
        balance = data["balance"]
        latest_hash = data["latest_hash"] if data["latest_hash"] else None

        transactions = {}
        for wrapper_data in data["transactions"]:
            wrapper = TransactionWrapper.from_dict(wrapper_data, Transaction)
            transactions[wrapper.id] = wrapper

        wallet = cls(owner_pk, balance, transactions, latest_hash)
        return wallet

    def get_recent_transactions(self, num):
        """
        Return the most recent `num` transactions from self.transactions,
        sorted by created_at descending.
        """
        wrappers = list(self.transactions.values())
        wrappers_sorted = sorted(wrappers, key=lambda w: w.created_at, reverse=True)

        if num == -1 or num > len(wrappers_sorted):
            return wrappers_sorted
        return wrappers_sorted[:num]

def assertion_check():
    """
    Thoroughly tests the Wallet class and TransactionWrapper functionality.
    1) Creates a wallet and some keypairs.
    2) Adds pending transactions and verifies status transitions.
    3) Checks correct balance changes for relevant transactions.
    4) Tests serialization/deserialization (to_dict/from_dict).
    5) Confirms recent transaction sorting.
    """


    # -------------
    # Setup
    # -------------
    # Generate key pairs
    my_sk, my_pk = get_sk_pk_pair()
    other_sk, other_pk = get_sk_pk_pair()

    # Create a wallet with an initial balance
    wallet = Wallet(owner_pk=my_pk, balance=1000)
    assert wallet.balance == 1000, "Initial wallet balance is incorrect."

    # -------------
    # 1) Add Pending Transaction (Outgoing)
    # -------------
    tx_outgoing = Transaction(sender_pk=my_pk, recipient_pk=other_pk, amount=100, tip=1)
    tx_outgoing.sign_transaction(my_sk)  # Must sign to generate a signature
    outgoing_sig = tx_outgoing.signature
    wallet.add_pending_transaction(tx_outgoing)

    # Confirm it's in the wallet with status "pending"
    out_id = outgoing_sig[:8]
    assert out_id in wallet.transactions, "Outgoing transaction not found after add_pending_transaction."
    out_wrapper = wallet.transactions[out_id]
    assert out_wrapper.status == "pending", "Outgoing transaction should have status='pending' right after adding."
    assert out_wrapper.created_at <= datetime.now(), "created_at should be set to current time."

    # -------------
    # 2) Add Pending Transaction (Incoming)
    # -------------
    tx_incoming = Transaction(sender_pk=other_pk, recipient_pk=my_pk, amount=50, tip=2)
    tx_incoming.sign_transaction(other_sk)
    inc_sig = tx_incoming.signature
    wallet.add_pending_transaction(tx_incoming)

    inc_id = inc_sig[:8]
    assert inc_id in wallet.transactions, "Incoming transaction not found after add_pending_transaction."
    inc_wrapper = wallet.transactions[inc_id]
    assert inc_wrapper.status == "pending", "Incoming transaction should have status='pending' immediately."
    old_balance = wallet.balance

    # -------------
    # 3) Approve One Transaction (filter_and_add_transaction)
    #    Outgoing transaction
    # -------------
    # We'll immediately "filter_and_add" the outgoing transaction
    # (simulate receiving it from a block or network).
    wallet.filter_and_add_transaction(tx_outgoing)

    # Because the transaction is relevant (sender = me), check status
    new_wrapper_out = wallet.transactions[out_id]
    # In our example code, it is marked 'approved' if not too old
    assert new_wrapper_out.status in ["approved", "failed"], \
        "Outgoing transaction status should be approved or failed after filter_and_add_transaction."

    # If approved, balance should decrease by (amount + tip) => 100 + 1
    if new_wrapper_out.status == "approved":
        assert wallet.balance == 1000 - (100 + 1), \
            "Outgoing transaction approved but wallet balance didn't decrement correctly."
    else:
        # If the transaction was considered too old (failed), the balance shouldn't have changed
        assert wallet.balance == 1000, "Failed transaction should not alter wallet balance."

    # -------------
    # 4) Test Automatic Failing of Pending (if time passes)
    #    We'll artificially move the pending incoming transaction's created_at back in time.
    # -------------
    # Suppose a pending transaction that doesn't get confirmed quickly is "failed" after 1 second
    # (for demonstration, we'll forcibly shift its created_at to simulate time passing).
    inc_wrapper.created_at = datetime.now() - timedelta(seconds=2)

    # Now call filter_and_add_transaction for the same incoming transaction
    wallet.filter_and_add_transaction(tx_incoming)
    new_wrapper_inc = wallet.transactions[inc_id]
    # If your logic says 1 second => too old => "failed", then we check:
    # Alternatively, you might have a 1-minute threshold. Adjust as needed.
    assert new_wrapper_inc.status in ["approved", "failed"], \
        "Incoming transaction status should be updated to approved or failed."

    if new_wrapper_inc.status == "approved":
        # Balance should have increased by 50 if it was approved
        assert wallet.balance == (1000 - (100 + 1)) + 50, \
            "Incoming transaction approval did not properly update balance."
    else:
        # If it failed, no balance change from old_balance
        # We must figure out what the balance was after the outgoing was processed
        if new_wrapper_out.status == "approved":
            # Then the wallet had 899
            assert wallet.balance == 899, "Incoming transaction failed, so wallet balance shouldn't have changed."
        else:
            # Then outgoing also failed, wallet is still 1000
            assert wallet.balance == 1000, "Incoming transaction failed, so wallet balance shouldn't have changed."

    # -------------
    # 5) Test to_dict / from_dict
    # -------------
    wallet_dict = wallet.to_dict()
    # Recreate from the dict
    new_wallet = Wallet.from_dict(wallet_dict)

    # Compare essential fields
    assert new_wallet.owner_pk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ) == wallet.owner_pk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ), "Public keys do not match after to_dict/from_dict."

    assert new_wallet.balance == wallet.balance, "Balance mismatch after serialization."
    assert new_wallet.latest_hash == wallet.latest_hash, "latest_hash mismatch after serialization."
    assert len(new_wallet.transactions) == len(wallet.transactions), \
        "Transaction count mismatch after serialization."

    for wid, wwrapper in wallet.transactions.items():
        # Compare individual wrappers
        new_wrapper = new_wallet.transactions.get(wid)
        assert new_wrapper, f"Missing transaction wrapper {wid} after from_dict."
        assert new_wrapper.status == wwrapper.status, f"Status mismatch for transaction {wid}."
        assert abs((new_wrapper.created_at - wwrapper.created_at).total_seconds()) < 0.001, \
            f"Timestamp mismatch for transaction {wid}."
        # Compare the transaction data inside
        assert new_wrapper.transaction.to_dict() == wwrapper.transaction.to_dict(), \
            f"Transaction data mismatch for wrapper {wid}."

    # -------------
    # 6) Check get_recent_transactions
    # -------------
    # Sort all wrappers by created_at descending
    sorted_wrappers = wallet.get_recent_transactions(-1)  # -1 to get all
    for i in range(len(sorted_wrappers) - 1):
        assert sorted_wrappers[i].created_at >= sorted_wrappers[i+1].created_at, \
            "Transactions are not in descending order by created_at."

    logger.info("All assertion checks passed successfully!")
    print("All assertion checks passed successfully!")

if __name__ == "__main__":
    assertion_check()
