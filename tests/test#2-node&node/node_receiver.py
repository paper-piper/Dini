from communication.node import Node
from threading import Event
from utils.logging_utils import setup_basic_logger

logger = setup_basic_logger()


NODE1_IP = "127.0.0.1"
NODE1_PORT = 8080


class Node1(Node):
    """
    A specialized Node class for testing Node-to-Node communication.
    """

    def serve_blockchain_request(self, latest_hash):
        logger.info("Node1 received a block request.")
        return {"block_data": "Sample block from Node1"}

    def serve_node_request(self):
        logger.info("Node1 received a peer request.")
        return {"peer_list": list(self.node_connections.keys())}

    def process_blockchain_data(self, params):
        logger.info(f"Node1 received a block: {params}")
        return False  # Indicate the block has not been seen before.

    def process_node_data(self, params):
        logger.info(f"Node1 received a peer update: {params}")

    def process_transaction_data(self, params):
        logger.info(f"Node1 received a transaction: {params}")
        return False

    def process_test_data(self, params):
        logger.info(f"received test message! ({params})")

    def process_block_data(self, params):
        logger.info(f"Node2 received a block: {params}")
        return False


if __name__ == "__main__":
    # Use localhost for same-computer testing

    # Initialize Node1 on port 8080
    node1 = Node1(port=NODE1_PORT, ip=NODE1_IP)

    # Event to keep the script alive
    stop_event = Event()

    try:
        logger.info(f"Node1 is running at {NODE1_IP}:{NODE1_PORT}. Waiting for communication...")
        stop_event.wait()  # Keep the program running
    except KeyboardInterrupt:
        logger.info("Node1 shutting down...")
