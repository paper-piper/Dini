import logging
import json
import os
from Blockchain.blockchain import Blockchain, Transaction, Block

from cryptography.hazmat.primitives.asymmetric import rsa

class Peer:
    def __init__(self, blockchain, peer_type):
        self.blockchain = blockchain
        self.peer_type = peer_type
        self.peers = []  # List of connected peers
        self.logger = logging.getLogger(f"{peer_type}_peer")

    def save_blockchain(self, filename="blockchain.json"):
        """Saves the current blockchain to a file in JSON format."""
        with open(filename, "w") as f:
            json.dump(self.blockchain.to_dict(), f)
        self.logger.info("Blockchain saved to %s", filename)

    def load_blockchain(self, filename="blockchain.json"):
        """Loads the blockchain from a file if it exists."""
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.blockchain.from_dict(json.load(f))
            self.logger.info("Blockchain loaded from %s", filename)
        else:
            self.logger.warning("No blockchain file found to load.")

    def request_block(self, block_hash):
        """Request a specific block from other peers."""
        # Network request logic to be implemented
        self.logger.info("Requesting block with hash: %s", block_hash)

    def pass_block(self, block):
        """Pass the mined or received block to other peers."""
        # Network broadcast logic to be implemented
        self.logger.info("Broadcasting block with hash: %s", block.hash)

    def add_peer(self, peer_info):
        """Adds a new peer to the network list."""
        self.peers.append(peer_info)
        self.logger.info("New peer added: %s", peer_info)

def create_sample_data(filename="sample_blockchain.json"):
    # Generate RSA keys for sample transactions
    sender_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    recipient_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    sender_pk = sender_private_key.public_key()
    recipient_pk = recipient_private_key.public_key()

    # Create sample transactions
    transaction1 = Transaction(sender_pk, recipient_pk, amount=100)
    transaction1.sign_transaction(sender_private_key)

    transaction2 = Transaction(sender_pk, recipient_pk, amount=50)
    transaction2.sign_transaction(sender_private_key)

    # Create a sample block with transactions
    sample_block = Block(previous_hash="0" * 64, transactions=[transaction1, transaction2])

    # Create a sample blockchain and add the sample block
    sample_blockchain = Blockchain(difficulty=2)
    sample_blockchain.chain.append(sample_block)

    # Serialize the blockchain to dictionary form and save to a file
    with open(filename, "w") as f:
        json.dump(sample_blockchain.to_dict(), f, indent=4)

    print(f"Sample blockchain data saved to {filename}")


def load_and_resave_blockchain(input_filename="sample_blockchain.json", output_filename="resaved_blockchain.json"):
    # Load the blockchain data from the input file
    with open(input_filename, "r") as f:
        blockchain_data = json.load(f)

    # Reconstruct the blockchain object from the dictionary
    loaded_blockchain = Blockchain.from_dict(blockchain_data)

    # Save the reconstructed blockchain to the output file
    with open(output_filename, "w") as f:
        json.dump(loaded_blockchain.to_dict(), f, indent=4)

    print(f"Blockchain data loaded from {input_filename} and saved to {output_filename}")

# Test the function
load_and_resave_blockchain()
