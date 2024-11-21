import os

from Node.node import Node
import json
from dini_settings import BootSettings, MsgTypes, MsgSubTypes
from logging_utils import setup_logger
import socket
logger = setup_logger("bootstrap")


class Bootstrap(Node):

    def __init__(self, is_bootstrap, port=8000, peer_connections=None, ip=None):
        super().__init__(port, peer_connections=peer_connections, ip=ip)
        if is_bootstrap:
            self.add_bootstrap_address()

        if not self.peer_connections:
            self.discover_peers()

    def __del__(self):
        self.delete_bootstrap_address()

    def discover_peers(self):
        bootstrap_addresses = self.get_bootstrap_addresses()
        logger.info(f"tried to connect to bootstrap addresses, got the address: {bootstrap_addresses}")
        for address in bootstrap_addresses:
            # convert the list to a tuple
            self.connect_to_node(address)

        # after connecting to all available bootstrap addresses, send a distributed request peer msg
        self.send_distributed_message(MsgTypes.REQUEST_OBJECT, MsgSubTypes.PEER_ADDRESS)

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
            logger.error(f"An error occurred while retrieving bootstrap addresses: {e}")
            return []

    def add_bootstrap_address(self):
        """Adds a new bootstrap server address to the config file."""
        config = _load_config()

        # Normalize self.address for comparison
        address_as_list = list(self.address)

        # Add the address if it's not already in the list
        if address_as_list not in config["bootstrap_addresses"]:
            config["bootstrap_addresses"].append(address_as_list)
            logger.info(f"Added new bootstrap address: {self.address}")
            _save_config(config)
        else:
            logger.info(f"Bootstrap address {self.address} already exists.")

    def delete_bootstrap_address(self):
        """Deletes the bootstrap server address from the config file."""
        config = _load_config()

        # Normalize self.address for comparison
        address_as_list = list(self.address)

        # Remove the address if it exists in the list
        if address_as_list in config["bootstrap_addresses"]:
            config["bootstrap_addresses"].remove(address_as_list)
            logger.info(f"Deleted bootstrap address: {self.address}")
            _save_config(config)
        else:
            logger.warning(f"Bootstrap address {self.address} not found.")

    def handle_block_request(self, latest_hash):
        raise NotImplementedError("Bootstrap does not handle block requests")

    def handle_peer_request(self):
        # Implementation for Bootstrap
        peer_addresses = self.peer_connections.keys()
        return peer_addresses

    def handle_peer_send(self, peer_addresses):
        # Implementation for Bootstrap
        for address in peer_addresses:
            self.connect_to_node(address)

    def handle_block_send(self, params):
        raise NotImplementedError("Bootstrap does not handle block sending")

    def handle_transaction_send(self, params):
        raise NotImplementedError("Bootstrap does not handle transactions")


def _load_config():
    """Loads the configuration file, initializing it if it doesn't exist or is empty."""
    if not os.path.exists(BootSettings.CONFIG_PATH) or os.path.getsize(BootSettings.CONFIG_PATH) == 0:
        # File does not exist or is empty, initialize with an empty list
        return {"bootstrap_addresses": []}

    try:
        with open(BootSettings.CONFIG_PATH, 'r') as config_file:
            return json.load(config_file)
    except json.JSONDecodeError as e:
        logger.error(f"Config file is corrupted. Reinitializing it. {e}")
        return {"bootstrap_addresses": []}
    except Exception as e:
        logger.error(f"An error occurred while loading the config: {e}")
        return {"bootstrap_addresses": []}


def _save_config(config):
    """Saves the updated configuration to the config file."""
    try:
        with open(BootSettings.CONFIG_PATH, 'w') as config_file:
            json.dump(config, config_file, indent=4)
    except Exception as e:
        logger.error(f"An error occurred while saving the config: {e}")