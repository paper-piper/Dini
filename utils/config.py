import hashlib
import os

from cryptography.hazmat.primitives.asymmetric import rsa


def get_sk_pk_pair():
    # a placeholder function, need to create for actual global pk,sk
    ps = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return ps, ps.public_key()


class TransactionSettings:
    MAX_AMOUNT = 10 ** 6


class BlockSettings:
    MAX_TRANSACTIONS = 1024
    BONUS_AMOUNT = 100
    PROCESSES_NUMBER = 10


class BlockChainSettings:
    FIRST_GEN_ENCODED_STR = '5f6bef989faab6438c2eacd664f0fd3ac7523ab688e6ed68560b0eb152bcf76c|Transaction(Sender: 270..., Recipient: 270..., Amount: 0, Tip: 0)|2|time-zero|0'
    FIRST_HASH = hashlib.sha256(FIRST_GEN_ENCODED_STR.encode()).hexdigest()


class KeysSettings:
    GEN_SK, GEN_PK = "gen_sk", "gen_pk"
    LORD_SK, LORD_PK = "lord_sk", "lord_pk"
    BONUS_SK, BONUS_PK = "bonus_sk", "bonus_pk"
    TIPPING_SK, TIPPING_PK = "tipping_sk", "tipping_pk"


class FilesSettings:
    LOGS_FOLDER_NAME = "logs"
    DATA_FOLDER_NAME = "data"
    DATA_ROOT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", DATA_FOLDER_NAME)
    BOOTSTRAP_CONFIG_FILENAME = "bootstrap_config.json"
    KEYS_FILENAME = "keys.json"
    WALLET_FILE_NAME = "wallet.json"
    BLOCKCHAIN_FILE_NAME = "core.json"


class MsgStructure:
    # NEED TO BE CAREFUL ABOUT THAT VALUE, BECAUSE IT WILL LEAD TO A CRASH IN ENCODING
    ENCRYPTION_KEY = b'A_cyjLQL7Fa2331XceidKn0F7NtgGVG-NAzNmPWnKVM='
    LENGTH_FIELD_SIZE = 4
    MSG_TYPE_LENGTH = 4
    DIVIDER = ':'.encode()


class MsgTypes:
    RESPONSE_OBJECT = "resp"
    REQUEST_OBJECT = "reqt"
    BROADCAST_OBJECT = "bcst"


class MsgSubTypes:
    TEST = "test"
    NODE_ADDRESS = "node"
    NODE_INIT = "init"
    BLOCK = "blok"
    TRANSACTION = "trsn"
    BLOCKCHAIN = "bkcn"


class MsgSideParameters:
    DONT_PASS = False
    PASS = True


class MinerSettings:
    PROCESSES_NUMBER = 7
    PROCESS_RANGE = 10 ** 4
    DIFFICULTY_LEVEL = 2


class BootSettings:
    ADDRESSES_LIST = "bootstrap_addresses"
    BOOTSTRAP_SERVERS = 3


class LoggingSettings:
    REWRITE = False
    BASIC_LOGS = "basic"


class PortSettings:
    BOOTSTRAP_RANGE = (5000, 5500)
    USER_RANGE = (5501, 5800)
    MINER_RANGE = (5801, 6000)
    GENERAL_RANGE = (5000, 6000)
