import threading
from queue import Queue
from abc import abstractmethod, ABC
from utils.config import MsgTypes, MsgSubTypes
from utils.logging_utils import setup_logger
from core_communication.protocol import receive_message, send_message
import socket

# Setup logger for node file
logger = setup_logger("node")
QUEUE_SIZE = 10


class Node(ABC):
    """
    basic communication tools;
    receiving and sending messages and implementing a queue which will handle all of those messages.
    Essentially handling all communication and threading.
    """

    def __init__(self, port=8080, ip=None, node_connections=None, port_manager=None):
        """
        :param port: Port number for the node's socket.
        :param ip: IP address of the node (defaults to the local machine's IP).
        :param node_connections: Dictionary of existing node connections.
        :return: None
        """
        self.connection_readers = 0
        self.writer_active = False
        self.connection_lock = threading.Lock()
        self.condition = threading.Condition(self.connection_lock)
        self.node_connections = {} if not node_connections else node_connections

        self.ip = socket.gethostbyname(socket.gethostname()) if not ip else ip
        self.port_manager = port_manager
        if port_manager:
            self.port = port_manager.allocate_port()
        else:
            self.port = port

        self.address = (self.ip, self.port)
        self.accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages_queue = Queue()

        self.process_incoming_messages = threading.Thread(target=self.process_messages_from_queue, daemon=True)
        self.process_incoming_messages.start()
        self.accept_connections_thread = threading.Thread(target=self.accept_connections, daemon=True)
        self.accept_connections_thread.start()

    def __del__(self):
        if self.port_manager:
            self.port_manager.release_port(self.port)

    def get_connected_nodes(self):
        return self.node_connections.keys()

    def acquire_connections_read(self):
        with self.condition:
            while self.writer_active:
                self.condition.wait()
            self.connection_readers += 1

    def release_connections_read(self):
        with self.condition:
            self.connection_readers -= 1
            if self.connection_readers == 0:
                self.condition.notify_all()

    def acquire_connections_write(self):
        with self.condition:
            while self.writer_active or self.connection_readers > 0:
                self.condition.wait()
            self.writer_active = True

    def release_connections_write(self):
        with self.condition:
            self.writer_active = False
            self.condition.notify_all()

    def accept_connections(self):
        """
        Accepts incoming connections from other nodes and adds them to node connections.
        logs any connection errors.
        :return: None
        """
        try:
            # accept all connections
            self.accept_socket.bind(('0.0.0.0', self.port))
            self.accept_socket.listen(QUEUE_SIZE)
            logger.info(f"Node ({self.address}) listening for connections")
            while True:
                node_socket, node_address = self.accept_socket.accept()

                self.acquire_connections_write()
                self.node_connections[node_address] = node_socket
                self.release_connections_write()

                threading.Thread(target=self.receive_messages, args=(node_address, node_socket), daemon=True).start()
                logger.info(f"Node ({self.address}) accepted connection from {node_address}")
        except Exception as e:
            logger.error(f"Error in accept_connections: {e}")

    def connect_to_node(self, address):
        """
        Adds a node to the nodes list and establishes a connection to it.
        :param address: the node address
        """
        # check if the address is our own address
        if self.address == address:
            return

        # Check if the node is already connected
        self.acquire_connections_read()
        if address in self.node_connections.keys():
            logger.warning(f"Node ({self.address}): node {address} is already connected.")
            self.release_connections_read()
            return
        self.release_connections_read()
        try:
            # Attempt to connect to the new node
            node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            node_socket.bind(self.address)
            node_socket.connect(address)

            self.acquire_connections_read()
            self.node_connections[address] = node_socket
            self.release_connections_read()

            # Start a thread to listen for messages from this node
            threading.Thread(target=self.receive_messages, args=(address, node_socket), daemon=True).start()
            logger.info(f"Node ({self.address}): Connected to new node {address}")

        except Exception as e:
            logger.error(f"Node ({self.address}): Failed to connect to node {address} - {e}")

    def send_distributed_message(self, msg_type, msg_sub_type, *msg_params, excluded_node=None):
        """
        Sends a message to all connected nodes except excluded ones.
        :param msg_type: Type of the message.
        :param msg_sub_type: Subtype of the message.
        :param msg_params: Parameters for the message.
        :param excluded_node: List of nodes to exclude from the message.
        :return: None
        """
        sent_nodes = []
        self.acquire_connections_read()
        for node_info, node_socket in self.node_connections.items():
            try:
                if not excluded_node or node_info is not excluded_node:
                    send_message(node_socket, msg_type, msg_sub_type, *msg_params)
                    sent_nodes.append(node_info)
            except Exception as e:
                logger.error(f"Node ({self.address}): Failed to send message to {node_info}: {e}")
        if len(sent_nodes) > 0:
            logger.info(f"Node ({self.address}): Distributed message: ({msg_type}), ({msg_sub_type}), ({msg_params})"
                        f" Sent to {sent_nodes}")
        self.release_connections_read()

    def send_focused_message(self, address, msg_type, msg_subtype, *msg_params):
        """
        Sends a focused message to a specific node.

        :param address: Address of the node to send the message to.
        :param msg_type: Type of the message.
        :param msg_subtype: Subtype of the message.
        :param msg_params: Parameters for the message.
        :return: True if successful, False otherwise.
        """
        self.acquire_connections_read()
        if address not in self.node_connections:
            self.release_connections_read()
            logger.warning(f"Node ({self.address}): Node at {address} not found.")
            return False
        try:
            self.acquire_connections_read()
            send_message(self.node_connections[address], msg_type, msg_subtype, *msg_params)
            self.release_connections_read()
            logger.info(f"Node ({self.address}): Focused message sent to {address}: {msg_type}, {msg_subtype}")
            return True
        except Exception as e:
            logger.error(f"Node ({self.address}): Error sending focused message to {address}: {e}")
            return False

    def receive_messages(self, node_address, node_socket):
        """
        Continuously receives messages from a specific node and puts them in the message queue.
        :param node_address: the node address
        :param node_socket: The socket connection to the node.
        """
        try:
            while True:
                # Receive message from node
                msg_type, msg_sub_type, msg_params = receive_message(node_socket)
                # Add the message to the queue for processing
                self.messages_queue.put((node_address, msg_type, msg_sub_type, msg_params))
                logger.info(f"Node ({self.address}): Message received from node with address:"
                            f" {node_socket.getpeername()}:"
                            f" type:({msg_type}), sub type: ({msg_sub_type})"
                            f" params: {msg_params}")
        except socket.error as e:
            logger.error(f"Node ({self.address}): Socket error while receiving message: {e}")
        except Exception as e:
            logger.error(f"Node ({self.address}): General error while receiving message: {e}")
        finally:
            node_socket.close()  # Ensure socket is closed
            self.acquire_connections_write()
            del self.node_connections[node_address]
            self.release_connections_write()

    def process_messages_from_queue(self):
        """
        Processes messages from the message queue and directs them to appropriate handlers.
        """
        while True:
            if not self.messages_queue.empty():
                node_address, msg_type, msg_subtype, msg_params = self.messages_queue.get()
                try:
                    self.process_message(node_address, msg_type, msg_subtype, msg_params)
                except Exception as e:
                    logger.error(f"Node ({self.address}): Error handling message: {e}")

    def process_message(self, node_address, msg_type, msg_subtype, msg_params):
        match msg_type:
            case MsgTypes.REQUEST_OBJECT:
                requested_object = self.get_requested_object(msg_subtype, msg_params)
                # if the node cannot handle the request, discard it for now and trust other node to answer it
                if not requested_object:
                    return
                forward_object = False
                self.send_focused_message(
                    node_address,
                    MsgTypes.SEND_OBJECT,
                    msg_subtype,
                    requested_object,
                    forward_object
                )

            case MsgTypes.SEND_OBJECT:
                msg_object = msg_params[0]
                forward_object = msg_params[1]

                already_seen = self.process_send_message(msg_subtype, msg_object)
                # check if message needs to be ignored
                if already_seen:
                    return

                # check if the message is needed to be forwarded
                if forward_object:
                    (self.
                     send_distributed_message(msg_type, msg_subtype, excluded_node=node_address, *msg_params))
            case _:
                logger.warning(f"Node ({self.address}): Received invalid message type ({msg_type})")

    def get_requested_object(self, object_type, params):
        """
        Routes request messages to specific handlers based on object type.

        :param object_type: Type of object requested (e.g., BLOCK, NODE).
        :param params: additional parameters (not always required)
        """
        results = None
        match object_type:
            case MsgSubTypes.BLOCKCHAIN:
                results = self.serve_blockchain_request(params)
            case MsgSubTypes.NODE_ADDRESS:
                results = self.serve_node_request()
            case _:
                logger.error("Node ({self.address}): Received invalid message subtype")

        return results

    def process_send_message(self, object_type, msg_object):
        """
        Routes send messages to specific handlers based on object type.
        :param object_type: Type of object sent (e.g., BLOCK, NODE, TRANSACTION).
        :param msg_object: Additional parameters for message processing.
        """
        already_seen = False
        match object_type:
            case MsgSubTypes.BLOCK:
                already_seen = self.process_block_data(msg_object)

            case MsgSubTypes.BLOCKCHAIN:
                # blockchain is only request-send pair message, so it always needs new
                self.process_blockchain_data(msg_object)

            case MsgSubTypes.NODE_ADDRESS:
                # node is only request-send pair message, so it always needs new
                self.process_node_data(msg_object)

            case MsgSubTypes.TRANSACTION:
                already_seen = self.process_transaction_data(msg_object)

            case MsgSubTypes.TEST:
                # since this is a test, it is new
                already_seen = self.process_test_data(msg_object)

            case _:
                logger.error(f"Node ({self.address}): invalid object type: '{object_type}'")

        return already_seen

    @abstractmethod
    def serve_blockchain_request(self, latest_hash):
        """
        Handles requests for a specific block (abstract method to be implemented in subclasses).
        """
        pass

    @abstractmethod
    def serve_node_request(self):
        """
        Handles requests for node information (abstract method).
        """
        pass

    @abstractmethod
    def process_block_data(self, params):
        """
        Handles sending block information (abstract method).

        :param params: Parameters for block sending.
        """
        pass

    @abstractmethod
    def process_blockchain_data(self, params):
        """
        Handles sending block information (abstract method).

        :param params: Parameters for block sending.
        """
        pass

    @abstractmethod
    def process_node_data(self, params):
        """
        Handles sending node information (abstract method).

        :param params: Parameters for node sending.
        """
        pass

    @abstractmethod
    def process_transaction_data(self, params):
        """
        Handles sending transaction information (abstract method).

        :param params: Parameters for transaction sending.
        """
    def process_test_data(self, params):
        """
        Handles sending test information (abstract method).
        :param params: Parameters for test sending.
        """
        logger.info(f"Node ({self.address}): received test message! ({params})")
