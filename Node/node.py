import json
import os
import threading
from queue import Queue
from abc import ABC, abstractmethod
from Blockchain.blockchain import Blockchain, create_sample_blockchain
from cryptography.hazmat.primitives.asymmetric import rsa
from dini_Settings import FileSettings, ProtocolSettings
from logging_utils import setup_logger
from Protocol.protocol import receive_message, send_message
import socket

# Setup logger for peer file
logger = setup_logger("node_module")


class Node(ABC):
    """
    Represents a network node responsible for handling peer communication, blockchain management,
    and message processing.

    :param peer_type: Type of the peer (e.g., User, Miner).
    :param blockchain: Optional blockchain instance; if not provided, loads from file.
    """

    def __init__(self, peer_type, blockchain=None, filename=None):
        self.peer_type = peer_type
        self.filename = FileSettings.BLOCKCHAIN_FILE_NAME if filename is None else filename
        self.blockchain = blockchain if blockchain else self.load_blockchain()
        self.peers = []
        self.messages_queue = Queue()
        self.peer_connections = {}  # Dictionary to hold peer sockets
        self.handle_messages_thread = threading.Thread(target=self.handle_messages, daemon=True)
        self.handle_messages_thread.start()

    def __del__(self):
        self.save_blockchain()

    def add_peer(self, host, port):
        """
        Adds a peer to the peers list and establishes a connection to it.

        :param host: Host address of the peer.
        :param port: Port number of the peer.
        """
        peer_info = (host, port)

        # Check if the peer is already connected
        if peer_info in self.peers:
            logger.warning(f"Peer {host}:{port} is already connected.")
            return

        self.peers.append(peer_info)

        try:
            # Attempt to connect to the new peer
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((host, port))
            self.peer_connections[(host, port)] = peer_socket

            # Start a thread to listen for messages from this peer
            threading.Thread(target=self.receive_messages, args=(peer_socket,), daemon=True).start()
            logger.info(f"Connected to new peer {host}:{port}")

        except Exception as e:
            logger.error(f"Failed to connect to peer {host}:{port} - {e}")

    def receive_messages(self, peer_socket):
        """
        Continuously receives messages from a specific peer and puts them in the message queue.

        :param peer_socket: The socket connection to the peer.
        """
        while True:
            try:
                # Receive message from peer
                msg_type, msg_sub_type, msg_params = receive_message(peer_socket)
                # Add the message to the queue for processing
                self.messages_queue.put((msg_type, msg_sub_type, msg_params))
                logger.info(f"Message received from peer {peer_socket.getpeername()}:"
                            f" type:{msg_type},sub type: {msg_sub_type}")
            except Exception as e:
                logger.error(f"Error receiving message from {peer_socket.getpeername()}: {e}")
                break  # Exit the loop if there's an error to stop this thread

    def handle_messages(self):
        """
        Processes messages from the message queue and directs them to appropriate handlers.
        """
        while True:
            if not self.messages_queue.empty():
                msg_type, msg_sub_type, msg_params = self.messages_queue.get()
                try:
                    if msg_type == ProtocolSettings.REQUEST_OBJECT:
                        self.handle_request_message(msg_sub_type)
                    elif msg_type == ProtocolSettings.SEND_OBJECT:
                        self.handle_send_message(msg_sub_type, msg_params)
                    else:
                        logger.warning("Received invalid message type")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")

    def handle_request_message(self, object_type):
        """
        Routes request messages to specific handlers based on object type.

        :param object_type: Type of object requested (e.g., BLOCK, PEER).
        """
        match object_type:
            case ProtocolSettings.BLOCK:
                self.handle_block_request()
            case ProtocolSettings.PEER:
                self.handle_peer_request()

    def handle_send_message(self, object_type, params):
        """
        Routes send messages to specific handlers based on object type.

        :param object_type: Type of object sent (e.g., BLOCK, PEER, TRANSACTION).
        :param params: Additional parameters for message processing.
        """
        match object_type:
            case ProtocolSettings.BLOCK:
                self.handle_block_send(params)
            case ProtocolSettings.PEER:
                self.handle_peer_send(params)
            case ProtocolSettings.TRANSACTION:
                self.handle_transaction_send(params)

    def handle_block_request(self):
        """
        Handles requests for a specific block (abstract method to be implemented in subclasses).
        """
        raise NotImplementedError("Block request handling must be implemented in subclass.")

    @abstractmethod
    def handle_peer_request(self):
        """
        Handles requests for peer information (abstract method).
        """
        pass

    @abstractmethod
    def handle_block_send(self, params):
        """
        Handles sending block information (abstract method).

        :param params: Parameters for block sending.
        """
        pass

    @abstractmethod
    def handle_peer_send(self, params):
        """
        Handles sending peer information (abstract method).

        :param params: Parameters for peer sending.
        """
        pass

    @abstractmethod
    def handle_transaction_send(self, params):
        """
        Handles sending transaction information (abstract method).

        :param params: Parameters for transaction sending.
        """
        pass

    def save_blockchain(self):
        """
        Saves the current blockchain to a file in JSON format.
        """
        try:
            with open(self.filename, "w") as f:
                json.dump(self.blockchain.to_dict(), f, indent=4)
            logger.info(f"Blockchain saved to {self.filename}")
        except Exception as e:
            logger.error(f"Error saving blockchain: {e}")

    def load_blockchain(self):
        """
        Loads the blockchain from a file if it exists, otherwise initializes a new blockchain.

        :return: Loaded or newly created blockchain object.
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    blockchain_data = json.load(f)
                    self.blockchain = Blockchain.from_dict(blockchain_data)
                logger.info(f"Blockchain loaded from {self.filename}")
            except Exception as e:
                logger.error(f"Error loading blockchain: {e}")
        else:
            logger.warning(f"No blockchain file found at {self.filename}, initializing new blockchain.")
            self.blockchain = create_sample_blockchain()

    def request_block(self, block_hash):
        """
        Requests a specific block from peers.

        :param block_hash: The hash of the block being requested.
        """
        for peer in self.peers:
            send_message(peer.sock, ProtocolSettings.REQUEST_OBJECT, ProtocolSettings.BLOCK)
        logger.info(f"Requesting block with hash: {block_hash}")

    def add_block_to_blockchain(self, block):
        """
        Adds a block to the blockchain and saves the updated chain.

        :param block: Block to add.
        """
        self.blockchain.add_block(block)
        self.save_blockchain()


class TestNode(Node):
    """
    A concrete subclass of Node for testing purposes, implementing abstract methods minimally.
    """

    def handle_peer_request(self):
        logger.info("TestNode handling peer request")

    def handle_block_request(self):
        logger.info("TestNode handling block request")

    def handle_block_send(self, params):
        logger.info("TestNode handling block send")

    def handle_peer_send(self, params):
        logger.info("TestNode handling peer send")

    def handle_transaction_send(self, params):
        logger.info("TestNode handling transaction send")


def assertion_check():
    """
    Performs assertion checks to verify the correctness of the Node class using TestNode instances.
    Includes tests for saving and loading the blockchain from a file and adding peers.
    """
    # Sample blockchain for testing
    blockchain = create_sample_blockchain()
    test_filename = "test_blockchain.json"
    test_node = TestNode("TestNode", blockchain, test_filename)

    # Test add_peer and peers list
    peer_info = ("127.0.0.1", 8000)
    test_node.add_peer(*peer_info)
    assert peer_info in test_node.peers, "Peer not correctly added"

    # Save blockchain to file
    test_node.save_blockchain()
    assert os.path.exists(test_filename), "Blockchain file not created"

    # Load blockchain from file and verify content
    test_node_loaded = TestNode("Test", filename=test_filename)
    test_node_loaded.load_blockchain()

    assert test_node.blockchain.to_dict() == test_node_loaded.blockchain.to_dict(), \
        "Mismatch between saved and loaded blockchain data"

    # Clean up test file
    os.remove(test_filename)
    logger.info("File save and load tests passed.")

    logger.info("All assertion checks passed.")


def main():
    # Main execution, include assertion check
    assertion_check()


if __name__ == "__main__":
    main()
