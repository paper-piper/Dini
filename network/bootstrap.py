import os
from communication.node import Node
import json
from utils.config import MsgTypes, MsgSubTypes, FilesSettings, NodeSettings
from utils.logging_utils import configure_logger


class Bootstrap(Node):

    def __init__(
            self,
            is_bootstrap=True,
            port=8000,
            node_connections=None,
            ip=None,
            child_dir="Bootstrap",
            name=NodeSettings.DEFAULT_NAME

    ):
        super().__init__(port,
                         node_connections=node_connections,
                         ip=ip,
                         child_dir=child_dir,
                         name=name
                         )

        self.bootstrap_logger = configure_logger(
            class_name="Bootstrap",
            child_dir=child_dir,
            instance_id=f"{self.ip}-{self.port}"
        )
        if is_bootstrap:
            self.add_bootstrap_address()

        if not self.node_connections:
            self.discover_peers()

    def __del__(self):
        super().__del__()
        self.delete_bootstrap_address()

    def discover_peers(self):
        bootstrap_addresses = self.get_bootstrap_addresses()
        for address in bootstrap_addresses:
            # convert the list to a tuple
            self.connect_to_node(address)

        # after connecting to all available bootstrap addresses, send a distributed request peer msg
        self.bootstrap_logger.debug("Sending nodes discovery message")
        self.send_distributed_message(MsgTypes.REQUEST, MsgSubTypes.NODE_ADDRESS)

    def get_bootstrap_addresses(self):
        """
        Retrieves the list of bootstrap server addresses from the config file.

        :return: List of bootstrap addresses, or an empty list if none exist.
        """
        try:
            # Load the configuration file using the helper function
            config = self._load_config()

            # Get the bootstrap addresses list, defaulting to an empty list if not found
            addresses = config.get("bootstrap_addresses", [])

            # Convert each address from a list to a tuple
            return [tuple(address) for address in addresses]

        except Exception as e:
            self.bootstrap_logger.error(f"An error occurred while retrieving bootstrap addresses: {e}")
            return []

    def add_bootstrap_address(self):
        """Adds a new bootstrap server address to the config file."""
        config = self._load_config()

        # Normalize self.address for comparison
        address_as_list = list(self.address)

        # Add the address if it's not already in the list
        if address_as_list not in config["bootstrap_addresses"]:
            config["bootstrap_addresses"].append(address_as_list)
            self.bootstrap_logger.info(f"Added bootstrap address: {self.address} to data")
            self._save_config(config)

    def delete_bootstrap_address(self):
        """Deletes the bootstrap server address from the config file."""
        config = self._load_config()

        # Normalize self.address for comparison
        address_as_list = list(self.address)

        # Remove the address if it exists in the list
        if address_as_list in config["bootstrap_addresses"]:
            config["bootstrap_addresses"].remove(address_as_list)
            self.bootstrap_logger.info(f"Deleted bootstrap address: {self.address}")
            self._save_config(config)
        else:
            self.bootstrap_logger.warning(f"Bootstrap address {self.address} not found.")

    def serve_node_request(self):
        # Implementation for Bootstrap
        peer_addresses = list(self.node_connections.keys())
        return peer_addresses

    def process_node_data(self, peer_addresses):
        for address in peer_addresses:
            self.connect_to_node(address)

    def process_block_data(self, params):
        """
        Handles sending block information.
        :param params: Parameters for block sending.
        """
        self.bootstrap_logger.debug(f"Bootstrap does not handle blocks")

    def process_blockchain_data(self, params):
        self.bootstrap_logger.debug(f"Bootstrap does not handle block sending")

    def process_transaction_data(self, params):
        self.bootstrap_logger.debug(f"Bootstrap does not handle transactions")

    def serve_blockchain_request(self, latest_hash):
        self.bootstrap_logger.debug(f"Bootstrap does not handle block requests")

    def get_public_key(self):
        return None

    def _load_config(self):
        bootstrap_config_filepath = os.path.join(
            FilesSettings.DATA_ROOT_DIRECTORY,
            FilesSettings.BOOTSTRAP_CONFIG_FILENAME
        )
        """Loads the configuration file, initializing it if it doesn't exist or is empty."""
        if not os.path.exists(bootstrap_config_filepath) or os.path.getsize(bootstrap_config_filepath) == 0:
            # File does not exist or is empty, initialize with an empty list
            return {"bootstrap_addresses": []}

        try:
            with open(bootstrap_config_filepath, 'r') as config_file:
                return json.load(config_file)
        except json.JSONDecodeError as e:
            self.bootstrap_logger.error(f"Config file is corrupted. Reinitializing it. {e}")
            return {"bootstrap_addresses": []}
        except Exception as e:
            self.bootstrap_logger.error(f"An error occurred while loading the config: {e}")
            return {"bootstrap_addresses": []}

    def _save_config(self, config):
        bootstrap_config_filepath = os.path.join(
            FilesSettings.DATA_ROOT_DIRECTORY,
            FilesSettings.BOOTSTRAP_CONFIG_FILENAME
        )
        """Saves the updated configuration to the config file."""
        try:
            with open(bootstrap_config_filepath, 'w') as config_file:
                json.dump(config, config_file, indent=4)
        except Exception as e:
            self.bootstrap_logger.error(f"An error occurred while saving the config: {e}")


if __name__ == "__main__":
    boot = Bootstrap()
    boot.bootstrap_logger.info("Another message from bootstrap")
