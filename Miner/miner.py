import threading
import queue
from dini_settings import MsgTypes, MsgSubTypes
from Blockchain.blockchain import Block
from logging_utils import setup_logger
import multiprocess_mining
from User.user import User
# Setup logger for file
logger = setup_logger("miner")


class Miner(User):
    """
    adds block mining essentially , which has many complications in it but that is it.
    """

    def __init__(self, sk_pk, blockchain=None, filename=None, mempool=None):
        """
        Initialize a Miner instance with a blockchain reference, mempool, difficulty level, and necessary sync elements.

        :param blockchain: The Blockchain object this miner will add mined blocks to.
        :param mempool: A list or object representing the transaction pool from which this miner selects transactions.
        """
        super().__init__(sk_pk, blockchain, filename)

        self.mempool = mempool

        self.mempool_lock = threading.Lock()
        self.new_block_event = threading.Event()
        self.currently_mined_block = None
        self.currently_mining = threading.Event()

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
            self.mempool.add_transactions(transaction)

        print("miner handling transaction send")

    def process_blockchain_data(self, params):
        super().process_blockchain_data(params)
        self.new_block_event.set()

    def mining_process(self):
        """
        Mines a block by selecting transactions and performing Proof of Work, restarting if a new block arrives.
        """
        while self.currently_mining.is_set():
            self.new_block_event.clear()  # Reset the event since we're about to start mining

            # check for available transaction until a block is made
            has_pending_transactions = False
            while not has_pending_transactions:
                has_pending_transactions = self.create_block()  # sets the currently mined block to a new block

            # Begin mining with the given difficulty
            mined_block = self.mine_block(self.currently_mined_block, self.blockchain.difficulty)

            # if the mining was interrupted, the mined block is None
            if not mined_block:
                logger.info("Mining interrupted by a new block, resetting mining process")
            else:
                self.blockchain.filter_and_add_block(mined_block)
                self.send_distributed_message(MsgTypes.SEND_OBJECT, MsgSubTypes.BLOCK, mined_block)
                logger.info("Block mined and added to blockchain successfully. "
                            "Nonce: %d, Hash: %s", mined_block.nonce, mined_block.hash)

    def create_block(self):
        # Lock mempool to prevent transaction modifications
        with self.mempool_lock:
            # build new block
            transactions = self.mempool.select_transactions()
            if transactions is None:
                return False
            previous_hash = self.blockchain.get_latest_block().hash
            self.currently_mined_block = Block(previous_hash, transactions)
            return True

    def start_mining(self):
        if self.currently_mining.is_set():
            logger.info("can't start mining again, process already mining, ")
        self.currently_mining.set()
        threading.Thread(target=self.mining_process()).start()

    def stop_mining(self):
        self.currently_mining.clear()

    def mine_block(self, block, difficulty):
        """
        Mines the given block by finding a valid hash that meets the required difficulty.
        :param block: The Block object to be mined.
        :param difficulty: the difficulty
        :return: The mined Block object with a valid hash.
        """
        target = "0" * difficulty
        best_hash = None
        max_trailing_zeros = 0
        logger.info("Starting mining with difficulty %d...", difficulty)
        while block.hash[:difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()
            # Count trailing zeros in the current hash
            trailing_zeros = len(block.hash) - len(block.hash.rstrip("0"))
            # Update the best hash if the current hash has more trailing zeros
            if trailing_zeros > max_trailing_zeros:
                max_trailing_zeros = trailing_zeros
                best_hash = block.hash
            # Log the best hash every 100,000 attempts
            if block.nonce % 100000 == 0:
                logger.debug("Mining attempt %d, Best hash so far: %s (Trailing zeros: %d)",
                             block.nonce, best_hash,  max_trailing_zeros)
            # Check if a new block has arrived
            if self.new_block_event.is_set():
                logger.info("New block detected, aborting current mining process")
                return None

        return block

    def mine_block_multiprocess(self, block):
        """
        Initiates the mining process using multiple processes to increase efficiency.
        """
        processes, result_queue = multiprocess_mining.start_mining_processes(
            block, difficulty=self.blockchain.difficulty, new_block_event=self.new_block_event
        )

        mined_block = None
        try:
            # Wait for a result or new block detection
            while mined_block is None and not self.new_block_event.is_set():
                try:
                    mined_block = result_queue.get(timeout=1)  # Check queue for mined block
                except queue.Empty:
                    continue

            if mined_block:
                logger.info("Block mined successfully.")
            else:
                logger.info("Mining aborted due to new block.")

        finally:
            multiprocess_mining.terminate_processes(processes)

        return mined_block if mined_block else block  # Return mined block or the original if aborted


if __name__ == "__main__":
    pass
