from cryptography.hazmat.primitives import serialization
from network.miner.action import Action
from utils.keys_manager import load_key
from utils.logging_utils import configure_logger
from utils.config import BlockChainSettings, KeysSettings, ActionStatus, ActionType, ActionSettings
from core.transaction import Transaction, get_sk_pk_pair, create_sample_transaction
from core.block import create_sample_block
import random
# Setup logger for the file


class Wallet:
    """
    A lightweight blockchain representation for managing a user's transactions and balance.

    :param owner_pk: Public key of the blockchain owner
    :param balance: Initial balance of the owner, default is 0
    :param actions: List of transactions associated with the blockchain
    :param latest_hash: Hash of the latest block added to the blockchain
    """
    def __init__(self, owner_pk, balance=0, actions=None, latest_hash=None, instance_id=None, child_dir="wallet"):
        self.owner_pk = owner_pk
        self.balance = balance
        self.actions = actions or {}
        self.latest_hash = latest_hash if latest_hash else BlockChainSettings.FIRST_HASH
        self.wallet_logger = configure_logger(
            class_name="wallet",
            child_dir=child_dir,
            instance_id=instance_id
        )
        self.wallet_logger.info("mempool logger initiated!")

    def add_pending_transaction(self, transaction, action_type):
        """
        Place a transaction in the pending pool with a timestamp.
        """
        action = Action(
            transaction.signature[:ActionSettings.ID_LENGTH],
            action_type,
            transaction.amount,
            ActionStatus.PENDING
        )
        self.actions[action.id] = action

    def filter_and_add_transaction(self, transaction):
        """
        Filters a transaction to determine if it is relevant and updates the balance accordingly.

        :param transaction: A transaction object containing sender, recipient, and amount details
        :return: False if the transaction is not relevant, otherwise True
        """
        if transaction.sender_pk == self.owner_pk:
            self.balance -= transaction.amount
        elif transaction.recipient_pk == self.owner_pk:
            self.balance += transaction.amount
        else:
            self.wallet_logger.info(f"Irrelevant transaction detected: {transaction}")
            return False

        transaction_id = transaction.signature[:ActionSettings.ID_LENGTH]
        if transaction_id in self.actions:
            self.actions[transaction_id].status = ActionStatus.APPROVED
            self.wallet_logger.info(f"action updated to be approved: {self.actions[transaction_id]}")
        else:
            action_type = ActionType.TRANSFER
            lord_key = load_key(KeysSettings.LORD_PK)
            bonus_key = lord_key(KeysSettings.BONUS_PK)
            tipping_key = lord_key(KeysSettings.TIPPING_PK)
            if transaction.sender_pk == lord_key:
                action_type = ActionType.BUY
            if transaction.recipient_pk == lord_key:
                action_type = ActionType.SELL
            if transaction.sender_pk == bonus_key:
                action_type = ActionType.MINE
            if transaction.sender_pk == tipping_key:
                action_type = ActionType.TIP

            action = Action(transaction_id, action_type, transaction.amount, ActionStatus.APPROVED)
            self.actions[transaction_id] = action
            self.wallet_logger.info(f"Action added: {action}")
        return True

    def filter_and_add_block(self, block):
        """
        Filters and adds a block to the blockchain if it is valid.

        :param block: A block object containing transactions and hash details
        :return: False if the block is new, otherwise True
        """
        if block.previous_hash != self.latest_hash:
            self.wallet_logger.info(f"Block rejected due to mismatched hash: {block}")
            return True

        self.latest_hash = block.hash
        for transaction in block.transactions:
            self.filter_and_add_transaction(transaction)

        self.wallet_logger.info(f"Block added: {block}")
        return False

    def to_dict(self):
        """
        Convert this LightBlockchain object into a dictionary for serialization.
        Since self.actions and self.pending_transactions store timestamps,
        convert them to a serializable format.
        """
        return {
            "owner_pk": self.owner_pk.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode(),
            "balance": self.balance,
            "actions": {action_id.hex(): action.to_dict() for action_id, action in self.actions.items()},
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
        actions = {
            bytes.fromhex(key): Action.from_dict(value)
            for key, value in data.get("actions", {}).items()
        }
        latest_hash = data["latest_hash"] if data["latest_hash"] else None
        light_blockchain = cls(owner_pk, balance, actions, latest_hash)
        return light_blockchain

    def get_recent_transactions(self, num=-1):
        """
        Return the most recent `num` transactions, merging both finalized and pending transactions,
        sorted by timestamp descending.
        """
        # Make sure the list is sorted
        sorted_actions = sorted(self.actions.values(), key=lambda x: x.timestamp, reverse=True)

        # Extract the transaction objects from the sorted list
        if num > len(sorted_actions) or num == -1:
            return sorted_actions

        return sorted_actions[:num]


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


def test_wallet():
    # Setup
    owner_sk, owner_pk = get_sk_pk_pair()  # Assume a utility function for creating a test key
    wallet = Wallet(owner_pk)
    transaction = create_sample_transaction(pk_sk_pair=(owner_pk, owner_sk))  # Assume a utility function for creating a test transaction
    block = create_sample_block(previews_hash=wallet.latest_hash, transactions_num=0)  # Assume a utility for creating a test block
    block.transactions.insert(1, transaction)

    # Test `add_pending_transaction`
    wallet.add_pending_transaction(transaction, "test_action")
    assert transaction.signature[:ActionSettings.ID_LENGTH] in wallet.actions, "Pending transaction not added correctly."

    # Test `filter_and_add_transaction`
    wallet.filter_and_add_transaction(transaction)
    assert wallet.balance == -transaction.amount, "Balance not updated correctly for received transaction."

    # Test `filter_and_add_block`
    result = wallet.filter_and_add_block(block)
    assert result is False, "Block addition returned incorrect value."
    assert wallet.latest_hash == block.hash, "Latest hash not updated after block addition."

    # Test `to_dict` and `from_dict`
    wallet_dict = wallet.to_dict()
    new_wallet = Wallet.from_dict(wallet_dict)
    assert wallet.owner_pk == new_wallet.owner_pk, "Owner public key mismatch after serialization."
    assert wallet.balance == new_wallet.balance, "Balance mismatch after serialization."

    # Test `get_recent_transactions`
    recent_transactions = wallet.get_recent_transactions(1)
    assert len(recent_transactions) == 1, "Recent transactions retrieval failed."
    assert recent_transactions[0].id == transaction.signature[:ActionSettings.ID_LENGTH], "Incorrect transaction retrieved."

    print("All Wallet class tests passed!")


if __name__ == "__main__":
    test_wallet()
