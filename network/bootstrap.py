import os

from communication.node import Node
import json
from utils.config import MsgTypes, MsgSubTypes, FilesSettings
from utils.logging_utils import setup_logger
logger = setup_logger()


class Bootstrap(Node):

    def __init__(self, is_bootstrap=True, port=8000, node_connections=None, ip=None, port_manager=None):
        super().__init__(port, node_connections=node_connections, ip=ip, port_manager=port_manager)
        if is_bootstrap:
            self.add_bootstrap_address()

        if not self.node_connections:
            self.discover_peers()

    def __del__(self):
        super().__del__()
        self.delete_bootstrap_address()

    def discover_peers(self):
        bootstrap_addresses = self.get_bootstrap_addresses()
        logger.info(f"Bootstrap ({self.address}): tried to connect to bootstrap addresses, got the address: {bootstrap_addresses}")
        for address in bootstrap_addresses:
            # convert the list to a tuple
            self.connect_to_node(address)

        # after connecting to all available bootstrap addresses, send a distributed request peer msg
        self.send_distributed_message(MsgTypes.REQUEST_OBJECT, MsgSubTypes.NODE_ADDRESS)
        logger.info(f"Bootstrap ({self.address}): Send a distributed request for nodes")

    def get_bootstrap_addresses(self):
        """
        Retrieves the list of bootstrap server addresses from the config file.

        :return: List of bootstrap addresses, or an empty list if none exist.
        """
        try:
            # Load the configuration file using the helper function
            config = _load_config()

            # Get the bootstrap addresses list, defaulting to an empty list if not found
            addresses = config.get("bootstrap_addresses", [])

            # Convert each address from a list to a tuple
            return [tuple(address) for address in addresses]

        except Exception as e:
            logger.error(f"Bootstrap ({self.address}): An error occurred while retrieving bootstrap addresses: {e}")
            return []

    def add_bootstrap_address(self):
        """Adds a new bootstrap server address to the config file."""
        config = _load_config()

        # Normalize self.address for comparison
        address_as_list = list(self.address)

        # Add the address if it's not already in the list
        if address_as_list not in config["bootstrap_addresses"]:
            config["bootstrap_addresses"].append(address_as_list)
            logger.info(f"Bootstrap ({self.address}): Added new bootstrap address: {self.address}")
            _save_config(config)
        else:
            logger.info(f"Bootstrap ({self.address}): Bootstrap address {self.address} already exists.")

    def delete_bootstrap_address(self):
        """Deletes the bootstrap server address from the config file."""
        config = _load_config()

        # Normalize self.address for comparison
        address_as_list = list(self.address)

        # Remove the address if it exists in the list
        if address_as_list in config["bootstrap_addresses"]:
            config["bootstrap_addresses"].remove(address_as_list)
            logger.info(f"Bootstrap ({self.address}): Deleted bootstrap address: {self.address}")
            _save_config(config)
        else:
            logger.warning(f"Bootstrap ({self.address}): Bootstrap address {self.address} not found.")

    def serve_node_request(self):
        # Implementation for Bootstrap
        peer_addresses = list(self.node_connections.keys())
        logger.info(f"Bootstrap ({self.address}): Received peer request, returned the peers addresses: {peer_addresses}")
        return peer_addresses

    def process_node_data(self, peer_addresses):
        # Implementation for Bootstrap
        logger.info(f"Bootstrap ({self.address}): Received peer data: {peer_addresses}")
        for address in peer_addresses:
            self.connect_to_node(address)

    def process_block_data(self, params):
        """
        Handles sending block information.
        :param params: Parameters for block sending.
        """
        logger.debug("Bootstrap ({self.address}): Bootstrap does not handle blocks")

    def process_blockchain_data(self, params):
        logger.debug("Bootstrap ({self.address}): Bootstrap does not handle block sending")

    def process_transaction_data(self, params):
        logger.debug("Bootstrap ({self.address}): Bootstrap does not handle transactions")

    def serve_blockchain_request(self, latest_hash):
        logger.debug("Bootstrap ({self.address}): Bootstrap does not handle block requests")


def _load_config():
    bootstrap_config_filepath = os.path.join(FilesSettings.DATA_ROOT_DIRECTORY, FilesSettings.BOOTSTRAP_CONFIG_FILENAME)
    """Loads the configuration file, initializing it if it doesn't exist or is empty."""
    if not os.path.exists(bootstrap_config_filepath) or os.path.getsize(bootstrap_config_filepath) == 0:
        # File does not exist or is empty, initialize with an empty list
        return {"bootstrap_addresses": []}

    try:
        with open(bootstrap_config_filepath, 'r') as config_file:
            return json.load(config_file)
    except json.JSONDecodeError as e:
        logger.error(f"Config file is corrupted. Reinitializing it. {e}")
        return {"bootstrap_addresses": []}
    except Exception as e:
        logger.error(f"An error occurred while loading the config: {e}")
        return {"bootstrap_addresses": []}


def _save_config(config):
    bootstrap_config_filepath = os.path.join(FilesSettings.DATA_ROOT_DIRECTORY, FilesSettings.BOOTSTRAP_CONFIG_FILENAME)
    """Saves the updated configuration to the config file."""
    try:
        with open(bootstrap_config_filepath, 'w') as config_file:
            json.dump(config, config_file, indent=4)
    except Exception as e:
        logger.error(f"An error occurred while saving the config: {e}")
