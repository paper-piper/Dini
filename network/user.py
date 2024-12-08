from network.bootstrap import Bootstrap
import json
import os
from core.light_blockchain import LightBlockchain, create_sample_light_blockchain
from core.transaction import Transaction, get_sk_pk_pair
from utils.config import MsgTypes, MsgSubTypes, FilesSettings, BlockSettings, KeysSettings
from utils.keys_manager import load_key
from utils.logging_utils import setup_logger

logger = setup_logger()


class User(Bootstrap):
    """
    Manages user operations including blockchain updating, file saving, and broadcasting transactions.
    """
    def __init__(self, public_key, secret_key, wallet=None, wallet_filename=None, port_manager=None):
        """
        :param public_key: User's public key
        :param secret_key: User's secret key
        :param wallet: core object, or None to load from file.
        :param wallet_filename: Name of the file where wallet data is saved.
        """
        super().__init__(is_bootstrap=False, port_manager=port_manager)
        self.public_key = public_key
        self.private_key = secret_key
        self.wallet_filename = FilesSettings.WALLET_FILE_NAME if wallet_filename is None else wallet_filename
        self.wallet = wallet if wallet else self.load_wallet()
        # try and get updates for wallet (in case of missing out)
        self.send_distributed_message(
            MsgTypes.REQUEST_OBJECT,
            MsgSubTypes.BLOCKCHAIN,
            self.wallet.latest_hash
        )

    def __del__(self):
        if self.port_manager:
            self.port_manager.release_port(self.port)
        self.save_wallet()

    def get_recent_transactions(self, num=5):
        return self.wallet.get_recent_transactions(num)

    def buy_dinis(self, amount):
        lord_pk = load_key(KeysSettings.LORD_PK)
        lord_sk = load_key(KeysSettings.LORD_SK)
        transaction = Transaction(lord_pk, self.public_key, amount, BlockSettings.BONUS_AMOUNT)
        transaction.sign_transaction(lord_sk)
        self.send_distributed_message(MsgTypes.SEND_OBJECT, MsgSubTypes.TRANSACTION, transaction)
        logger.info(f"bought {amount} Dini's")

    def sell_dinis(self, amount):
        lord_pk = load_key(KeysSettings.LORD_PK)
        transaction = Transaction(self.public_key, lord_pk, amount, BlockSettings.BONUS_AMOUNT)
        transaction.sign_transaction(self.private_key)
        self.send_distributed_message(MsgTypes.SEND_OBJECT, MsgSubTypes.TRANSACTION, transaction)
        logger.info(f"Sold {amount} Dini's")

    def make_transaction(self, address, amount, tip=0):
        """
        Creates a signed transaction and broadcasts it to peers.
        :param address: Recipient's address.
        :param amount: Amount to be transferred.
        :param tip: added tip (optional)
        """
        transaction = Transaction(self.public_key, address, amount, tip)
        transaction.sign_transaction(self.private_key)
        self.send_distributed_message(MsgTypes.SEND_OBJECT, MsgSubTypes.TRANSACTION, transaction)
        logger.info(f"Transaction made from {self.public_key} to {address} of amount {amount} and tip {tip}")

    def process_block_data(self, block):
        """
        Adds a block to the wallet and saves the updated chain.

        :param block: Block to add.
        :return: None
        """
        self.wallet.filter_and_add_block(block)
        self.save_wallet()
        logger.info("Block added to wallet and saved")

    def process_blockchain_data(self, blockchain):
        """
        Handles the sending of blocks to other peers.
        :param blockchain: Parameters associated with the block send.
        """
        relevant_blocks = blockchain.get_blocks_after(self.wallet.latest_hash)
        for block in relevant_blocks:
            self.process_block_data(block)

    def serve_blockchain_request(self, latest_hash):
        """
        Handles requests from peers to update the blockchain.
        """
        logger.info("User does not handle blockchain updates")

    def process_transaction_data(self, params):
        """
        Raises an error as users do not handle transactions directly.

        :param params: Parameters associated with the transaction send.
        """
        logger.info("User does not handle transactions")

    def save_wallet(self):
        """
        Saves the current wallet to a file in JSON format.
        :return: None
        """
        try:
            wallet_path = os.path.join(FilesSettings.DATA_ROOT_DIRECTORY, self.wallet_filename)
            with open(wallet_path, "w") as f:
                dictionary_wallet = self.wallet.to_dict()
                json.dump(dictionary_wallet, f, indent=4)
            logger.info(f"wallet saved to {wallet_path}")
        except Exception as e:
            logger.error(f"Error saving wallet: {e}")

    def load_wallet(self):
        """
        Loads the wallet from a file if it exists.
        :return: the wallet if exists, else initialized wallet
        """
        wallet_path = os.path.join(FilesSettings.DATA_ROOT_DIRECTORY, self.wallet_filename)
        if os.path.exists(wallet_path):
            try:
                with open(wallet_path, "r") as f:
                    blockchain_data = json.load(f)
                    wallet = LightBlockchain.from_dict(blockchain_data)
                logger.info(f"core loaded from {wallet_path}")
                return wallet
            except Exception as e:
                logger.error(f"Error loading blockchain: {e}")
                return LightBlockchain(self.public_key)

        logger.warning(f"No blockchain file found at {self.wallet_filename}, initializing new blockchain.")
        return LightBlockchain(self.public_key)

    def request_update_blockchain(self):
        """
        Requests a specific block update from peers.
        :return: None
        """
        self.send_distributed_message(
            MsgTypes.REQUEST_OBJECT,
            MsgSubTypes.BLOCKCHAIN,
            self.wallet.latest_hash
        )
        logger.info(f"Requesting updates with latest hash: {self.wallet.latest_hash}")


def assertion_check():
    """
    Runs assertions to test the functionality of User class methods related to blockchain saving and loading.

    :return: None
    """
    # Generate key pair for testing
    sk, pk = get_sk_pk_pair()
    first_wallet_name = "sample_wallet1.json"
    second_wallet_name = "sample_wallet2.json"
    # Create a sample blockchain and save it using the first User instance
    user1 = User(
        pk,
        sk,
        wallet=create_sample_light_blockchain(pk, sk),
        wallet_filename=first_wallet_name)
    user1.save_wallet()

    # Load the blockchain from the saved file using a second User instance and save to a new file
    user2 = User(pk, sk, wallet_filename=first_wallet_name)
    user2.load_wallet()
    user2.wallet_filename = second_wallet_name
    user2.save_wallet()

    # Load files and verify they are identical
    with (open("../data/sample_wallet1.json", "r") as f1,
          open("../data/sample_wallet2.json", "r") as f2):
        blockchain_data_1 = json.load(f1)
        blockchain_data_2 = json.load(f2)

    assert blockchain_data_1 == blockchain_data_2, "Loaded blockchain data does not match saved data"
    logger.info("core data saved and loaded successfully and files match.")


if __name__ == "__main__":
    assertion_check()
