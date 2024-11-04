import pickle
from dini_Settings import ProtocolSettings
import struct
from logging_utils import setup_logger
from Blockchain.transaction import Transaction, get_sk_pk_pair
from Blockchain.blockchain import Blockchain
from Blockchain.block import Block
from Node.node import Node
# Setup logger for file
logger = setup_logger("protocol_module")


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
        encrypted_message = encrypt_object(message)
        sock.sendall(encrypted_message)
    except (OSError, ValueError) as e:
        logger.error(f"Failed to send message: {e}")
        raise


def receive_message(sock):
    """
    Receives and decrypts an encrypted message from the socket.
    :param sock: The socket from which the message is received.
    :return: A tuple of message type, subtype, and the decoded message object
    """
    try:
        encrypted_msg_type, encrypted_msg_sub_type, encrypted_params = receive_encrypted_message(sock)
        msg_type = decrypt_object(encrypted_msg_type)
        msg_sub_type = decrypt_object(encrypted_msg_sub_type)

        # if request object, the params are empty
        if msg_type == ProtocolSettings.REQUEST_OBJECT:
            return msg_type, msg_sub_type, None

        params_bytes = decrypt_object(encrypted_params)
        params = pickle.loads(params_bytes)
        # Handle specific message types with object conversion if needed
        main_param = params[0]

        match msg_sub_type:
            case ProtocolSettings.TRANSACTION:
                main_param = Transaction.from_dict(main_param)
            case ProtocolSettings.BLOCK:
                main_param = Block.from_dict(main_param)
            case ProtocolSettings.BLOCKCHAIN:
                main_param = Blockchain.from_dict(main_param)
            case ProtocolSettings.PEER:
                main_param = Node.from_dict(main_param)

        params[0] = main_param

        return msg_type, msg_sub_type, params
    except (pickle.PickleError, ValueError, ConnectionError) as e:
        logger.error(f"Failed to receive and decode message: {e}")
        raise


def encrypt_object(message_object) -> bytes:
    """
    Placeholder for encryption function.
    :param message_object: The message object to encrypt.
    :return: The encrypted message as bytes
    """
    return message_object


def decrypt_object(message_object):
    """
    Placeholder for decryption function.
    :param message_object: The encrypted message object to decrypt.
    :return: The decrypted message
    """
    if message_object is None:
        return None
    return message_object


def receive_encrypted_message(sock) -> tuple:
    """
    Receives an encrypted message, extracting message length, type, sub-type, and parameters.
    :param sock: The socket from which the message is received.
    :return: A tuple of encrypted message type, sub-type, and parameters
    """
    try:
        # Step 1: Read and decrypt the message length field
        length_field_bytes = bytearray()
        while len(length_field_bytes) < 4:  # Message length is always 4 bytes
            byte = sock.recv(1)
            if not byte:
                raise ConnectionError("Socket connection closed unexpectedly")
            length_field_bytes.extend(byte)

        encrypted_length = bytes(length_field_bytes)
        decrypted_length = decrypt_object(encrypted_length)
        msg_length = struct.unpack('!I', decrypted_length)[0]

        # Step 2: Read the message type field
        message_type_bytes = bytearray()
        while len(message_type_bytes) < 4:  # Message type is always 4 bytes
            byte = sock.recv(1)
            if not byte:
                raise ConnectionError("Socket connection closed unexpectedly")
            message_type_bytes.extend(byte)

        encrypted_message_type = bytes(message_type_bytes)

        # Step 3: Read the message sub-type field
        message_sub_type_bytes = bytearray()
        while len(message_sub_type_bytes) < 4:  # Message sub-type is always 4 bytes
            byte = sock.recv(1)
            if not byte:
                raise ConnectionError("Socket connection closed unexpectedly")
            message_sub_type_bytes.extend(byte)

        encrypted_message_sub_type = bytes(message_sub_type_bytes)

        # Step 4: Read the exact number of bytes for the message parameters
        params_data = bytearray()
        while len(params_data) < msg_length:
            byte = sock.recv(1)
            if not byte:
                raise ConnectionError("Socket connection closed unexpectedly")
            params_data.extend(byte)

        encrypted_params = bytes(params_data)
        return encrypted_message_type, encrypted_message_sub_type, encrypted_params

    except (OSError, ConnectionError) as e:
        logger.error(f"Failed to receive encrypted message: {e}")
        raise


def construct_message(msg_type: str, msg_sub_type: str, *msg_params) -> bytes:
    """
    Constructs a message according to protocol, serializing and structuring the components.
    :param msg_type: The primary command type (e.g., SEND, REQUEST).
    :param msg_sub_type: The specific object type (e.g., peer, block, transaction).
    :param msg_params: Message parameters to be serialized.
    :return: The constructed message as bytes
    """
    try:
        # TODO: handle no parameters
        if len(msg_params) > 0 and hasattr(msg_params[0], "to_dict"):
            msg_params = (msg_params[0].to_dict(),) + msg_params[1:]

        params_data = pickle.dumps(list(msg_params))
        params_max_size = 2 ** (4 * 8)  # 4 bytes for length
        if len(params_data) > params_max_size:
            raise ValueError("Encoded message exceeds maximum allowable length.")

        msg_type_encoded = msg_type.encode('utf-8').ljust(4, b'\x00')
        msg_sub_type_encoded = msg_sub_type.encode('utf-8').ljust(4, b'\x00')

        full_message = msg_type_encoded + msg_sub_type_encoded + params_data
        message_length = len(params_data)
        length_prefix = struct.pack('!I', message_length)

        final_message = length_prefix + full_message
        return final_message

    except (pickle.PickleError, ValueError) as e:
        logger.error(f"Failed to construct message: {e}")
        raise


def assertion_check():
    """
    Tests core functions to validate expected functionality.
    """
    test_sock = None  # Placeholder for actual socket testing if implemented
    _, pk = get_sk_pk_pair()
    _, recvpk = get_sk_pk_pair()
    transaction = Transaction(pk, recvpk, 100)
    assert construct_message(ProtocolSettings.SEND_OBJECT, ProtocolSettings.TRANSACTION, transaction)  # Check construct_message

    test_object = b"sample_object"
    encrypted = encrypt_object(test_object)
    decrypted = decrypt_object(encrypted)
    assert decrypted == test_object, "Encrypt/Decrypt test failed"

    logger.info("All assertions passed.")


if __name__ == "__main__":
    assertion_check()
