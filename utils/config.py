import hashlib
import logging
import os

from cffi.cffi_opcode import PRIM_INT8


class NodeSettings:
    DEFAULT_NAME = "nameless node"


class PortsRanges:
    RANGE_SIZE = 1000
    BOOTSTRAP_RANGE_START = 4000
    USER_RANGE_START = 5000
    MINER_RANGE_START = 5000


class TransactionSettings:
    MAX_AMOUNT = 10 ** 6


class ActionSettings:
    ID_LENGTH = 8


class ActionStatus:
    PENDING = "pending"
    APPROVED = "approved"
    FAILED = "failed"


class ActionType:
    BUY = "buy"
    SELL = "sell"
    TRANSFER = "transfer"
    MINE = "mine"
    TIP = "mining tip"


class BlockSettings:
    MAX_TRANSACTIONS = 1024
    BONUS_AMOUNT = 199
    USUAL_TIP = 5
    PROCESSES_NUMBER = 10


class BlockChainSettings:
    GENESYS_PREVIEWS_HASH_DATA = '5f6bef989faab6438c2eacd664f0fd3ac7523ab688e6ed68560b0eb152bcf76c|Transaction(Sender: 270..., Recipient: 270..., Amount: 0, Tip: 0)|2|time-zero|0'
    GENESYS_PREVIEWS_HASH = hashlib.sha256(GENESYS_PREVIEWS_HASH_DATA.encode()).hexdigest()
    # e4e5e801f8d62dc6564612ad956763af4ac2350080093abca3765b020fa6af6c

    GENESYS_HASH_DATA = 'e4e5e801f8d62dc6564612ad956763af4ac2350080093abca3765b020fa6af6c|Transaction(Sender: 251..., Recipient: 251..., Amount: 0, Tip: 0)|3|time-zero|0'
    GENESYS_HASH = hashlib.sha256(GENESYS_HASH_DATA.encode()).hexdigest()
    # 6c4709c3ec9daa2f9916b684c4eb5fb53912c883876e3f1cf817131d58d689e2


class KeysSettings:
    GENESIS_SK, GENESIS_PK = "gen_sk", "gen_pk"
    LORD_SK, LORD_PK = "lord_sk", "lord_pk"
    BONUS_SK, BONUS_PK = "bonus_sk", "bonus_pk"
    TIPPING_SK, TIPPING_PK = "tipping_sk", "tipping_pk"


class FilesSettings:
    LOGS_FOLDER_NAME = "logs"
    DATA_FOLDER_NAME = "data"
    SERVER_DATABASE_FILENAME = "users.db"
    DATA_ROOT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", DATA_FOLDER_NAME)
    BOOTSTRAP_CONFIG_FILENAME = "bootstrap_config.json"
    KEYS_FILENAME = "keys.json"
    WALLET_FILE_NAME = "wallet.json"
    BLOCKCHAIN_FILE_NAME = "blockchain.json"


class MsgStructure:
    # NEED TO BE CAREFUL ABOUT THAT VALUE, BECAUSE IT WILL LEAD TO A CRASH IN ENCODING
    ENCRYPTION_KEY = b'A_cyjLQL7Fa2331XceidKn0F7NtgGVG-NAzNmPWnKVM='
    LENGTH_FIELD_SIZE = 4
    MSG_TYPE_LENGTH = 4
    DIVIDER = ':'.encode()


class MsgTypes:
    RESPONSE = "resp"
    REQUEST = "reqt"
    BROADCAST = "bcst"
    ALL_MSG_TYPES = [RESPONSE, REQUEST, BROADCAST]


class MsgSubTypes:
    TEST = "test"
    NODE_ADDRESS = "node"
    NODE_INIT = "init"
    NODE_NAME = "name"
    BLOCK = "blok"
    TRANSACTION = "trsn"
    BLOCKCHAIN = "bkcn"
    ALL_MSGSUB_TYPES = [TEST, NODE_ADDRESS, NODE_INIT, NODE_NAME, BLOCK, TRANSACTION, BLOCKCHAIN]


class MinerSettings:
    PROCESSES_NUMBER = 7
    PROCESS_RANGE = 10 ** 4
    DIFFICULTY_LEVEL = 3


class LoggingSettings:
    REWRITE = True
    WRITE_BASIC_LOGS = False
    BASIC_LOGS = "basic"
    LOGGING_LEVEL = logging.INFO


class IPSettings:
    LOCAL_IP = "10.100.102.6"
    BACKEND_SERVER_IP = "10.100.102.6"
    OUTER_BOOTSTRAP_IP = "134.2134.53"  # none if there is not an outer bootstrap
    OUTER_BOOTSTRAP_PORT = 8000  # none if there is not an outer bootstrap


class FrontendEnvSettings:
    ENV_FILEPATH = "../frontend/.env"
    BACKEND_SERVER_VARIABLE_NAME = "NEXT_PUBLIC_API_IP"
