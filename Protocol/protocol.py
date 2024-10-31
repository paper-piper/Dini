import pickle
from dini_Settings import ProtocolSettings
import struct
from logging_utils import setup_logger

# Setup logger for file
logger = setup_logger("protocol_module")

def send_message(sock, msg_type, msg_sub_type, *msg_params):
    """
    Constructs and sends an encrypted message over the socket.
    :param sock: The socket through which the message is sent.
    :param msg_type: The general type of the message (4 bytes).
    :param msg_sub_type: The specific sub-type of the message (4 bytes).
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
    :return: A tuple of message type, message sub-type, and the decoded message parameters
    """
    try:
        encrypted_msg_type, encrypted_msg_sub_type, encrypted_raw_object = receive_encrypted_message(sock)
        msg_type = decrypt_object(encrypted_msg_type)
        msg_sub_type = decrypt_object(encrypted_msg_sub_type)
        object_bytes = decrypt_object(encrypted_raw_object)
        msg_object = pickle.loads(object_bytes)

        if isinstance(msg_object[0], dict):
            msg_object[0] = msg_object[0].__class__.from_dict(msg_object[0])

        return msg_type, msg_sub_type, msg_object
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
    return message_object

def receive_encrypted_message(sock) -> tuple:
    """
    Receives an encrypted message, extracting message length, type, sub-type, and parameters.
    :param sock: The socket from which the message is received.
    :return: A tuple of encrypted message type, sub-type, and parameters
    """
    try:
        # Read and decrypt the message length field (4 bytes)
        length_field_bytes = sock.recv(4)
        if not length_field_bytes:
            raise ConnectionError("Socket connection closed unexpectedly")
        decrypted_length = decrypt_object(length_field_bytes)
        msg_length = struct.unpack('!I', decrypted_length)[0]

        # Read the message type (4 bytes)
        message_type_bytes = sock.recv(4)
        if not message_type_bytes:
            raise ConnectionError("Socket connection closed unexpectedly")
        encrypted_message_type = bytes(message_type_bytes)

        # Read the message sub-type (4 bytes)
        message_sub_type_bytes = sock.recv(4)
        if not message_sub_type_bytes:
            raise ConnectionError("Socket connection closed unexpectedly")
        encrypted_message_sub_type = bytes(message_sub_type_bytes)

        # Read the exact number of bytes for the message parameters
        params_data = sock.recv(msg_length)
        if len(params_data) < msg_length:
            raise ConnectionError("Incomplete message received")

        encrypted_params = bytes(params_data)
        return encrypted_message_type, encrypted_message_sub_type, encrypted_params

    except (OSError, ConnectionError) as e:
        logger.error(f"Failed to receive encrypted message: {e}")
        raise

def construct_message(msg_type: str, msg_sub_type: str, *msg_params) -> bytes:
    """
    Constructs a message according to protocol, serializing and structuring the components.
    :param msg_type: The general type of message (4 bytes).
    :param msg_sub_type: The specific sub-type of message (4 bytes).
    :param msg_params: Message parameters to be serialized.
    :return: The constructed message as bytes
    """
    try:
        # Convert first parameter if it has a to_dict method
        if len(msg_params) > 0 and hasattr(msg_params[0], "to_dict"):
            msg_params = (msg_params[0].to_dict(),) + msg_params[1:]

        # Serialize all parameters as a list
        params_data = pickle.dumps(list(msg_params))
        params_max_size = 2 ** (ProtocolSettings.LENGTH_FIELD_SIZE * 8)
        if len(params_data) > params_max_size:
            raise ValueError("Encoded message exceeds maximum allowable length.")

        # Encode msg_type and msg_sub_type, ensuring they are 4 bytes each
        msg_type_encoded = msg_type.encode('utf-8').ljust(4, b'\x00')
        msg_sub_type_encoded = msg_sub_type.encode('utf-8').ljust(4, b'\x00')

        # Construct the full message
        message_length = len(params_data)
        length_prefix = struct.pack('!I', message_length)  # 4 bytes for length
        full_message = length_prefix + msg_type_encoded + msg_sub_type_encoded + params_data

        return full_message

    except (pickle.PickleError, ValueError) as e:
        logger.error(f"Failed to construct message: {e}")
        raise

def assertion_check():
    """
    Tests core functions to validate expected functionality.
    """
    test_sock = None  # Placeholder for actual socket testing if implemented
    assert construct_message("TEST", "SUBT", "param1", 123)  # Checking construct_message functionality

    # Encrypt/decrypt placeholders should round-trip without changes
    test_object = b"sample_object"
    encrypted = encrypt_object(test_object)
    decrypted = decrypt_object(encrypted)
    assert decrypted == test_object, "Encrypt/Decrypt test failed"

    logger.info("All assertions passed.")

if __name__ == "__main__":
    assertion_check()
