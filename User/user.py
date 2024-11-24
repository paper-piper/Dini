from Blockchain.blockchain import Blockchain
from Bootstrap.bootstrap import Bootstrap
import json
import os
from Blockchain.light_blockchain import LightBlockchain
from Blockchain.transaction import Transaction, get_sk_pk_pair
from dini_settings import MsgTypes, MsgSubTypes, File
from logging_utils import setup_logger

logger = setup_logger("user")


class User(Bootstrap):
    """
    Manages user operations including blockchain updating, file saving, and broadcasting transactions.

    :param sk_pk: Tuple containing user's private and public keys, or None to generate new keys.
    :param blockchain: Blockchain object, or None to load from file.
    :param filename: Name of the file where blockchain data is saved. Defaults to the standard blockchain file name.
    """

    def __init__(self, public_key, secret_key, blockchain=None, filename=None):
        super().__init__(False)
        self.public_key = public_key
        self.private_key = secret_key
        self.filename = File.BLOCKCHAIN_FILE_NAME if filename is None else filename
        self.blockchain = blockchain if blockchain else self.load_blockchain()

    def __del__(self):
        self.save_blockchain()

    def process_block_data(self, block):
        """
        Adds a block to the blockchain and saves the updated chain.

        :param block: Block to add.
        :return: None
        """
        self.blockchain.filter_and_add_block(block)
        self.save_blockchain()
        logger.info("Block added to blockchain and saved")

    def process_blockchain_data(self, blockchain):
        """
        Handles the sending of blocks to other peers.

        :param blockchain: Parameters associated with the block send.
        """
        relevant_blocks = blockchain.get_blocks_after()
        for block in relevant_blocks:
            self.process_block_data(block)

    def serve_blockchain_request(self, latest_hash):
        """
        Handles requests from peers to update the blockchain.
        """
        logger.error("User does not handle blockchain updates")
        raise NotImplementedError("user does not handle blockchain updates")

    def process_transaction_data(self, params):
        """
        Raises an error as users do not handle transactions directly.

        :param params: Parameters associated with the transaction send.
        """
        logger.error("User does not handle transactions")
        raise NotImplementedError("user does not handle transactions")

    def make_transaction(self, address, amount):
        """
        Creates a signed transaction and broadcasts it to peers.

        :param address: Recipient's address.
        :param amount: Amount to be transferred.
        """
        transaction = Transaction(self.public_key, address, amount)
        transaction.sign_transaction(self.private_key)
        self.send_distributed_message(MsgTypes.SEND_OBJECT, MsgSubTypes.TRANSACTION, transaction)
        logger.info(f"Transaction made from {self.public_key} to {address} of amount {amount}")

    def save_blockchain(self):
        """
        Saves the current blockchain to a file in JSON format.

        :return: None
        """
        try:
            with open(self.filename, "w") as f:
                json.dump(self.blockchain.to_dict(), f, indent=4)
            logger.info(f"Blockchain saved to {self.filename}")
        except Exception as e:
            logger.error(f"Error saving blockchain: {e}")

    def load_blockchain(self):
        """
        Loads the blockchain from a file if it exists.

        :return: Boolean indicating whether the blockchain was successfully loaded.
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    blockchain_data = json.load(f)
                    # Dynamically determine which blockchain type to use
                    if isinstance(self.blockchain, LightBlockchain):
                        self.blockchain = LightBlockchain.from_dict(blockchain_data)
                    else:
                        self.blockchain = Blockchain.from_dict(blockchain_data)
                logger.info(f"Blockchain loaded from {self.filename}")
                return True
            except Exception as e:
                logger.error(f"Error loading blockchain: {e}")
                return False
        else:
            logger.warning(f"No blockchain file found at {self.filename}, initializing new blockchain.")
            self.blockchain = LightBlockchain(self.public_key) if isinstance(self.blockchain,
                                                                             LightBlockchain) else Blockchain()
            return False

    def request_update_blockchain(self):
        """
        Requests a specific block update from peers.
        :return: None
        """
        latest_hash = self.blockchain.latest_hash if isinstance(self.blockchain, LightBlockchain)\
            else self.blockchain.get_latest_block().hash
        self.send_distributed_message(
            MsgTypes.REQUEST_OBJECT,
            MsgSubTypes.BLOCKCHAIN,
            latest_hash
        )
        logger.info(f"Requesting updates with latest hash: {latest_hash}")


def assertion_check():
    """
    Runs assertions to test the functionality of User class methods related to blockchain saving and loading.

    :return: None
    """
    # Generate key pair for testing
    sk, pk = get_sk_pk_pair()

    # Create a sample blockchain and save it using the first User instance
    user1 = User(sk_pk=(sk, pk), blockchain=c(), filename="sample_blockchain_1.json")
    user1.save_blockchain()

    # Load the blockchain from the saved file using a second User instance and save to a new file
    user2 = User(sk_pk=(sk, pk), filename="sample_blockchain_1.json")
    user2.load_blockchain()
    user2.filename = "sample_blockchain_2.json"
    user2.save_blockchain()

    # Load files and verify they are identical
    with open("sample_blockchain_1.json", "r") as f1, open("sample_blockchain_2.json", "r") as f2:
        blockchain_data_1 = json.load(f1)
        blockchain_data_2 = json.load(f2)

    assert blockchain_data_1 == blockchain_data_2, "Loaded blockchain data does not match saved data"
    logger.info("Blockchain data saved and loaded successfully and files match.")


if __name__ == "__main__":
    assertion_check()
