import hashlib
import multiprocessing
from logging_utils import setup_logger
from dini_settings import MinerSettings
from Blockchain.block import Block, create_sample_block, MINE_SUCCESS_ERROR

# Setup logger for file
logger = setup_logger("mining_module")

HASH_VALIDATION_ERROR = "Calculated hash should match the expected hash"


def mine_worker(block_data, start_nonce, end_nonce, difficulty, new_block_event, result_queue):
    """
    Mines the block within a specified nonce range by working with serialized block data.
    If a valid hash is found, it is put into the result queue.
    This function also stops if a new block event is detected.

    :param block_data: The serialized block data (excluding nonce) to be hashed.
    :param start_nonce: The starting nonce for this mining process.
    :param end_nonce: The ending nonce for this mining process.
    :param difficulty: The difficulty level, representing the required number of leading zeros.
    :param new_block_event: An event that stops the mining if another block is mined first.
    :param result_queue: A queue to send the mined block (with nonce) once a valid hash is found.
    :return: None
    """
    target = "0" * difficulty
    max_trailing_zeros = 0
    best_hash = None

    for nonce in range(start_nonce, end_nonce):
        if new_block_event.is_set():
            logger.info("New block detected, worker stopping.")
            return

        try:
            # Append the nonce to the serialized block data for hashing
            block_string = f"{block_data}{nonce}"
            block_hash = hashlib.sha256(block_string.encode()).hexdigest()

            # Check if block is mined (hash meets difficulty)
            if block_hash[:difficulty] == target:
                result_queue.put((block_hash, nonce))  # Put hash and nonce in result queue
                new_block_event.set()  # Notify other workers to stop
                logger.info("Thread %s mined a valid block! Nonce: %d, Hash: %s",
                            multiprocessing.current_process().name, nonce, block_hash)
                return

            # Log progress every 100,000 attempts
            if nonce % 100000 == 0:
                trailing_zeros = len(block_hash) - len(block_hash.rstrip("0"))
                if trailing_zeros > max_trailing_zeros:
                    max_trailing_zeros = trailing_zeros
                    best_hash = block_hash
                logger.debug("Worker %s nonce %d: Best hash so far: %s (Trailing zeros: %d)",
                             multiprocessing.current_process().name, nonce, best_hash, max_trailing_zeros)

        except Exception as e:
            logger.error("Error occurred in mine_worker: %s", e)


def start_mining_processes(block_data, difficulty, new_block_event):
    """
    Starts multiple processes to mine the block. Each process mines within a unique nonce range
    and will stop if a new block is mined by another process.

    :param block_data: The block object to be mined.
    :param difficulty: Difficulty level indicating the number of leading zeros required in the hash.
    :param new_block_event: Event to stop all mining processes if a new block is found.
    :return: A tuple containing the list of processes and the result queue.
    """
    result_queue = multiprocessing.Queue()
    processes = []
    nonce_step = MinerSettings.PROCESS_RANGE  # Define the range each worker will mine (customize as needed)

    for i in range(MinerSettings.PROCESSES_NUMBER):
        start_nonce = i * nonce_step
        end_nonce = (i + 1) * nonce_step
        try:
            p = multiprocessing.Process(target=mine_worker,
                                        args=(block_data, start_nonce, end_nonce, difficulty, new_block_event, result_queue))
            processes.append(p)
            p.start()
            logger.info("Started mining process for nonce range %d-%d", start_nonce, end_nonce)
        except Exception as e:
            logger.error("Error starting mining process for range %d-%d: %s", start_nonce, end_nonce, e)

    return processes, result_queue


def terminate_processes(processes):
    """
    Terminates all active mining processes gracefully and waits for them to exit.

    :param processes: List of active mining processes.
    :return: None
    """
    for process in processes:
        try:
            process.terminate()
            process.join()  # Wait for the process to fully terminate
            logger.info("Terminated process %s", process.name)
        except Exception as e:
            logger.error("Error terminating process %s: %s", process.name, e)
    logger.info("All mining processes terminated.")


def assertion_check():
    """
    Performs assertion checks to ensure the mining functions work as expected.

    :return: None
    """
    logger.info("Starting assertion checks for mining functions...")

    # Create a sample Block instance
    test_block = create_sample_block()
    difficulty = MinerSettings.DIFFICULTY_LEVEL
    new_block_event = multiprocessing.Event()
    new_block_event.clear()

    # Serialize the block data (without nonce)
    serialized_transactions = ''.join(repr(tx) for tx in test_block.transactions)
    block_data = f"{test_block.previous_hash}{serialized_transactions}{test_block.timestamp}"

    # Check mine_worker in a small range and confirm block is found
    result_queue = multiprocessing.Queue()
    start_nonce, end_nonce = 0, 1000
    local_difficulty = 1
    mine_worker(block_data, start_nonce, end_nonce, local_difficulty, new_block_event, result_queue)
    mined_result = result_queue.get() if not result_queue.empty() else None
    assert mined_result is not None, "Mined block should be present in the result queue."
    mined_hash, mined_nonce = mined_result
    assert mined_hash[:local_difficulty] == "0" * local_difficulty, MINE_SUCCESS_ERROR
    logger.info("Checking da big ones")

    # Test start_mining_processes and terminate_processes
    processes, _ = start_mining_processes(block_data, difficulty, new_block_event)
    assert len(processes) == MinerSettings.PROCESSES_NUMBER, "Incorrect number of processes started."
    terminate_processes(processes)
    for process in processes:
        assert not process.is_alive(), "Process should be terminated."

    logger.info("All assertions passed for mining functions.")


def check_straight_hash(string):
    """
    Calculates the SHA-256 hash of a given string.

    :param string: The string to hash.
    :return: The SHA-256 hash as a hex string.
    """
    block_hash = hashlib.sha256(string.encode()).hexdigest()
    return block_hash


# Run assertion checks if this file is executed as main
if __name__ == "__main__":
    assertion_check()


