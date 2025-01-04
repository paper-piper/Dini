import json
import os
import threading
from utils.config import MsgTypes, MsgSubTypes, FilesSettings
from network.user import User
from network.miner.mempool import Mempool
from network.miner.multiprocess_mining import MultiprocessMining
from core.transaction import get_sk_pk_pair, create_sample_transaction
from core.block import Block
from core.blockchain import create_sample_blockchain, Blockchain
from utils.logging_utils import configure_logger


class Miner(User):
    """
    adds block mining essentially , which has many complications in it but that is it.
    """

    def __init__(
            self,
            public_key,
            secret_key,
            blockchain_filename=None,
            blockchain=None,
            mempool=None,
            wallet=None,
            wallet_filename=None,
            port_manager=None,
            ip=None,
            port=None,
            instance_id=None,
            child_dir="Miner"
    ):
        """
        Initialize a miner instance with a blockchain reference, mempool, difficulty level, and necessary sync elements.

        :param blockchain: The core object this miner will add mined blocks to.
        :param mempool: A list or object representing the transaction pool from which this miner selects transactions.
        """

        super().__init__(
            public_key,
            secret_key,
            wallet=wallet,
            wallet_filename=wallet_filename,
            port_manager=port_manager,
            ip=ip,
            port=port,
            instance_id=instance_id,
            child_dir=child_dir
        )

        self.miner_logger = configure_logger(
            class_name="Miner",
            child_dir=child_dir,
            instance_id=f"{self.ip}-{self.port}"
        )
        self.miner_logger.info("Miner logger initialized.")

        self.address = (ip, port)
        self.mempool = mempool if mempool else Mempool(f"{self.ip}-{self.port}", child_dir)
        self.mempool_lock = threading.Lock()
        self.multi_miner = MultiprocessMining(instance_id=f"{self.ip}-{self.port}", child_dir=child_dir)
        self.new_block_event = threading.Event()
        self.currently_mining = threading.Event()
        self.blockchain_filename = blockchain_filename if blockchain_filename else FilesSettings.BLOCKCHAIN_FILE_NAME
        if blockchain:
            self.blockchain = blockchain
            self.save_blockchain()
        else:
            self.blockchain = self.load_blockchain()

    def __del__(self):
        super().__del__()
        self.save_blockchain()

    def start_mining(self, blocks_num=-1):
        if self.currently_mining.is_set():
            self.miner_logger.info(f"can't start mining again, process already mining, ")
        self.currently_mining.set()
        threading.Thread(target=self.mine_blocks, args=(blocks_num,)).start()

    def stop_mining(self):
        self.currently_mining.clear()
        self.new_block_event.set()

    def load_blockchain(self):
        """
        Loads the blockchain from a file if it exists.
        :return: The blockchain if exists, else initialized blockchain
        """
        blockchain_path = os.path.join(FilesSettings.DATA_ROOT_DIRECTORY, self.blockchain_filename)
        if os.path.exists(blockchain_path):
            try:
                with open(blockchain_path, "r") as f:
                    blockchain_data = json.load(f)
                    blockchain = Blockchain.from_dict(blockchain_data)
                self.miner_logger.info(f"core loaded from {blockchain_path}")
                return blockchain
            except Exception as e:
                self.miner_logger.error(f"Error loading blockchain: {e}")
                return False

        self.miner_logger.info(f"No blockchain file found at path {blockchain_path}, initializing new blockchain.")
        return Blockchain()

    def save_blockchain(self):
        """
        Saves the current blockchain to a file in JSON format.
        :return: None
        """
        try:
            blockchain_path = os.path.join(FilesSettings.DATA_ROOT_DIRECTORY, self.blockchain_filename)
            with open(blockchain_path, "w") as f:
                blockchain_dict = self.blockchain.to_dict()
                json.dump(blockchain_dict, f, indent=4)
            self.miner_logger.info(f"core saved to {blockchain_path}")
        except Exception as e:
            self.miner_logger.error(f"Error saving blockchain: {e}")

    def serve_blockchain_request(self, latest_hash):
        """
        Handles requests from peers to update the blockchain.
        """
        blockchain = self.blockchain.create_sub_blockchain(latest_hash)
        self.miner_logger.info(f"received blockchain request, sending blockchain: {blockchain}")
        return blockchain

    def process_transaction_data(self, transaction):
        # first, check if the transaction was already seen
        if self.mempool.has_transaction(transaction):
            return True

        if not transaction.verify_signature():
            self.miner_logger.warning(f"Found unverified transaction")
            return
        with self.mempool_lock:
            self.mempool.add_transactions([transaction])

        self.miner_logger.info(f"added transaction {transaction} to mempool")

    def process_blockchain_data(self, blockchain):
        super().process_blockchain_data(blockchain)

        # bonus: only if new blocks
        self.new_block_event.set()

        # add blockchain to current blockchain
        relevant_blocks = blockchain.get_blocks_after(self.blockchain.get_latest_block().hash)
        valid_blocks = 0
        for block in relevant_blocks:
            if self.blockchain.filter_and_add_block(block):
                valid_blocks += 1

        self.miner_logger.info(f"received blockchain ({blockchain.to_dict()}) send and added {valid_blocks} blocks")

    def process_block_data(self, block):
        """
        Adds a block to the blockchain and saves the updated chain.
        :param block: Block to add.
        :return: None
        """
        super().process_block_data(block)
        # only if new blocks
        self.save_blockchain()
        self.new_block_event.set()

    def mine_blocks(self, blocks_num):
        """
        Mines a block by selecting transactions and performing Proof of Work, restarting if a new block arrives.
        """
        while self.currently_mining.is_set() and blocks_num != 0:
            self.new_block_event.clear()  # Reset the event since we're about to start mining

            # check for available transaction until a block is made
            current_block = self.create_block()
            while current_block is None:
                current_block = self.create_block()

            # Begin mining with the given difficulty
            mined_block = self.multi_miner.get_block_hash(current_block, current_block.difficulty)

            # if the mining was interrupted, the mined block is None
            if not mined_block:
                self.miner_logger.info(f"Mining interrupted by a new block, resetting mining process")
            else:
                self.blockchain.filter_and_add_block(mined_block)
                blocks_num -= 1
                self.send_distributed_message(MsgTypes.RESPONSE_OBJECT, MsgSubTypes.BLOCK, mined_block)
                self.miner_logger.info(f"Block mined and added to blockchain successfully. Block: {mined_block}")

    def create_block(self):
        # Lock mempool to prevent transaction modifications
        with self.mempool_lock:
            # build new block
            transactions = self.mempool.select_transactions()
            if len(transactions) == 0:
                return None
            previous_hash = self.blockchain.get_latest_block().hash
            # create the bonus transaction to reward the miner
            block = Block(previous_hash, transactions)
            # create the tipping transaction at start
            block.add_tipping_transaction(self.public_key)
            block.add_bonus_transaction(self.public_key)
            return block


