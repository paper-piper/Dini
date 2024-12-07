import hashlib

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
    FIRST_HASH = hashlib.sha256('0'.encode()).hexdigest().encode()


class KeysSettings:
    LORD_SK, LORD_PK = "lord_sk", "lord_pk"
    BONUS_SK, BONUS_PK = "bonus_sk", "bonus_pk"
    TIPPING_SK, TIPPING_PK = "tipping_sk", "tipping_pk"


class FilesSettings:
    LOGS_FOLDER_NAME = "logs"
    DATA_FOLDER_NAME = "data"
    KEYS_FILENAME = "keys.json"
    BLOCKCHAIN_FILE_NAME = "core.txt"


class MsgStructure:
    # NEED TO BE CAREFUL ABOUT THAT VALUE, BECAUSE IT WILL LEAD TO A CRASH IN ENCODING
    ENCRYPTION_KEY = b'A_cyjLQL7Fa2331XceidKn0F7NtgGVG-NAzNmPWnKVM='
    LENGTH_FIELD_SIZE = 4
    MSG_TYPE_LENGTH = 4
    DIVIDER = ':'.encode()


class MsgTypes:
    SEND_OBJECT = "send"
    REQUEST_OBJECT = "reqt"


class MsgSubTypes:
    TEST = "test"
    PEER_ADDRESS = "peer"
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
    CONFIG_PATH = r"bootstrap_config.json"
    ADDRESSES_LIST = "bootstrap_addresses"
    BOOTSTRAP_SERVERS = 3


class LoggingSettings:
    REWRITE = True


class PortSettings:
    BOOTSTRAP_RANGE = (5000, 5500)
    USER_RANGE = (5501, 5800)
    MINER_RANGE = (5801, 6000)
