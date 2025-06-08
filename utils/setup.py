import json
import os
from utils.config import FilesSettings, IPSettings, FrontendEnvSettings
from utils.logging_utils import setup_basic_logger

logger = setup_basic_logger()


def add_bootstrap_address(ip, port):
    """Adds a new bootstrap server address to the config file."""
    config = _load_config()

    # Normalize self.address for comparison
    address_as_list = [ip, port]

    # Add the address if it's not already in the list
    if address_as_list not in config["bootstrap_addresses"]:
        config["bootstrap_addresses"].append(address_as_list)
        logger.info(f"Added bootstrap address: {ip}:{port} to data")
        _save_config(config)


def _load_config():
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
        logger.error(f"Config file is corrupted. Reinitializing it. {e}")
        return {"bootstrap_addresses": []}
    except Exception as e:
        logger.error(f"An error occurred while loading the config: {e}")
        return {"bootstrap_addresses": []}


def _save_config(config):
    bootstrap_config_filepath = os.path.join(
        FilesSettings.DATA_ROOT_DIRECTORY,
        FilesSettings.BOOTSTRAP_CONFIG_FILENAME
    )
    """Saves the updated configuration to the config file."""
    try:
        with open(bootstrap_config_filepath, 'w') as config_file:
            json.dump(config, config_file, indent=4)
    except Exception as e:
        logger.error(f"An error occurred while saving the config: {e}")


def config_env_frontend_file():
    with open(FrontendEnvSettings.ENV_FILEPATH, 'w') as f:
        f.write(f'{FrontendEnvSettings.BACKEND_SERVER_VARIABLE_NAME}={IPSettings.BACKEND_SERVER_IP}\n')


if __name__ == "__main__":
    if IPSettings.OUTER_BOOTSTRAP_IP and IPSettings.OUTER_BOOTSTRAP_PORT:
        add_bootstrap_address(IPSettings.OUTER_BOOTSTRAP_IP, IPSettings.OUTER_BOOTSTRAP_PORT)

    config_env_frontend_file()
