from node import Node
from threading import Event
from logging_utils import setup_logger
logger = setup_logger("node1")


class Node1(Node):
    """
    A specialized Node class for testing Node-to-Node communication.
    """

    def handle_block_request(self):
        logger.info("Node1 received a block request.")
        return {"block_data": "Sample block from Node1"}

    def handle_peer_request(self):
        logger.info("Node1 received a peer request.")
        return {"peer_list": list(self.peer_connections.keys())}

    def handle_block_send(self, params):
        logger.info(f"Node1 received a block: {params}")
        return False  # Indicate the block has not been seen before.

    def handle_peer_send(self, params):
        logger.info(f"Node1 received a peer update: {params}")

    def handle_transaction_send(self, params):
        logger.info(f"Node1 received a transaction: {params}")
        return False


if __name__ == "__main__":
    # Use localhost for same-computer testing
    node_ip = "127.0.0.1"

    # Initialize Node1 on port 8080
    node1 = Node1(port=8080, ip=node_ip)

    # Event to keep the script alive
    stop_event = Event()

    try:
        logger.info(f"Node1 is running at {node_ip}:8080. Waiting for communication...")
        stop_event.wait()  # Keep the program running
    except KeyboardInterrupt:
        logger.info("Node1 shutting down...")
