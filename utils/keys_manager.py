import base64
import json
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from config import KeysSettings, FilesSettings
from logging_utils import setup_logger

logger = setup_logger()

# Define the relative path for the data folder and JSON file
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", str(FilesSettings.DATA_FOLDER_NAME))
KEYS_FILE = os.path.join(DATA_FOLDER, FilesSettings.KEYS_FILENAME)

# Ensure the data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)


def generate_and_save_keys(sk_name, pk_name):
    """
    Generate an RSA key pair, and save or update them in the JSON file.
    If the keys exist in the file, update their values; otherwise, append new keys.

    :param sk_name: The name for the private key
    :param pk_name: The name for the public key
    :return: None
    """
    try:
        # Generate private and public keys
        sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pk = sk.public_key()

        # Export keys to PEM format and encode as Base64 strings
        private_pem = sk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = pk.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        encoded_private_key = base64.b64encode(private_pem).decode('utf-8')
        encoded_public_key = base64.b64encode(public_pem).decode('utf-8')

        # Load existing keys or initialize new dictionary
        keys_dict = {}
        if os.path.exists(KEYS_FILE):
            with open(KEYS_FILE, 'r') as json_file:
                keys_dict = json.load(json_file)

        # Update or append new keys
        keys_dict[sk_name] = encoded_private_key
        keys_dict[pk_name] = encoded_public_key

        # Save back to the JSON file
        with open(KEYS_FILE, 'w') as json_file:
            json.dump(keys_dict, json_file, indent=4)

        logger.info(f"Keys '{sk_name}' and '{pk_name}' saved/updated successfully in {KEYS_FILE}")

    except Exception as e:
        logger.error(f"Error generating or saving keys: {e}")


def load_key(key_name, private_key):
    """
    Load a single RSA key (private or public) from the JSON file.
    :param key_name: The name of the key to load
    :param private_key: is the key private or public
    :return: The key object (private or public), or None if the key is missing
    """

    try:
        if not os.path.exists(KEYS_FILE):
            logger.error(f"No keys file found at {KEYS_FILE}")
            return None

        # Load the keys from JSON
        with open(KEYS_FILE, 'r') as json_file:
            keys_dict = json.load(json_file)

        if key_name not in keys_dict:
            logger.error(f"Key '{key_name}' not found in {KEYS_FILE}")
            return None

        # Decode the Base64 string and load the PEM key
        key_pem = base64.b64decode(keys_dict[key_name])

        if private_key:
            # Load private key
            key = serialization.load_pem_private_key(key_pem, password=None)
        else:
            # Load public key
            key = serialization.load_pem_public_key(key_pem)

        logger.info(f"Key '{key_name}' loaded successfully from {KEYS_FILE}")
        return key

    except Exception as e:
        logger.error(f"Error loading key '{key_name}': {e}")
        return None


def create_all_keys():
    generate_and_save_keys(KeysSettings.LORD_SK, KeysSettings.LORD_PK)
    generate_and_save_keys(KeysSettings.TIPPING_SK, KeysSettings.TIPPING_PK)
    generate_and_save_keys(KeysSettings.BONUS_SK, KeysSettings.BONUS_PK)

    tipping = load_key(KeysSettings.TIPPING_PK, False)
    assert load_key(KeysSettings.TIPPING_SK, True)
    assert load_key(KeysSettings.LORD_PK, False)


if __name__ == "__main__":
    create_all_keys()
