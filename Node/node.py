import threading
from queue import Queue
from abc import abstractmethod, ABC
from dini_settings import MsgTypes, MsgSubTypes
from logging_utils import setup_logger
from Protocol.protocol import receive_message, send_message
import socket

# Setup logger for peer file
logger = setup_logger("node")
QUEUE_SIZE = 10


class Node(ABC):
    """
    basic communication tools;
    receiving and sending messages and implementing a queue which will handle all of those messages.
    Essentially handling all communication and threading.
    """

    def __init__(self, port=8080, ip=None, peer_connections=None):
        """
        :param port: Port number for the node's socket.
        :param ip: IP address of the node (defaults to the local machine's IP).
        :param peer_connections: Dictionary of existing peer connections.
        :return: None
        """
        self.peer_connections = {} if not peer_connections else peer_connections
        self.ip = socket.gethostbyname(socket.gethostname()) if not ip else ip
        self.port = port

        self.address = (self.ip, self.port)
        self.accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages_queue = Queue()

        self.process_incoming_messages = threading.Thread(target=self.process_incoming_messages, daemon=True)
        self.process_incoming_messages.start()
        self.accept_connections_thread = threading.Thread(target=self.accept_connections, daemon=True)
        self.accept_connections_thread.start()

    def accept_connections(self):
        """
        Accepts incoming connections from other peers and adds them to peer connections.
        Logs any connection errors.
        :return: None
        """
        try:
            self.accept_socket.bind(self.address)
            self.accept_socket.listen(QUEUE_SIZE)
            logger.info(f"Node listening for connections at {self.address}")
            while True:
                node_socket, node_address = self.accept_socket.accept()
                self.peer_connections[node_address] = node_socket
                threading.Thread(target=self.receive_messages, args=(node_socket,), daemon=True).start()
                logger.info(f"Accepted connection from {node_address}")
        except Exception as e:
            logger.error(f"Error in accept_connections: {e}")

    def connect_to_node(self, address):
        """
        Adds a peer to the peers list and establishes a connection to it.
        :param address: the node address
        """

        # Check if the peer is already connected
        if address in self.peer_connections.keys():
            logger.warning(f"Peer {address} is already connected.")
            return

        try:
            # Attempt to connect to the new peer
            node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            node_socket.connect(address)
            self.peer_connections[address] = node_socket

            # Start a thread to listen for messages from this peer
            threading.Thread(target=self.receive_messages, args=(node_socket,), daemon=True).start()
            logger.info(f"Connected to new peer {address}")

        except Exception as e:
            logger.error(f"Failed to connect to peer {address} - {e}")

    def send_distributed_message(self, msg_type, msg_sub_type, *msg_params, excluded_peers=None):
        """
        Sends a message to all connected peers except excluded ones.
        :param msg_type: Type of the message.
        :param msg_sub_type: Subtype of the message.
        :param msg_params: Parameters for the message.
        :param excluded_peers: List of peers to exclude from the message.
        :return: None
        """
        for peer_info, peer_socket in self.peer_connections.items():
            try:
                if not excluded_peers or peer_info not in excluded_peers:
                    send_message(peer_socket, msg_type, msg_sub_type, *msg_params)
                    logger.info(f"Distributed message sent to {peer_info}: {msg_type}, {msg_sub_type}")
            except Exception as e:
                logger.error(f"Failed to send message to {peer_info}: {e}")

    def send_focused_message(self, address, msg_type, msg_subtype, *msg_params):
        """
        Sends a focused message to a specific peer.

        :param address: Address of the peer to send the message to.
        :param msg_type: Type of the message.
        :param msg_subtype: Subtype of the message.
        :param msg_params: Parameters for the message.
        :return: True if successful, False otherwise.
        """
        if address not in self.peer_connections:
            logger.warning(f"Peer at {address} not found.")
            return False
        try:
            send_message(self.peer_connections[address], msg_type, msg_subtype, *msg_params)
            logger.info(f"Focused message sent to {address}: {msg_type}, {msg_subtype}")
            return True
        except Exception as e:
            logger.error(f"Error sending focused message to {address}: {e}")
            return False

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

    def process_incoming_messages(self):
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
                msg_object = msg_params[0]
                forward_object = msg_params[1]

                already_seen = self.handle_send_message(msg_subtype, msg_object)
                # check if message needs to be ignored
                if already_seen:
                    return

                # check if the message is needed to be forwarded
                if forward_object:
                    self.send_distributed_message(msg_type, msg_subtype, *msg_params)
            case _:
                logger.warning(f"Received invalid message type ({msg_type})")

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

    def handle_send_message(self, object_type, msg_object):
        """
        Routes send messages to specific handlers based on object type.
        :param object_type: Type of object sent (e.g., BLOCK, PEER, TRANSACTION).
        :param msg_object: Additional parameters for message processing.
        """
        already_seen = False
        match object_type:
            case MsgSubTypes.BLOCK:
                already_seen = self.handle_block_send(msg_object)
            case MsgSubTypes.PEER:
                # peer is only request-send pair message, so it always needs new
                self.handle_peer_send(msg_object)
            case MsgSubTypes.TRANSACTION:
                already_seen = self.handle_transaction_send(msg_object)
            case _:
                logger.error(f"invalid object type: '{object_type}'")

        return already_seen

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