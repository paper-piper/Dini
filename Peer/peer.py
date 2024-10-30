import logging
import json
import os
from Blockchain.blockchain import Blockchain, Transaction, Block
from cryptography.hazmat.primitives.asymmetric import rsa
from dini_Settings import FileSettings
from protocol import send_message, receive_message


class Peer:
    def __init__(self, blockchain, peer_type):
        self.blockchain = blockchain
        self.peer_type = peer_type
        self.filename = FileSettings.BLOCKCHAIN_FILE_NAME
        self.peers = []  # List of connected peers
        self.logger = logging.getLogger(f"{peer_type}_peer")

    def save_blockchain(self):
        """Saves the current blockchain to a file in JSON format."""
        with open(self.filename, "w") as f:
            json.dump(self.blockchain.to_dict(), f, indent=4)
        print(f"Blockchain saved to {self.filename}")

    def load_blockchain(self):
        """Loads the blockchain from a file if it exists."""
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                blockchain_data = json.load(f)
                self.blockchain = Blockchain.from_dict(blockchain_data)
            print(f"Blockchain loaded from {self.filename}")
        else:
            print(f"No blockchain file found to load at {self.filename}")

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


def create_sample_blockchain():
    """Creates a sample blockchain with transactions and a block."""
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

    print("Sample blockchain created.")
    return sample_blockchain


def save_blockchain_with_peer(filename="sample_blockchain.json"):
    """Creates a Peer instance with a sample blockchain and saves it to a file."""
    # Create sample blockchain
    sample_blockchain = create_sample_blockchain()

    # Create Peer with blockchain and save to file
    peer = Peer(blockchain=sample_blockchain, peer_type="test_peer")
    peer.save_blockchain()

    print(f"Blockchain saved to {filename} using Peer class.")


def load_and_resave_with_peer(input_filename="sample_blockchain.json", output_filename="resaved_blockchain.json"):
    """Loads blockchain from a file with a Peer instance and resaves it to another file."""
    # Load the blockchain with Peer
    peer = Peer(blockchain=Blockchain(difficulty=2), peer_type="test_peer")
    peer.load_blockchain()

    # Resave the loaded blockchain to a new file
    with open(output_filename, "w") as f:
        json.dump(peer.blockchain.to_dict(), f, indent=4)

    print(f"Blockchain loaded from {input_filename} and resaved to {output_filename} using Peer class.")


# Test the function
save_blockchain_with_peer()
load_and_resave_with_peer()
