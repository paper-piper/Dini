class BlockSettings:
    MAX_TRANSACTIONS = 1024
    LORD_PK = "lord_public_string"
    LORD_SK = "lord_secret_string"
    BONUS_PK = "bonus_public_string"
    BONUS_SK = "bonus_secret_string"
    TIPPING_PK = "tipping_public_string"
    BONUS_AMOUNT = 100
    PROCESSES_NUMBER = 10


class TransactionSettings:
    MAX_AMOUNT = 10 ** 6


class File:
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
    REWRITE = False


class PortSettings:
    BOOTSTRAP_RANGE = (5000, 5500)
    USER_RANGE = (5501, 5800)
    MINER_RANGE = (5801, 6000)