class BlockSettings:
    MAX_TRANSACTIONS = 1024
    BONUS_PK = "some_string"
    BONUS_AMOUNT = 100


class TransactionSettings:
    MAX_AMOUNT = 10 ** 6


class File:
    BLOCKCHAIN_FILE_NAME = "Blockchain.txt"


class MsgStructure:
    # NEED TO BE CAREFUL ABOUT THAT VALUE, BECAUSE IT WILL LEAD TO A CRASH IN ENCODING
    ENCRYPTION_KEY = b'A_cyjLQL7Fa2331XceidKn0F7NtgGVG-NAzNmPWnKVM='
    LENGTH_FIELD_SIZE = 4
    MSG_TYPE_LENGTH = 4


class MsgTypes:
    SEND_OBJECT = "send"
    REQUEST_OBJECT = "reqt"


class MsgSubTypes:
    TEST_TYPE = "test"
    PEER = "peer"
    BLOCK = "blok"
    BLOCKCHAIN = 'blkc'
    TRANSACTION = "trsn"


class MsgSideParameters:
    DONT_PASS = False
    PASS = True


class MinerSettings:
    PROCESSES_NUMBER = 10
    PROCESS_RANGE = 10 ** 4
    DIFFICULTY_LEVEL = 2


class Bootstrap:
    addresses = [('192.168.1.100', 5000)]  # replace with actual addresses
