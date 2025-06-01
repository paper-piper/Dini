import threading
from queue import Queue
from abc import abstractmethod, ABC

from cryptography.hazmat.primitives import serialization

from utils.config import MsgTypes, MsgSubTypes, NodeSettings, IPSettings
from utils.logging_utils import configure_logger
from communication.protocol import receive_message, send_protocol_message
import socket

# Setup logger for node file
QUEUE_SIZE = 10


class Node(ABC):
    """
    basic communication tools;
    receiving and sending messages and implementing a queue which will handle all of those messages.
    Essentially handling all communication and threading.
    """

    def __init__(self,
                 port=8080,
                 ip=None,
                 node_connections=None,
                 child_dir="Node",
                 name=NodeSettings.DEFAULT_NAME
                 ):
        """
        :param port: Port number for the node's socket.
        :param ip: IP address of the node (defaults to the local machine's IP).
        :param node_connections: Dictionary of existing node connections.
        :param child_dir:   The name of the subdirectory under logs/,
                            e.g. "miner", "user", etc.
        :return: None
        """

        self.ip = IPSettings.LOCAL_IP if not ip else ip
        self.accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if port:
            self.port = port
            self.accept_socket.bind(('0.0.0.0', self.port))
        else:
            # Bind to all interfaces on an ephemeral port
            self.accept_socket.bind(('0.0.0.0', 0))
            self.port = self.accept_socket.getsockname()[1]

        self.address = (self.ip, self.port)
        self.name = name
        self.node_logger = configure_logger(
            class_name="Node",
            child_dir=child_dir,
            instance_id=name
        )

        self.running = threading.Event()
        self.running.set()
        self.node_connections_lock = threading.Lock()
        self.node_connections = {} if not node_connections else node_connections
        self.nodes_names_addresses = {}  # name : public key
        self.messages_queue = Queue()

        self.connections_threads = []
        self.main_threads = []
        process_incoming_messages = threading.Thread(target=self.process_messages_from_queue)
        self.main_threads.append(process_incoming_messages)
        process_incoming_messages.start()

        accept_connections_thread = threading.Thread(target=self.accept_connections)
        self.main_threads.append(accept_connections_thread)
        accept_connections_thread.start()

    def __del__(self):
        self.accept_socket.close()

    def stop_all_threads(self):
        self.running.clear()

        for thread in self.main_threads:
            thread.join()

        for thread in self.connections_threads:
            thread.join()

    def get_connected_nodes(self):
        with self.node_connections_lock:
            return self.node_connections.keys()

    def accept_connections(self):
        """
        Accepts incoming connections from other nodes and adds them to node connections.
        logs any connection errors.
        :return: None
        """
        # accept all connections
        self.accept_socket.listen(QUEUE_SIZE)
        while True:
            try:
                if self.accept_socket.fileno() == -1:  # check if socket is closed
                    return
                node_socket, _ = self.accept_socket.accept()
                _, _, node_address = receive_message(node_socket)
                node_address = node_address[0]
                with self.node_connections_lock:
                    self.node_connections[node_address] = node_socket

                get_messages_from_node = threading.Thread(target=self.receive_messages, args=(node_address, node_socket))
                self.connections_threads.append(get_messages_from_node)
                get_messages_from_node.start()
                self.node_logger.debug(f"accepted connection from {node_address}")
            except Exception as e:
                self.node_logger.error(f"Error in connecting to node: {e}")

    def connect_to_node(self, address):
        """
        Adds a node to the nodes list and establishes a connection to it.
        :param address: the node address
        """
        # check if the address is our own address
        if self.address == address:
            return

        # Check if the node is already connected
        with self.node_connections_lock:
            if address in self.node_connections.keys():
                self.node_logger.warning(f"node {address} is already connected.")
                return
        try:
            # Attempt to connect to the new node
            node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            node_socket.connect(address)
            self.node_logger.debug(f"Connected to node with address {address}")

            # send the accepting node the actual address
            send_protocol_message(node_socket, MsgTypes.RESPONSE, MsgSubTypes.NODE_INIT, self.address)

            with self.node_connections_lock:
                self.node_connections[address] = node_socket

            # Start a thread to listen for messages from this node
            threading.Thread(target=self.receive_messages, args=(address, node_socket)).start()
        except socket.error as se:
            self.node_logger.info(f"Failed to connect to node with address {address}. {se}")
        except Exception as e:
            self.node_logger.error(f"Caught unexpected error while connecting to node with address {address} - {e}")

    def send_distributed_message(self, msg_type, msg_sub_type, *msg_params, excluded_node=None):
        """
        Sends a message to all connected nodes except excluded ones.
        :param msg_type: Type of the message.
        :param msg_sub_type: Subtype of the message.
        :param msg_params: Parameters for the message.
        :param excluded_node: a node to exclude from the message.
        :return: None
        """
        with self.node_connections_lock:
            connections_copy = self.node_connections.copy()

        sent_nodes = []
        for node_info, node_socket in connections_copy.items():
            try:
                if not excluded_node or node_info is not excluded_node:
                    send_protocol_message(node_socket, msg_type, msg_sub_type, *msg_params)
                    sent_nodes.append(node_info)
            except Exception as e:
                self.node_logger.error(f"Failed to send message to {node_info}: {e}")

        if sent_nodes:
            self.node_logger.debug(
                f"Distributed message with {msg_sub_type} object: ({msg_params})"
                f" was sent to: {sent_nodes}")

    def send_focused_message(self, address, msg_type, msg_subtype, *msg_params):
        """
        Sends a focused message to a specific node.

        :param address: Address of the node to send the message to.
        :param msg_type: Type of the message.
        :param msg_subtype: Subtype of the message.
        :param msg_params: Parameters for the message.
        :return: True if successful, False otherwise.
        """
        with self.node_connections_lock:
            if address not in self.node_connections:
                self.node_logger.warning(f" Node at {address} not found.")
                return False
        try:
            with self.node_connections_lock:
                send_protocol_message(self.node_connections[address], msg_type, msg_subtype, *msg_params)
            self.node_logger.debug(f"Focused message sent to {address}: "
                                  f"({msg_type}), ({msg_subtype}), ({msg_params})")
            return True
        except Exception as e:
            self.node_logger.error(f" Error sending focused message to {address}: {e}")
            return False

    def receive_messages(self, node_address, node_socket):
        """
        Continuously receives messages from a specific node and puts them in the message queue.
        :param node_address: the node address
        :param node_socket: The socket connection to the node.
        """
        try:
            # before receiving messages from his indefinably, send him your name
            pk = self.get_public_key()
            if pk:
                self.send_focused_message(
                    node_address, MsgTypes.RESPONSE, MsgSubTypes.NODE_NAME, [self.name, pk])
            while True:
                # Receive message from node
                message = receive_message(node_socket)
                if not message:  # connection crushed
                    pass
                else:
                    msg_type, msg_subtype, msg_params = message
                    # Add the message to the queue for processing if message is not None
                    if msg_type:
                        self.messages_queue.put((node_address, msg_type, msg_subtype, msg_params))
        except socket.error as e:
            self.node_logger.error(f" Socket error while receiving message: {e}")
        except Exception as e:
            self.node_logger.error(f" General error while receiving message: {e}")
        finally:
            node_socket.close()  # Ensure socket is closed
            with self.node_connections_lock:
                del self.node_connections[node_address]

    def process_messages_from_queue(self):
        """
        Processes messages from the message queue and directs them to appropriate handlers.
        """
        while True:
            node_address, msg_type, msg_subtype, msg_params = self.messages_queue.get(block=True)
            try:
                self.process_message(node_address, msg_type, msg_subtype, msg_params)
            except Exception as e:
                self.node_logger.error(
                    f"Error handling message: Type: {msg_type}, Subtype: {msg_subtype}, Params: {msg_params} - {e}"
                )

    def process_message(self, node_address, msg_type, msg_subtype, msg_params):
        match msg_type:
            case MsgTypes.REQUEST:
                requested_object = self.get_requested_object(msg_subtype, msg_params)

                # if the node cannot handle the request, discard it for now and trust other node to answer it
                if not requested_object:
                    return
                self.send_focused_message(
                    node_address,
                    MsgTypes.RESPONSE,
                    msg_subtype,
                    requested_object
                )
                self.node_logger.debug(f"{node_address} Requested ({msg_subtype}) object."
                                       f" replied with object {requested_object}")

            case MsgTypes.RESPONSE:
                msg_object = msg_params[0]
                self.node_logger.debug(
                    f"received response {msg_subtype} object: ({msg_object}) from node with address: {node_address}"
                )
                self.process_object_data(msg_subtype, msg_object)

            case MsgTypes.BROADCAST:
                msg_object = msg_params[0]
                self.node_logger.debug(f"received broadcast {msg_subtype} object: ({msg_object})"
                                      f" from node with address: {node_address}")
                already_seen = self.process_object_data(msg_subtype, msg_object)
                if not already_seen:
                    self.send_distributed_message(msg_type, msg_subtype, excluded_node=node_address, *msg_params)

            case _:
                self.node_logger.warning(f"Received invalid message type ({msg_type})")

    def get_requested_object(self, object_type, params):
        """
        Routes request messages to specific handlers based on object type.

        :param object_type: Type of object requested (e.g., BLOCK, NODE).
        :param params: additional parameters (not always required)
        """
        results = None
        match object_type:
            case MsgSubTypes.BLOCKCHAIN:
                results = self.serve_blockchain_request(params[0])
            case MsgSubTypes.NODE_ADDRESS:
                results = self.serve_node_request()

        return results

    def process_object_data(self, object_type, msg_object):
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
                self.process_test_data(msg_object)

            case MsgSubTypes.NODE_NAME:
                # since name is new connection-based, it is always new
                self.process_name_data(msg_object)
            case _:
                self.node_logger.error(f" invalid object type: '{object_type}'")

        return already_seen

    def process_name_data(self, name_pk_pair):
        if not name_pk_pair or len(name_pk_pair) == 1 or name_pk_pair[1] is None:
            self.node_logger.warning(f"Invalid name pk pair - {name_pk_pair}")
            return
        name = name_pk_pair[0]
        public_key = serialization.load_pem_public_key(name_pk_pair[1].encode())
        self.nodes_names_addresses[name] = public_key
        self.node_logger.info(f"Connected to new node named '{name}'")

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

    @abstractmethod
    def get_public_key(self):
        """
        Sends the public key (depends on the class, not every class can send it)
        """

    def process_test_data(self, params):
        """
        Handles sending test information (abstract method).
        :param params: Parameters for test sending.
        """
        self.node_logger.info(f": received test message! ({params})")
