from Block import Block
from Transaction import Transaction, get_sk_pk_pair
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
        Create the first block in the blockchain with unique genesis transaction properties.
        :return: The genesis block with a predefined "Genesis Block" transaction.
        """
        # Generate keys for the genesis block transaction
        genesis_private_key, genesis_public_key = get_sk_pk_pair()
        _, network_public_key = get_sk_pk_pair()

        # Create a unique genesis transaction
        genesis_transaction = Transaction(genesis_public_key, network_public_key, 0)
        genesis_transaction.sign_transaction(genesis_private_key)
        genesis_block = Block("0", [genesis_transaction])
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

    def mine_block(self, block):
        """
        Mines a given block using the set difficulty level.

        :param block: The block to mine.
        :return: None
        """
        block.mine_block(self.difficulty)

    def add_block(self, new_block):
        """
        Add a new block to the chain after mining it with the specified difficulty.
        :param new_block: The block to be added to the blockchain.
        :return: None
        """
        # Check if the block has a valid hash for the difficulty level
        if new_block.hash is None or new_block.hash[:self.difficulty] != "0" * self.difficulty:
            logger.error("Failed to add block: Block is not mined or does not meet the difficulty requirements.")
            return

        new_block.previous_hash = self.get_latest_block().hash
        if new_block.validate_transactions():
            self.chain.append(new_block)
            logger.info("New block added: %s", new_block)
        else:
            logger.error("Failed to add block: Contains invalid transactions.")

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
            if not current_block.validate_transactions():
                logger.warning("Block validation failed due to invalid transaction at index %d", i)
                return False

        logger.info("Blockchain validation succeeded.")
        return True


def assertion_check():
    """
    Performs various assertions to verify the functionality of the Blockchain class.

    :return: None
    """
    # Generate keys for testing
    sender_private_key, sender_public_key = get_sk_pk_pair()
    _, recipient_public_key = get_sk_pk_pair()

    # Create sample Transaction objects
    transaction1 = Transaction(sender_public_key, recipient_public_key, 10)
    transaction1.sign_transaction(sender_private_key)
    transaction2 = Transaction(sender_public_key, recipient_public_key, 20)
    transaction2.sign_transaction(sender_private_key)

    # Initialize blockchain
    blockchain = Blockchain()

    # Check genesis block
    assert blockchain.chain[0].transactions[0].amount == 0, GENESIS_BLOCK_ERROR

    # Create and mine new block with transactions
    new_block = Block(blockchain.get_latest_block().hash, [transaction1, transaction2])
    blockchain.mine_block(new_block)
    assert new_block.hash[:blockchain.difficulty] == "0" * blockchain.difficulty, "Mining failed"

    # Add mined block and validate the blockchain
    blockchain.add_block(new_block)
    assert blockchain.is_chain_valid(), BLOCKCHAIN_VALIDITY_ERROR

    logger.info("All assertions passed for Blockchain class.")


if __name__ == "__main__":
    assertion_check()
