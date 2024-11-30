import multiprocessing
from core.block import create_sample_block
from utils.config import BlockSettings
from utils.logging_utils import setup_logger
import time
logger = setup_logger()


class MultiprocessMining:
    def __init__(self, num_processes=BlockSettings.PROCESSES_NUMBER):
        """
        Initialize the MultiprocessMining class.
        :param num_processes: Number of processes to use for mining.
        """
        self.num_processes = num_processes
        self.new_block_event = multiprocessing.Event()

    @staticmethod
    def _mine_range(block_dict, difficulty, start_nonce, end_nonce, new_block_event, result_queue, block_class):
        """
        Worker function to mine a block within a specific nonce range.
        :param block_dict: Serialized Block object (dictionary) to be mined.
        :param difficulty: The mining difficulty.
        :param start_nonce: Start of the nonce range.
        :param end_nonce: End of the nonce range.
        :param new_block_event: Event to signal when a new block is found.
        :param result_queue: Queue to store the mined block as a dictionary.
        :param block_class: The Block class to deserialize the block.
        """
        target = "0" * difficulty
        max_trailing_zeros = 0
        best_hash = None

        # Deserialize the block object
        block = block_class.from_dict(block_dict)

        for nonce in range(start_nonce, end_nonce):
            if new_block_event.is_set():
                return  # Stop mining if a new block is detected

            block.nonce = nonce
            block.hash = block.calculate_hash()

            # Check if the hash meets the difficulty
            if block.hash[:difficulty] == target:
                result_queue.put(block.to_dict())  # Store serialized block
                new_block_event.set()
                return

            # Count trailing zeros in the current hash
            trailing_zeros = len(block.hash) - len(block.hash.rstrip("0"))
            if trailing_zeros > max_trailing_zeros:
                max_trailing_zeros = trailing_zeros
                best_hash = block.hash

            # Log the best hash every 100,000 attempts
            if nonce % 100000 == 0 and not nonce == 0:
                #logger.debug("Nonce: %d, Best hash so far: %s (Trailing zeros: %d)",
                #             nonce, best_hash, max_trailing_zeros)
                pass
    def get_block_hash(self, block, difficulty):
        """
        Mines the given block using multiple processes.
        :param block: The Block object to be mined.
        :param difficulty: The mining difficulty.
        :return: The mined Block object with a valid hash, or None if aborted.
        """
        processes = []
        result_queue = multiprocessing.Queue()

        # Serialize the block to a dictionary
        block_dict = block.to_dict()

        # Calculate the nonce range for each process
        nonce_range = 2**32 // self.num_processes  # Adjust for a suitable nonce range
        for i in range(self.num_processes):
            start_nonce = i * nonce_range
            end_nonce = (i + 1) * nonce_range
            process = multiprocessing.Process(
                target=self._mine_range,
                args=(block_dict, difficulty, start_nonce, end_nonce, self.new_block_event, result_queue, type(block))
            )
            processes.append(process)
            process.start()

        # Wait for any process to find a valid hash
        mined_block = None
        try:
            mined_block_dict = result_queue.get(timeout=None)  # Wait indefinitely for a result
            mined_block = type(block).from_dict(mined_block_dict)  # Deserialize the block
        except Exception:
            logger.error("Mining interrupted or no block found.")

        # Signal all processes to terminate and join them
        self.new_block_event.set()
        for process in processes:
            process.join()

        # Reset the event for future mining
        self.new_block_event.clear()
        return mined_block


def assertion_check():
    # Assuming `block` is an instance of your Block class
    miner = MultiprocessMining(num_processes=4)
    mined_block = miner.get_block_hash(create_sample_block(), difficulty=4)

    if mined_block:
        print(f"Successfully mined block with hash: {mined_block.hash}")
    else:
        print("Mining was aborted or failed.")


def test_processes_speeds(start, end, difficulty=5):
    time_list = []
    for i in range(start, end, 1):
        start_time = time.time()
        miner = MultiprocessMining(num_processes=i)
        miner.get_block_hash(create_sample_block(), difficulty=difficulty)
        end_time = time.time()
        elapsed_time = end_time - start_time
        time_list.append(elapsed_time)

    # Pair each time with its original index
    indexed_times = list(enumerate(time_list))

    # Sort the times in ascending order by the time value
    sorted_times = sorted(indexed_times, key=lambda x: x[1])

    # Print the sorted times with their original index
    logger.info("Sorted times:")
    for index, time_value in sorted_times:
        logger.info(f"{index+1}: {time_value:.2f} seconds")


if __name__ == "__main__":
    test_processes_speeds(1, 20)


