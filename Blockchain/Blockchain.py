from Block import Block


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]  # Initialize chain with the genesis block
        self.difficulty = difficulty                # Mining difficulty level (number of leading zeros in hash)

    def create_genesis_block(self):
        """
        Create the first block in the blockchain.
        """
        return Block("0", ["Genesis Block"])

    def get_latest_block(self):
        """
        Retrieve the most recent block in the chain.
        """
        return self.chain[-1]

    def add_block(self, new_block):
        """
        Add a new block to the chain after mining.
        """
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def is_chain_valid(self):
        """
        Check the validity of the blockchain.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check if the current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                return False

            # Check if the previous hash is correctly set
            if current_block.previous_hash != previous_block.hash:
                return False

        return True
