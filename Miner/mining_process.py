import threading
from queue import Queue
from logging_utils import setup_logger
from dini_Settings import MinerSettings
from Blockchain.block import Block, create_sample_block

# Setup logger for file
logger = setup_logger("mining_module")

HASH_VALIDATION_ERROR = "Calculated hash should match the expected hash"


def mine_worker(block, start_nonce, end_nonce, difficulty, new_block_event, result_queue):
    """
    Mines the block within a specified nonce range, checking for a valid hash.
    If a valid hash is found, it is put into the result queue.
    This function also stops if a new block event is detected.

    :param block: The block to be mined, containing the necessary fields for mining.
    :param start_nonce: The starting nonce for this mining thread.
    :param end_nonce: The ending nonce for this mining thread.
    :param difficulty: The difficulty level, representing the required number of leading zeros.
    :param new_block_event: An event that stops the mining if another block is mined first.
    :param result_queue: A queue to send the mined block once a valid hash is found.
    :return: None
    """
    target = "0" * difficulty
    max_trailing_zeros = 0
    best_hash = None

    for nonce in range(start_nonce, end_nonce):
        # Check the new_block_event frequently to stop if another thread finds a solution
        if new_block_event.is_set():
            logger.info("New block detected, worker stopping.")
            return

        try:
            block.nonce = nonce
            block.hash = block.calculate_hash()

            # Check if block is mined
            if block.hash[:difficulty] == target:
                # Set the event so all threads are notified to stop
                new_block_event.set()
                result_queue.put(block)
                logger.info("Thread %s mined a valid block! Nonce: %d, Hash: %s",
                            threading.current_thread().name, nonce, block.hash)
                return

            # Periodic logging and event check every 10,000 nonces
            if nonce % 10000 == 0:
                trailing_zeros = len(block.hash) - len(block.hash.rstrip("0"))
                if trailing_zeros > max_trailing_zeros:
                    max_trailing_zeros = trailing_zeros
                    best_hash = block.hash
                #logger.debug("Worker %s nonce %d: Best hash so far: %s (Trailing zeros: %d)",
                #             threading.current_thread().name, nonce, best_hash, max_trailing_zeros)
        except Exception as e:
            logger.error("Error occurred in mine_worker: %s", e)


def start_mining_threads(block, difficulty, new_block_event):
    """
    Starts multiple threads to mine the block. Each thread mines within a unique nonce range
    and will stop if a new block is mined by another thread.

    :param block: The block object to be mined.
    :param difficulty: Difficulty level indicating the number of leading zeros required in the hash.
    :param new_block_event: Event to stop all mining threads if a new block is found.
    :return: A tuple containing the list of threads and the result queue.
    """
    result_queue = Queue()
    threads = []
    nonce_step = MinerSettings.PROCESS_RANGE  # Define the range each worker will mine (customize as needed)

    for i in range(MinerSettings.PROCESSES_NUMBER):
        start_nonce = i * nonce_step
        end_nonce = (i + 1) * nonce_step
        try:
            t = threading.Thread(target=mine_worker,
                                 args=(block, start_nonce, end_nonce, difficulty, new_block_event, result_queue))
            threads.append(t)
            t.start()
            logger.info("Started mining thread for nonce range %d-%d", start_nonce, end_nonce)
        except Exception as e:
            logger.error("Error starting mining thread for range %d-%d: %s", start_nonce, end_nonce, e)

    return threads, result_queue


def terminate_threads(threads):
    """
    Waits for all active mining threads to finish gracefully.

    :param threads: List of active mining threads.
    :return: None
    """
    for thread in threads:
        try:
            thread.join()
            logger.info("Thread %s completed", thread.name)
        except Exception as e:
            logger.error("Error joining thread %s: %s", thread.name, e)
    logger.info("All mining threads completed.")


def assertion_check():
    """
    Performs assertion checks to ensure the mining functions work as expected.

    :return: None
    """
    logger.info("Starting assertion checks for mining functions...")

    # Create a sample Block instance
    test_block = create_sample_block()
    difficulty = MinerSettings.DIFFICULTY_LEVEL
    new_block_event = threading.Event()
    new_block_event.clear()

    # Verify the hash calculation and initial state of the block
    initial_hash = test_block.calculate_hash()
    assert test_block.hash is None, HASH_VALIDATION_ERROR  # Ensure no hash is set initially
    assert initial_hash == test_block.calculate_hash(), HASH_VALIDATION_ERROR

    # Check mine_worker in a small range and confirm block is found
    result_queue = Queue()
    start_nonce, end_nonce = 0, 1000
    check_difficulty = 2
    mine_worker(test_block, start_nonce, end_nonce, check_difficulty, new_block_event, result_queue)
    mined_block = result_queue.get() if not result_queue.empty() else None
    assert mined_block is not None, "Mined block should be present in the result queue."
    assert mined_block.hash[:check_difficulty] == "0" * check_difficulty, "Mined block hash should meet difficulty target."

    # Test start_mining_threads and terminate_threads
    new_block_event.clear()
    threads, _ = start_mining_threads(test_block, difficulty, new_block_event)
    assert len(threads) == MinerSettings.PROCESSES_NUMBER, "Incorrect number of threads started."
    terminate_threads(threads)
    for thread in threads:
        assert not thread.is_alive(), "Thread should be completed."


    logger.info("All assertions passed for mining functions.")


# Run assertion checks if this file is executed as main
if __name__ == "__main__":
    assertion_check()
