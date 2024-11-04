import json
import os
import threading
from queue import Queue
from abc import ABC, abstractmethod
from Blockchain.blockchain import Blockchain, Transaction, Block
from cryptography.hazmat.primitives.asymmetric import rsa
from dini_Settings import FileSettings, ProtocolSettings
from logging_utils import setup_logger
from Protocol.protocol import receive_message, send_message
import socket

# Setup logger for peer file
logger = setup_logger("node_module")


class Node:
    def __init__(self, peer_type, blockchain=None):
        self.peer_type = peer_type
        self.filename = FileSettings.BLOCKCHAIN_FILE_NAME
        # Load blockchain if provided or initialize from file
        self.blockchain = blockchain if blockchain else self.load_blockchain()

        # Initialize a socket for peer connections
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peers = []  # List of connected peers
        self.messages_queue = Queue()
        self.receive_messages_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.handle_messages_thread = threading.Thread(target=self.handle_messages, daemon=True)

    def __del__(self):
        self.save_blockchain()
    
    def to_dict(self):
        """
        Converts the Node object into a dictionary, including the blockchain and peer information.
        :return: Dictionary representation of the Node object.
        """
        return {
            "blockchain": self.blockchain.to_dict(),  # Convert blockchain using its to_dict method
            "peer_type": self.peer_type,
            "peers": self.peers
        }

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Node object from a dictionary, reconstructing the blockchain and peer information.
        :param data: Dictionary containing peer information.
        :return: Node object.
        """
        blockchain = Blockchain.from_dict(data["blockchain"])  # Reconstruct blockchain using from_dict
        peer_type = data["peer_type"]
        peer_instance = cls(blockchain, peer_type)
        peer_instance.peers = data["peers"]
        return peer_instance

    def receive_messages(self):
        while True:
            msg_type, msg_sub_type, msg_params = receive_message(self.sock)
            self.messages_queue.put((msg_type, msg_sub_type, msg_params))

    def handle_messages(self):
        while True:
            if not self.messages_queue.empty():
                msg_type, msg_sub_type, msg_params = self.messages_queue.get()
                if msg_type == ProtocolSettings.REQUEST_OBJECT:
                    self.handle_request_message(msg_sub_type)
                elif msg_type == ProtocolSettings.SEND_OBJECT:
                    self.handle_send_message(msg_sub_type, msg_params)
                else:
                    raise "Received invalid message type"

    def handle_request_message(self, object_type):
        match object_type:
            case ProtocolSettings.BLOCK:
                self.handle_block_request()
            case ProtocolSettings.PEER:
                self.handle_peer_request()
            # No one can request transaction

    def handle_send_message(self, object_type, params):
        match object_type:
            case ProtocolSettings.BLOCK:
                self.handle_block_send(params)
            case ProtocolSettings.PEER:
                self.handle_peer_send(params)
            case ProtocolSettings.TRANSACTION:
                self.handle_transaction_send(params)

    def handle_block_request(self):
        pass

    @abstractmethod
    def handle_peer_request(self):
        pass

    @abstractmethod
    def handle_block_send(self, params):
        pass

    @abstractmethod
    def handle_peer_send(self, params):
        pass

    @abstractmethod
    def handle_transaction_send(self, params):
        pass

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
        # TODO: decide which peer to ask from
        for peer in self.peers:
            send_message(peer.sock, ProtocolSettings.REQUEST_OBJECT, ProtocolSettings.BLOCK)
        logger.info("Requesting block with hash: %s", block_hash)

    def validate_block(self):
        # bonus
        pass

    def pass_block(self, block):
        """Pass the mined or received block to other peers."""
        # Network broadcast logic to be implemented
        logger.info("Broadcasting block with hash: %s", block.hash)

    def add_peer(self, peer_info):
        """Adds a new peer to the network list."""
        self.peers.append(peer_info)
        logger.info("New peer added: %s", peer_info)

    def add_block_to_blockchain(self, block):
        self.blockchain.add_block(block)
        self.save_blockchain()


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
    """Creates a Node instance with a sample blockchain and saves it to a file."""
    # Create sample blockchain
    sample_blockchain = create_sample_blockchain()

    # Create Node with blockchain and save to file
    peer = Node(blockchain=sample_blockchain, peer_type="test_peer")
    peer.save_blockchain()

    print(f"Blockchain saved to {filename} using Node class.")


def load_and_resave_with_peer(input_filename="sample_blockchain.json", output_filename="resaved_blockchain.json"):
    """Loads blockchain from a file with a Node instance and resaves it to another file."""
    # Load the blockchain with Node
    peer = Node(blockchain=Blockchain(difficulty=2), peer_type="test_peer")
    peer.load_blockchain()

    # Resave the loaded blockchain to a new file
    with open(output_filename, "w") as f:
        json.dump(peer.blockchain.to_dict(), f, indent=4)

    print(f"Blockchain loaded from {input_filename} and resaved to {output_filename} using Node class.")


def main():
    # Test the function
    save_blockchain_with_peer()
    load_and_resave_with_peer()


if __name__ == "__main__":
    main()
