import json
import threading
from utils.config import MsgTypes, MsgSubTypes
from utils.logging_utils import setup_logger
from network.user import User
from mempool import Mempool
from multiprocess_mining import MultiprocessMining
from core.transaction import get_sk_pk_pair, create_sample_transaction
from core.block import Block
from core.blockchain import create_sample_blockchain
# Setup logger for file
logger = setup_logger("miner")


class Miner(User):
    """
    adds block mining essentially , which has many complications in it but that is it.
    """

    def __init__(self, public_key, secret_key, blockchain=None, filename=None, mempool=None):
        """
        Initialize a Miner instance with a blockchain reference, mempool, difficulty level, and necessary sync elements.

        :param blockchain: The core object this miner will add mined blocks to.
        :param mempool: A list or object representing the transaction pool from which this miner selects transactions.
        """
        super().__init__(public_key, secret_key, blockchain, filename, user=False)

        self.mempool = mempool if mempool else Mempool()
        self.mempool_lock = threading.Lock()
        self.multi_miner = MultiprocessMining()
        self.new_block_event = threading.Event()
        self.currently_mining = threading.Event()

    def start_mining(self, blocks_num=-1):
        if self.currently_mining.is_set():
            logger.info("can't start mining again, process already mining, ")
        self.currently_mining.set()
        threading.Thread(target=self.mine_blocks, args=(blocks_num,)).start()

    def stop_mining(self):
        self.currently_mining.clear()
        self.new_block_event.set()

    def serve_blockchain_request(self, latest_hash):
        """
        Handles requests from peers to update the blockchain.
        """
        blockchain = self.blockchain.create_sub_blockchain(latest_hash)
        return blockchain

    def process_transaction_data(self, params):
        # assuming the first parameter is the transaction
        transaction = params[0]
        if not transaction.verify_signature():
            logger.warning("Found unverified transaction")
            return
        with self.mempool_lock:
            self.mempool.add_transactions([transaction])

        print("miner handling transaction send")

    def process_blockchain_data(self, params):
        super().process_blockchain_data(params)
        # only if new blocks
        self.new_block_event.set()

    def process_block_data(self, block):
        """
        Adds a block to the blockchain and saves the updated chain.

        :param block: Block to add.
        :return: None
        """
        super().process_block_data(block)
        # only if new blocks
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
                logger.info("Mining interrupted by a new block, resetting mining process")
            else:
                self.blockchain.filter_and_add_block(mined_block)
                blocks_num -= 1
                self.send_distributed_message(MsgTypes.SEND_OBJECT, MsgSubTypes.BLOCK, mined_block)
                logger.info("Block mined and added to blockchain successfully. "
                            "Nonce: %d, Hash: %s", mined_block.nonce, mined_block.hash)

    def create_block(self):
        # Lock mempool to prevent transaction modifications
        with self.mempool_lock:
            # build new block
            transactions = self.mempool.select_transactions()
            if len(transactions) == 0:
                return None
            previous_hash = self.blockchain.get_latest_block().hash
            block = Block(previous_hash, transactions)
            return block


def assertion_checks():
    # first, ensure that blockchain saving also works for miner with regular blockchain
    pk, sk = get_sk_pk_pair()
    miner1 = Miner(pk, sk, create_sample_blockchain(), filename="../../data/sample_blockchain_1.json")
    miner1.save_blockchain()

    # Load the blockchain from the saved file using a second User instance and save to a new file
    miner2 = Miner(pk, sk, filename="../../data/sample_blockchain_1.json")
    miner2.load_blockchain()
    miner2.filename = "../../data/sample_blockchain_2.json"
    miner2.save_blockchain()

    # Load files and verify they are identical
    with open("../../data/sample_blockchain_1.json", "r") as f1, open("../../data/sample_blockchain_2.json", "r") as f2:
        blockchain_data_1 = json.load(f1)
        blockchain_data_2 = json.load(f2)

    assert blockchain_data_1 == blockchain_data_2, "Loaded blockchain data does not match saved data"
    logger.info("core data saved and loaded successfully and files match.")

    # secondly, check mine function
    miner1.process_transaction_data([create_sample_transaction()])
    miner1.start_mining(1)


if __name__ == "__main__":
    assertion_checks()
