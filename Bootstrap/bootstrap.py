from Node.node import Node
import json
from dini_settings import BootSettings, MsgTypes, MsgSubTypes
from logging_utils import setup_logger
import socket
logger = setup_logger("bootstrap")


class Bootstrap(Node):

    def __init__(self, is_bootstrap, port=8000, peers_address=None):
        super().__init__(port)
        if is_bootstrap:
            self.add_bootstrap_address()

        if not peers_address:
            self.discover_peers()

    def discover_peers(self):
        bootstrap_addresses = self.get_bootstrap_addresses()
        for address in bootstrap_addresses:
            self.connect_to_node(address)

        # after connecting to all available bootstrap addresses, send a distributed request peer msg
        self.send_distributed_message(MsgTypes.REQUEST_OBJECT, MsgSubTypes.PEER)

    def get_bootstrap_addresses(self):
        """Retrieves the list of bootstrap server addresses from the config file."""
        try:
            # Load current config
            with open(BootSettings.CONFIG_PATH, 'r') as config_file:
                config = json.load(config_file)

            # Return the list if it exists, otherwise return an empty list
            return config.get('bootstrap_addresses', [])

        except (FileNotFoundError, json.JSONDecodeError):
            logger.error("Config file not found or is corrupted.")
            raise "Config file not found or is corrupted."
        except Exception as e:
            logger.error(f"An error occurred while discovering bootstrap addresses: {e}")
            raise f"An error occurred while discovering bootstrap addresses: {e}"

    def add_bootstrap_address(self):
        """Adds a new bootstrap server address to the config file."""
        try:
            # Load current config
            with open(BootSettings.CONFIG_PATH, 'r') as config_file:
                config = json.load(config_file)

            # Initialize bootstrap list if it doesn't exist
            if BootSettings.BOOTSTRAP_ADDRESS not in config:
                config[BootSettings.BOOTSTRAP_ADDRESS] = []

            # Add the new address if it's not already in the list
            if self.address not in config[BootSettings.BOOTSTRAP_ADDRESS]:
                config[BootSettings.BOOTSTRAP_ADDRESS].append(self.address)

            # Save updated config
            with open(BootSettings.CONFIG_PATH, 'w') as config_file:
                json.dump(config, config_file, indent=4)

            logger.info(f"Added new bootstrap address: {self.address}")

        except (FileNotFoundError, json.JSONDecodeError):
            logger.error("Config file not found or is corrupted.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    def handle_block_request(self):
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
