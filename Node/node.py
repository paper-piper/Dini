import threading
from queue import Queue
from abc import ABC, abstractmethod
from dini_settings import MsgTypes, MsgSubTypes
from logging_utils import setup_logger
from Protocol.protocol import receive_message, send_message
import socket

# Setup logger for peer file
logger = setup_logger("node_module")

QUEUE_LEN = 1
SERVER_ADDRESS = ("127.123.123", 1900)


class Node(ABC):
    """
    basic communication tools;
    receiving and sending messages and implementing a queue which will handle all of those messages.
    Essentially handling all communication and threading.
    """

    def __init__(self, port=8080):
        self.messages_queue = Queue()
        self.peer_connections = {}  # Dictionary to hold peer addresses
        self.handle_messages_thread = threading.Thread(target=self.handle_messages, daemon=True)
        self.handle_messages_thread.start()

        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.address = (self.ip, self.port)
        self.accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.accept_connections_thread = threading.Thread(target=self.accept_connections, daemon=True)
        self.accept_connections_thread.start()

    def accept_connections(self):
        self.accept_socket.bind(self.address)
        self.accept_socket.listen(QUEUE_LEN)
        while True:
            node_address, node_socket = self.accept_socket.accept()
            self.peer_connections[node_socket] = node_socket

    def connect_to_node(self, address):
        node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        node_socket.connect(address)
        self.peer_connections[address[0]] = node_socket

    def add_peer(self, host, port):
        """
        Adds a peer to the peers list and establishes a connection to it.

        :param host: Host address of the peer.
        :param port: Port number of the peer.
        """
        peer_address = (host, port)

        # Check if the peer is already connected
        if peer_address in self.peer_connections.keys():
            logger.warning(f"Peer {host}:{port} is already connected.")
            return

        try:
            # Attempt to connect to the new peer
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect(peer_address)
            self.peer_connections[peer_address] = peer_socket

            # Start a thread to listen for messages from this peer
            threading.Thread(target=self.receive_messages, args=(peer_socket,), daemon=True).start()
            logger.info(f"Connected to new peer {host}:{port}")

        except Exception as e:
            logger.error(f"Failed to connect to peer {host}:{port} - {e}")

    def send_distributed_message(self, msg_type, msg_sub_type, *msg_params, excluded_peers=None):
        for peer_info, peer_socket in self.peer_connections.items():
            if not excluded_peers:
                send_message(peer_socket, msg_type, msg_sub_type, *msg_params)
            elif peer_info not in excluded_peers:
                send_message(peer_socket, msg_type, msg_sub_type, *msg_params)

    def send_focused_message(self, address, msg_type, msg_subtype, *msg_params):
        if address not in self.peer_connections.keys():
            return False  # error return value

        send_message(self.peer_connections[address], msg_type, msg_subtype, *msg_params)
        return True

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
                msg_type, msg_subtype, msg_params = self.messages_queue.get()
                try:
                    self.process_message(msg_type, msg_subtype, msg_params)
                except Exception as e:
                    logger.error(f"Error handling message: {e}")

    def process_message(self, msg_type, msg_subtype, msg_params):
        match msg_type:
            case MsgTypes.REQUEST_OBJECT:
                requested_object = self.get_requested_object(msg_subtype)
                # Bonus: send the message only to the sender
                return_address = msg_params[0]
                forward_object = False
                self.send_focused_message(
                    return_address,
                    MsgTypes.SEND_OBJECT,
                    msg_subtype,
                    requested_object,
                    forward_object
                )

            case MsgTypes.SEND_OBJECT:
                # check if message needs to be ignored
                if self.already_seen_message():
                    return
                self.handle_send_message(msg_subtype, msg_params)
                # check if the message is needed to be forwarded

                forward_object = msg_params[1]
                if forward_object:
                    self.send_distributed_message(msg_type, msg_subtype, *msg_params)
            case _:
                logger.warning(f"Received invalid message type ({msg_type})")

    def already_seen_message(self):
        return False  # placeholder

    def get_requested_object(self, object_type):
        """
        Routes request messages to specific handlers based on object type.

        :param object_type: Type of object requested (e.g., BLOCK, PEER).
        """
        results = None
        match object_type:
            case MsgSubTypes.BLOCK:
                results = self.handle_block_request()
            case MsgSubTypes.PEER:
                results = self.handle_peer_request()
            case _:
                logger.error("Received invalid message subtype")

        return results

    def handle_send_message(self, object_type, params):
        """
        Routes send messages to specific handlers based on object type.

        :param object_type: Type of object sent (e.g., BLOCK, PEER, TRANSACTION).
        :param params: Additional parameters for message processing.
        """
        match object_type:
            case MsgSubTypes.BLOCK:
                self.handle_block_send(params)
            case MsgSubTypes.PEER:
                self.handle_peer_send(params)
            case MsgSubTypes.TRANSACTION:
                self.handle_transaction_send(params)

    @abstractmethod
    def handle_block_request(self):
        """
        Handles requests for a specific block (abstract method to be implemented in subclasses).
        """
        pass

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

# File has no assertion checks, since communication needs to be check using multiple files
