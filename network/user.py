from cryptography.hazmat.primitives import serialization

from network.bootstrap import Bootstrap
import json
import os
from core.wallet import Wallet, create_sample_light_blockchain
from core.transaction import Transaction, get_sk_pk_pair
from utils.config import MsgTypes, MsgSubTypes, FilesSettings, BlockSettings, KeysSettings, ActionType, ActionSettings, \
    NodeSettings
from utils.keys_manager import load_key
from utils.logging_utils import configure_logger


class User(Bootstrap):
    """
    Manages user operations including blockchain updating, file saving, and broadcasting transactions.
    """
    def __init__(
            self,
            public_key,
            secret_key,
            wallet=None,
            ip=None,
            port=None,
            child_dir="User",
            name=NodeSettings.DEFAULT_NAME
    ):
        """
        :param public_key: User's public key
        :param secret_key: User's secret key
        :param wallet: core object, or None to load from file.
        """

        # initiate public and private keys before calling super class in order to pass public key and name
        self.public_key = public_key
        self.private_key = secret_key

        super().__init__(is_bootstrap=False,
                         ip=ip, port=port,
                         child_dir=child_dir,
                         name=name
                         )

        self.user_logger = configure_logger(
            class_name="User",
            child_dir=child_dir,
            instance_id=f"{self.ip}-{self.port}"
        )


        directory_name = f"{child_dir}_{str(self.port)}"
        self.wallet_path = os.path.join(FilesSettings.DATA_ROOT_DIRECTORY, directory_name, FilesSettings.WALLET_FILE_NAME)
        # make the wallet directory if you don't already exist
        full_directory = os.path.dirname(self.wallet_path)
        os.makedirs(full_directory, exist_ok=True)
        self.wallet = wallet if wallet else self.load_wallet(child_dir)

        # try and get updates for wallet (in case of missing out)
        self.request_blockchain_update()
        self.save_wallet()

    def request_blockchain_update(self):
        self.send_distributed_message(
            MsgTypes.REQUEST,
            MsgSubTypes.BLOCKCHAIN,
            self.wallet.latest_hash
        )

    def __del__(self):
        if hasattr(self, "port_manager") and self.port_manager:
            self.port_manager.release_port(self.port)
        self.save_wallet()

    def get_recent_transactions(self, num=5):
        return self.wallet.get_recent_transactions(num)

    def buy_dinis(self, amount):
        lord_pk = load_key(KeysSettings.LORD_PK)
        lord_sk = load_key(KeysSettings.LORD_SK)
        transaction = Transaction(lord_pk, self.public_key, amount, BlockSettings.BONUS_AMOUNT)
        transaction.sign_transaction(lord_sk)
        self.wallet.add_pending_transaction(transaction, ActionType.BUY)

        self.send_distributed_message(MsgTypes.RESPONSE, MsgSubTypes.TRANSACTION, transaction)
        self.user_logger.info(f"bought {amount} Dini's")

        return transaction.signature[:ActionSettings.ID_LENGTH]

    def sell_dinis(self, amount):
        lord_pk = load_key(KeysSettings.LORD_PK)
        transaction = Transaction(self.public_key, lord_pk, amount, BlockSettings.BONUS_AMOUNT)
        transaction.sign_transaction(self.private_key)
        self.wallet.add_pending_transaction(transaction, ActionType.SELL)
        self.send_distributed_message(MsgTypes.RESPONSE, MsgSubTypes.TRANSACTION, transaction)
        self.user_logger.info(f" {amount} Dini's")

        return transaction.signature[:ActionSettings.ID_LENGTH]

    def add_transaction(self, address, amount, tip=0):
        """
        Creates a signed transaction and broadcasts it to peers.
        :param address: Recipient's address.
        :param amount: Amount to be transferred.
        :param tip: added tip (optional)
        """
        transaction = Transaction(self.public_key, address, amount, tip)
        transaction.sign_transaction(self.private_key)
        # keep track of pending transactions
        self.wallet.add_pending_transaction(transaction, ActionType.TRANSFER)
        self.send_distributed_message(MsgTypes.RESPONSE, MsgSubTypes.TRANSACTION, transaction)
        self.user_logger.info(f"new transaction made: {transaction} ")

        return transaction.signature[:ActionSettings.ID_LENGTH]

    def process_block_data(self, block):
        """
        Adds a block to the wallet and saves the updated chain.

        :param block: Block to add.
        :return: None
        """
        # check
        already_seen = self.wallet.filter_and_add_block(block)
        self.save_wallet()
        self.user_logger.info(f" Block added to wallet and saved. block: {block}")
        return already_seen

    def process_blockchain_data(self, blockchain):
        """
        Handles the sending of blocks to other peers.
        :param blockchain: Parameters associated with the block send.
        """
        relevant_blocks = blockchain.get_blocks_after(self.wallet.latest_hash)
        for block in relevant_blocks:
            self.process_block_data(block)
        self.user_logger.info(f"Blockchain response added to wallet and saved.")

    def serve_blockchain_request(self, latest_hash):
        """
        Handles requests from peers to update the blockchain.
        """
        pass
        #  self.user_logger.debug(f"User does not handle blockchain updates")

    def process_transaction_data(self, params):
        """
        Raises an error as users do not handle transactions directly.

        :param params: Parameters associated with the transaction send.
        """
        pass
        #  self.user_logger.debug(f"User does not handle transactions")

    def get_public_key(self):
        return self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()

    def save_wallet(self):
        """
        Saves the current wallet to a file in JSON format.
        :return: None
        """
        # if the wallet is empty, don't save it
        if not self.wallet:
            return
        try:
            with open(self.wallet_path, "w") as f:
                dictionary_wallet = self.wallet.to_dict()
                json.dump(dictionary_wallet, f, indent=4)
        except Exception as e:
            self.user_logger.error(f"Error saving wallet: {e} the wallet: {dictionary_wallet}")

    def load_wallet(self, child_dir):
        """
        Loads the wallet from a file if it exists.
        :return: the wallet if exists, else initialized wallet
        """
        if os.path.exists(self.wallet_path) and os.path.getsize(self.wallet_path) != 0:
            try:
                with open(self.wallet_path, "r") as f:
                    blockchain_data = json.load(f)
                    wallet = Wallet.from_dict(blockchain_data)
                self.user_logger.info(f"core loaded from {self.wallet_path}")
                return wallet
            except Exception as e:
                self.user_logger.error(f"Error loading wallet: {e}")
                return Wallet(self.public_key, instance_id=f"{self.ip}-{self.port}", child_dir=child_dir)

        self.user_logger.warning(f"No wallet file found at {self.wallet_path}, initializing new blockchain.")
        return Wallet(self.public_key, instance_id=f"{self.ip}-{self.port}", child_dir=child_dir)

    def request_update_blockchain(self):
        """
        Requests a specific block update from peers.
        :return: None
        """
        self.send_distributed_message(
            MsgTypes.REQUEST,
            MsgSubTypes.BLOCKCHAIN,
            self.wallet.latest_hash
        )
        self.user_logger.info(f"Requesting updates with latest hash: {self.wallet.latest_hash}")


def assertion_check():
    """
    Runs assertions to test the functionality of User class methods related to blockchain saving and loading.

    :return: None
    """
    # Generate key pair for testing
    sk, pk = get_sk_pk_pair()
    # Create a sample blockchain and save it using the first User instance
    user1 = User(
        pk,
        sk,
        wallet=create_sample_light_blockchain(pk, sk),
        )
    user1.save_wallet()

    # Load the blockchain from the saved file using a second User instance and save to a new file
    user2 = User(pk, sk, )
    user2.load_wallet("User")
    user2.save_wallet()

    # Load files and verify they are identical
    with (open("../data/sample_wallet1.json", "r") as f1,
          open("../data/sample_wallet2.json", "r") as f2):
        blockchain_data_1 = json.load(f1)
        blockchain_data_2 = json.load(f2)

    assert blockchain_data_1 == blockchain_data_2, "Loaded blockchain data does not match saved data"


if __name__ == "__main__":
    assertion_check()
