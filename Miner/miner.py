import threading
import queue
import time
from Blockchain.blockchain import Blockchain, Block, Transaction
from mempool import Mempool
from logging_utils import setup_logger
from dini_Settings import BlockSettings
from mining_process import start_mining_processes, terminate_processes

# Setup logger for file
logger = setup_logger("miner_module")


class Miner:
    """
    Represents a miner responsible for mining blocks, receiving new blocks, and syncing with other miners.
    """

    def __init__(self, public_key, private_key, blockchain, mempool):
        """
        Initialize a Miner instance with a blockchain reference, mempool, difficulty level, and necessary sync elements.

        :param blockchain: The Blockchain object this miner will add mined blocks to.
        :param mempool: A list or object representing the transaction pool from which this miner selects transactions.
        """
        self.public_key = public_key
        self.private_key = private_key

        self.blockchain = blockchain
        self.mempool = mempool
        self.difficulty = blockchain.difficulty
        self.queue = queue.Queue()  # Queue for receiving blocks from other miners

        self.mempool_lock = threading.Lock()
        self.new_block_event = threading.Event()
        self.current_block = None
        self.mining_active = False

        # Start block processing and receiving threads
        threading.Thread(target=self.get_blocks, daemon=True).start()
        threading.Thread(target=self.process_blocks, daemon=True).start()

    def get_blocks(self):
        """
        Listens for new incoming blocks and adds them to the queue for processing.
        Runs indefinitely on its own thread.
        """
        # TODO: add try/except
        while True:
            # Waits for and simulates receiving a new block
            new_block = self.receive_block()  # receive_block function to be defined for actual communication
            if new_block:
                self.queue.put(new_block)

    def process_blocks(self):
        """
        Processes blocks from the queue, validates them, updates the blockchain, and notifies the mining thread if needed.
        Runs indefinitely on its own thread.
        """
        while True:
            new_block = self.queue.get()  # Blocking until a block is available
            # check if the block is valid, if so signal the new block event
            if new_block.validate_transactions() and self.blockchain.add_block(new_block):
                with self.mempool_lock:
                    # Update the mempool to remove processed transactions
                    self.mempool.update(new_block.transactions)
                self.new_block_event.set()  # Signal the mining thread to restart with new transactions
                logger.info(f"New block validated and added to the blockchain: {new_block}")

    def mine_block(self):
        """
        Mines a block by selecting transactions and performing Proof of Work, restarting if a new block arrives.
        """
        while self.mining_active:
            self.new_block_event.clear()  # Reset the event since we're about to start mining
            # Lock mempool to prevent transaction modifications
            with self.mempool_lock:
                # build new block
                transactions = self.mempool.select_transactions()
                self.add_bonus_transaction(transactions)
                previous_hash = self.blockchain.get_latest_block().hash
                self.current_block = Block(previous_hash, transactions)

            # Begin mining with the given difficulty
            mined_block = self.mine(self.current_block)

            # If mining completes before a new block event, add the block
            if self.new_block_event.is_set():
                logger.info("Mining interrupted by a new block, resetting mining process")
            else:
                self.blockchain.add_block(mined_block)
                self.broadcast_block(mined_block)
                logger.info("Block mined and added to blockchain successfully. "
                            "Nonce: %d, Hash: %s", mined_block.nonce, mined_block.hash)

    def mine(self, block):
        """
        Initiates the mining process using multiple processes to increase efficiency.
        """
        processes, result_queue = start_mining_processes(
            block, difficulty=self.difficulty, new_block_event=self.new_block_event
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
            terminate_processes(processes)

        return mined_block if mined_block else block  # Return mined block or the original if aborted

    def broadcast_block(self, block):
        pass

    def add_bonus_transaction(self, transactions):
        bonus_transaction = Transaction(BlockSettings.BONUS_PK, self.public_key, BlockSettings.BONUS_AMOUNT)
        transactions.insert(0, bonus_transaction)
