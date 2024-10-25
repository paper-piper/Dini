from Block import Block
from logging_utils import setup_logger

# Setup logger for file
logger = setup_logger("blockchain_module")

# Constants for assertion error messages
GENESIS_BLOCK_ERROR = "Genesis block should be the first block in the chain"
LATEST_BLOCK_ERROR = "Latest block should match the last block in the chain"
BLOCKCHAIN_VALIDITY_ERROR = "Blockchain should be valid after adding a new block"


class Blockchain:
    """
    Represents a blockchain, containing a series of blocks linked together. It provides
    methods to add new blocks, validate the chain, and retrieve the latest block.
    """

    def __init__(self, difficulty=4):
        """
        Initialize a Blockchain instance with a specified mining difficulty and create the genesis block.

        :param difficulty: The mining difficulty, indicating the number of leading zeros required in the block hash.
        """
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        logger.info("Blockchain created with initial difficulty: %d", difficulty)

    def create_genesis_block(self):
        """
        Create the first block in the blockchain.

        :return: The genesis block with a predefined "Genesis Block" transaction.
        """
        genesis_block = Block("0", ["Genesis Block"])
        logger.info("Genesis block created with hash: %s", genesis_block.hash)
        return genesis_block

    def get_latest_block(self):
        """
        Retrieve the most recent block in the chain.

        :return: The last block in the chain.
        """
        latest_block = self.chain[-1]
        logger.debug("Retrieved latest block with hash: %s", latest_block.hash)
        return latest_block

    def add_block(self, new_block):
        """
        Add a new block to the chain after mining it with the specified difficulty.

        :param new_block: The block to be added to the blockchain.
        :return: None
        """
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        logger.info("New block added with hash: %s", new_block.hash)

    def is_chain_valid(self):
        """
        Check the validity of the blockchain by ensuring each block's hash is correct and that each block points
        to the correct previous block.

        :return: True if the blockchain is valid; otherwise, False.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check if the current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                logger.warning("Block hash mismatch at index %d", i)
                return False

            # Check if the previous hash is correctly set
            if current_block.previous_hash != previous_block.hash:
                logger.warning("Previous hash mismatch at index %d", i)
                return False

        logger.info("Blockchain validation succeeded.")
        return True

def assertion_check():
    """
    Performs various assertions to verify the functionality of the Blockchain class.

    :return: None
    """
    # Initialize blockchain with default difficulty
    blockchain = Blockchain()

    # Check genesis block
    assert blockchain.chain[0].transactions == ["Genesis Block"], GENESIS_BLOCK_ERROR

    # Check retrieval of latest block
    assert blockchain.get_latest_block() == blockchain.chain[-1], LATEST_BLOCK_ERROR

    # Add new block and verify blockchain validity
    new_block = Block(blockchain.get_latest_block().hash, ["Transaction 1"])
    blockchain.add_block(new_block)
    assert blockchain.is_chain_valid(), BLOCKCHAIN_VALIDITY_ERROR

    # Add another block and check validity again
    another_block = Block(blockchain.get_latest_block().hash, ["Transaction 2"])
    blockchain.add_block(another_block)
    assert blockchain.is_chain_valid(), BLOCKCHAIN_VALIDITY_ERROR

    logger.info("All assertions passed for Blockchain class.")


if __name__ == "__main__":
    assertion_check()
