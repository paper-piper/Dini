class BlockSettings:
    MAX_TRANSACTIONS = 1024
    BONUS_PK = "some_string"
    BONUS_AMOUNT = 100


class TransactionSettings:
    MAX_AMOUNT = 10 ** 6


class FileSettings:
    BLOCKCHAIN_FILE_NAME = "filename"


class ProtocolSettings:
    # NEED TO BE CAREFUL ABOUT THAT VALUE, BECAUSE IT WILL LEAD TO A CRASH IN ENCODING
    LENGTH_FIELD_SIZE = 4
    MSG_TYPE_LENGTH = 4

    # Message types
    SEND_OBJECT = "send"
    REQUEST_OBJECT = "reqt"

    # Message parameters
    PEER = "peer"
    BLOCK = "block"
    TRANSACTION = "transaction"
