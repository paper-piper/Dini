from core.block import Block, create_sample_block
from core.transaction import Transaction
from utils.logging_utils import setup_basic_logger
from utils.config import MinerSettings, BlockChainSettings, KeysSettings
from utils.keys_manager import load_key
# Setup logger for file
logger = setup_basic_logger()

# Constants for assertion error messages
GENESIS_BLOCK_ERROR = "Genesis block should be the first block in the chain"
LATEST_BLOCK_ERROR = "Latest block should match the last block in the chain"
BLOCKCHAIN_VALIDITY_ERROR = "core should be valid after adding a new block"


class Blockchain:
    """
    Represents a blockchain, containing a series of blocks linked together. It provides
    methods to add new blocks, validate the chain, and retrieve the latest block.
    """

    def __init__(self):
        """
        Initialize a core instance with a specified mining difficulty and create the genesis block.
        """
        self.chain = [self.create_genesis_block()]
        logger.info("core created")

    def to_dict(self):
        return {
            "chain": [block.to_dict() for block in self.chain],
        }

    @classmethod
    def from_dict(cls, data):
        blockchain = cls()
        blockchain.chain = [Block.from_dict(block_data) for block_data in data["chain"]]
        return blockchain

    @staticmethod
    def create_genesis_block():
        """
        Create the first block in the blockchain with unique genesis transaction properties.
        :return: The genesis block with a predefined "Genesis Block" transaction.
        """
        # Generate keys for the genesis block transaction
        genesis_private_key = load_key(KeysSettings.GEN_SK)
        genesis_public_key = load_key(KeysSettings.GEN_PK)

        # Create a unique genesis transaction
        genesis_transaction = Transaction(genesis_public_key, genesis_public_key, 0)
        genesis_transaction.sign_transaction(genesis_private_key)
        genesis_block = Block(BlockChainSettings.FIRST_HASH, [genesis_transaction], timestamp="time-zero")
        genesis_block.hash = genesis_block.calculate_hash()  # Genesis block is pre-mined
        logger.info("Genesis block created: %s", genesis_block)
        return genesis_block

    def get_latest_block(self):
        """
        Retrieve the most recent block in the chain.

        :return: The last block in the chain.
        """
        latest_block = self.chain[-1]
        logger.debug("Retrieved latest block: %s", latest_block)
        return latest_block

    def filter_and_add_block(self, new_block):
        """
        Add a new block to the chain after mining it with the specified difficulty.
        :param new_block: The block to be added to the blockchain.
        :return: True if block valid and added, else False
        """
        # Check if the block has a valid hash for the difficulty level
        if new_block.hash is None or new_block.hash[:new_block.difficulty] != "0" * new_block.difficulty:
            logger.error("Failed to add block: Block is not mined or does not meet the difficulty requirements.")
            return False

        if new_block.previous_hash != self.get_latest_block().hash:
            logger.error("Failed to add block: block previous hash does not match latest hash")
            return False

        if not new_block.validate_block():
            logger.error("Failed to add block: Contains invalid transactions.")
            return False

        self.chain.append(new_block)
        logger.info("New block added: %s", new_block)
        return True

    def get_blocks_after(self, latest_hash):
        """
        Retrieve all blocks from the blockchain starting after the block with the given hash.
        :param latest_hash: The hash of the last known block.
        :return: A list of blocks after the specified hash.
        """
        blocks = []
        found = False

        for block in self.chain:
            if found:  # Start collecting blocks after the latest_hash block
                blocks.append(block)
            elif block.hash == latest_hash:  # Find the block with the latest_hash
                found = True

        if not found:
            logger.warning("Hash not found in the blockchain: %s", latest_hash)

        return blocks

    def create_sub_blockchain(self, latest_hash):
        """
        Create a new core object with all blocks following the block with the given hash.
        :param latest_hash: The hash of the last known block.
        :return: A new core object containing only the subsequent blocks.
        """
        new_blockchain = Blockchain()
        new_blockchain.chain.extend(self.get_blocks_after(latest_hash))  # Add subsequent blocks

        logger.info("Created a sub-blockchain with %d blocks starting after hash: %s",
                    len(new_blockchain.chain) - 1, latest_hash)

        return new_blockchain

    def is_chain_valid(self):
        """
        Check the validity of the blockchain by ensuring each block's hash is correct and that each block points
        to the correct previous block, while also validating each block's transactions.

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

            # Validate transactions within the block
            if not current_block.validate_block():
                logger.warning("Block validation failed due to invalid transaction at index %d", i)
                return False

        logger.info("core validation succeeded.")
        return True


def assertion_check():
    """
    Performs various assertions to verify the functionality of the core class.
    :return: None
    """
    blockchain = create_sample_blockchain()

    # Add mined block to the blockchain and validate the chain's integrity
    assert blockchain.is_chain_valid(), BLOCKCHAIN_VALIDITY_ERROR

    logger.info("All assertions passed for core class.")


def create_sample_blockchain(
        difficulty=MinerSettings.DIFFICULTY_LEVEL,
        blocks_num=2,
        transactions_nums=None,
        transactions_ranges=None
):
    if transactions_ranges is None:
        transactions_ranges = [[10, 20], [15, 10, 30]]
    if transactions_nums is None:
        transactions_nums = [2, 3]

    if len(transactions_nums) != blocks_num:
        raise "transactions nums does not much the blocks num"

    blockchain = Blockchain()
    previews_hash = blockchain.get_latest_block().calculate_hash()
    for i in range(blocks_num):
        block = create_sample_block(transactions_nums[i], transactions_ranges[i], previews_hash, difficulty)

        # Manually mine the block by finding a valid nonce and hash
        target = "0" * block.difficulty
        while block.hash is None or block.hash[:block.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()

        # Verify that the mined block meets the difficulty requirements
        assert block.hash[:block.difficulty] == target, "Mining failed"

        previews_hash = block.calculate_hash()
        blockchain.filter_and_add_block(block)

    return blockchain


if __name__ == "__main__":
    assertion_check()
