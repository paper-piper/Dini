"""
Implements a very simple looking “Send Message” and “Receive Message”.
A functions which takes message type, message subtype and message parameters.
"""

import pickle
from utils.logging_utils import setup_logger
from utils.config import MsgTypes, MsgSubTypes, MsgStructure
from core.blockchain import Transaction, Blockchain, Block


# Setup logger for file
logger = setup_logger("protocol")


def receive_message(sock):
    """
    Receives and decrypts an encrypted message from the socket.
    :param sock: The socket from which the message is received.
    :return: A tuple of message type, subtype, and the decoded message object
    """
    try:
        msg_type, msg_sub_type, params = receive_socket_message(sock)

        return msg_type, msg_sub_type, params
    except (pickle.PickleError, ValueError, ConnectionError) as e:
        logger.error(f"Failed to receive and decode message: {e}")
        raise


def receive_socket_message(sock):
    # Step 1: Read the message length until encountering ":"
    message_len_str = ""
    while True:
        char = sock.recv(1).decode()  # Read one byte, decode it to a string
        if char == ":":
            break
        message_len_str += char  # Add the character to the length string

    message_len = int(message_len_str)  # Convert the length to an integer

    # Step 2: get msg type and subtype
    msg_type = get_msg_section(sock)

    msg_subtype = get_msg_section(sock)

    # Step 3: Read the rest of the message with the specified length
    # First check for no parameters
    if message_len == 0:
        return msg_type, msg_subtype, None

    byte_sequence = bytearray()
    while len(byte_sequence) < message_len:
        byte = sock.recv(1)  # Read one byte at a time
        byte_sequence.extend(byte)   # Add the character to the message

    param_bytes = bytes(byte_sequence)
    param_dictionary = decrypt_msg_params(msg_subtype, param_bytes)
    return msg_type, msg_subtype, param_dictionary


def get_msg_section(sock, length=4):
    section = ""
    for i in range(length):
        char = sock.recv(1).decode()  # Read one byte, decode it to a string
        section += char
    return section


def decrypt_msg_params(msg_subtype, params_bytes):
    params_dictionary = pickle.loads(params_bytes)

    # try and convert the main object to an object from dictionary
    main_object_dict = params_dictionary[0]
    main_object = None
    match msg_subtype:
        case MsgSubTypes.BLOCK:
            main_object = Block.from_dict(main_object_dict)

        case MsgSubTypes.TRANSACTION:
            main_object = Transaction.from_dict(main_object_dict)

        case MsgSubTypes.BLOCKCHAIN:
            main_object = Blockchain.from_dict(main_object_dict)

        case MsgSubTypes.NODE_ADDRESS:
            # address is just a tuple, no need to convert
            main_object = main_object_dict

        case MsgSubTypes.TEST:
            # just for testing, no need to convert
            main_object = main_object_dict

        case _:
            logger.error(f"Got invalid message subtype: {msg_subtype}")

    params_dictionary[0] = main_object
    return params_dictionary


def send_message(sock, msg_type, msg_sub_type, *msg_params):
    """
    Constructs and sends an encrypted message over the socket.
    :param sock: The socket through which the message is sent.
    :param msg_type: The primary command type (e.g., SEND, REQUEST).
    :param msg_sub_type: The specific object type (e.g., peer, block, transaction).
    :param msg_params: Additional parameters for the message.
    :return: None
    """
    try:
        message = construct_message(msg_type, msg_sub_type, *msg_params)
        sock.sendall(message)
    except (OSError, ValueError) as e:
        logger.error(f"Failed to send message: {e}")
        raise


def construct_message(msg_type: str, msg_sub_type: str, *params) -> bytes:
    """
    Constructs a message according to protocol, serializing and structuring the components.
    :param msg_type: The primary command type (e.g., SEND, REQUEST).
    :param msg_sub_type: The specific object type (e.g., peer, block, transaction).
    :param params: Message parameters to be serialized.
    :return: The constructed message as bytes
    """
    try:
        msg_type_encoded = msg_type.encode()
        msg_sub_type_encoded = msg_sub_type.encode()

        # if the msg type is request, there is no parameters
        if msg_type == MsgTypes.REQUEST_OBJECT:
            msg_len = '0'
            message = msg_len.encode() + MsgStructure.DIVIDER + msg_type_encoded + msg_sub_type_encoded
            return message

        msg_params = [param for param in params]
        # else, it is a send message
        if hasattr(msg_params[0], "to_dict"):
            msg_params[0] = msg_params[0].to_dict()
        params_data = pickle.dumps(msg_params)
        msg_len = str(len(params_data)).encode()

        message = msg_len + MsgStructure.DIVIDER + msg_type_encoded + msg_sub_type_encoded + params_data
        return message

    except (pickle.PickleError, ValueError) as e:
        logger.error(f"Failed to construct message: {e}")
        raise
