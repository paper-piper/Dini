class BlockSettings:
    MAX_TRANSACTIONS = 1024
    BONUS_PK = "some_string"
    BONUS_AMOUNT = 100
    PROCESSES_NUMBER = 10


class TransactionSettings:
    MAX_AMOUNT = 10 ** 6


class File:
    BLOCKCHAIN_FILE_NAME = "Blockchain.txt"


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
    PROCESSES_NUMBER = 10
    PROCESS_RANGE = 10 ** 4
    DIFFICULTY_LEVEL = 2


class BootSettings:
    CONFIG_PATH = r"config.json"
    ADDRESSES_LIST = "bootstrap_addresses"


class LoggingSettings:
    REWRITE = True