def assert_file_saving():
    pk, sk = get_sk_pk_pair()
    first_blockchain = "sample_blockchain_1.json"
    second_blockchain = "sample_blockchain_2.json"
    miner1 = Miner(pk, sk, blockchain_filename=first_blockchain,
                   blockchain=create_sample_blockchain())

    # Load the blockchain from the saved file using a second User instance and save to a new file
    miner2 = Miner(pk, sk, blockchain_filename=first_blockchain)
    miner2.load_blockchain()
    miner2.blockchain_filename = second_blockchain
    miner2.save_blockchain()

    # Load files and verify they are identical
    with open("../../data/sample_blockchain_1.json", "r") as f1, open("../../data/sample_blockchain_2.json", "r") as f2:
        blockchain_data_1 = json.load(f1)
        blockchain_data_2 = json.load(f2)

    assert blockchain_data_1 == blockchain_data_2, "Loaded blockchain data does not match saved data"


def assertion_checks():
    # first, ensure that blockchain saving also works for miner with regular blockchain
    assert_file_saving()

    # secondly, check mine function
    sk, pk = get_sk_pk_pair()
    miner = Miner(pk, sk)

    miner.process_transaction_data(create_sample_transaction())
    miner.start_mining(1)


if __name__ == "__main__":
    assert_file_saving()