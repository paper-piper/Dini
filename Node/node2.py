from node import Node
from threading import Event
from logging_utils import setup_logger
from dini_settings import MsgTypes, MsgSubTypes
from Blockchain.transaction import create_sample_transaction
logger = setup_logger("node2")


class Node2(Node):
    """
    A specialized Node class for testing Node-to-Node communication.
    """

    def handle_block_request(self):
        logger.info("Node2 received a block request.")
        return {"block_data": "Sample block from Node2"}

    def handle_peer_request(self):
        logger.info("Node2 received a peer request.")
        return {"peer_list": list(self.peer_connections.keys())}

    def handle_block_send(self, params):
        logger.info(f"Node2 received a block: {params}")
        return False  # Indicate the block has not been seen before.

    def handle_peer_send(self, params):
        logger.info(f"Node2 received a peer update: {params}")

    def handle_transaction_send(self, params):
        logger.info(f"Node2 received a transaction: {params}")
        return False


if __name__ == "__main__":
    # Use localhost for same-computer testing
    node_ip = "127.0.0.1"

    # Initialize Node2 on port 9090
    node2 = Node2(port=9090, ip=node_ip)

    # Connect to Node1 (ensure Node1 is running)
    try:
        node2.connect_to_node((node_ip, 8080))
        logger.info(f"Node2 successfully connected to Node1 at {node_ip}:8080.")

        # Test communication: Send a message to Node1
        node2.send_distributed_message(
            MsgTypes.SEND_OBJECT,
            MsgSubTypes.TRANSACTION,
            create_sample_transaction(10),
            False
        )
        logger.info("Message sent to Node1 from Node2.")
    except Exception as e:
        logger.error(f"Error in Node2: {e}")

    # Event to keep the script alive
    stop_event = Event()

    try:
        logger.info(f"Node2 is running at {node_ip}:9090. Waiting for communication...")
        stop_event.wait()  # Keep the program running
    except KeyboardInterrupt:
        logger.info("Node2 shutting down...")
