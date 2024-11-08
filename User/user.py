from Bootstrap.bootstrap import Bootstrap
import json
import os
from Blockchain.blockchain import Blockchain, create_sample_blockchain
from Blockchain.transaction import Transaction, get_sk_pk_pair
from dini_settings import MsgTypes, MsgSubTypes, File
from logging_utils import setup_logger

logger = setup_logger("user")


class User(Bootstrap):
    """
    implements two abilities.
    Firstly, he handles blockchain updating and file saving.
    Secondly, creating a function to broadcast a transaction which he made.
    *Note: blockchain handling might be transferred to miner, in case of wallet servers.
    """
    def __init__(self, sk_pk=None, blockchain=None, filename=None):
        super().__init__(False)
        if sk_pk:
            self.private_key = sk_pk[0]
            self.public_key = sk_pk[1]
        else:
            self.private_key, self.public_key = get_sk_pk_pair()
        self.filename = File.BLOCKCHAIN_FILE_NAME if filename is None else filename
        self.blockchain = blockchain if blockchain else self.load_blockchain()

    def __del__(self):
        self.save_blockchain()

    def handle_block_request(self):
        print("user handling peer request")

    def handle_block_send(self, params):
        print("user handling block send")

    def handle_transaction_send(self, params):
        raise NotImplementedError("user does not handle transactions")

    def make_transaction(self, address, amount):
        transaction = Transaction(self.public_key, address, amount)
        transaction.sign_transaction(self.private_key)
        self.send_distributed_message(MsgTypes.SEND_OBJECT, MsgSubTypes.TRANSACTION, transaction)

    def save_blockchain(self):
        """
        Saves the current blockchain to a file in JSON format.
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

        :return: True if there's a blockchain file.
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    blockchain_data = json.load(f)
                    self.blockchain = Blockchain.from_dict(blockchain_data)
                logger.info(f"Blockchain loaded from {self.filename}")
            except Exception as e:
                logger.error(f"Error loading blockchain: {e}")
            finally:
                return True
        else:
            logger.warning(f"No blockchain file found at {self.filename}, initializing new blockchain.")
            return False

    def request_update_blockchain(self, current_block_hash):
        """
        Requests a specific block from peers.

        :param current_block_hash: The hash of the latest block the user has
        """
        self.send_distributed_message(MsgTypes.REQUEST_OBJECT, MsgSubTypes.BLOCK, current_block_hash)
        logger.info(f"Requesting updates with latest hash: {current_block_hash}")

    def add_block_to_blockchain(self, block):
        """
        Adds a block to the blockchain and saves the updated chain.

        :param block: Block to add.
        """
        self.blockchain.add_block(block)
        self.save_blockchain()

