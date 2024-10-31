import pickle
from dini_Settings import ProtocolSettings
import struct
from logging_utils import setup_logger

# Setup logger for file
logger = setup_logger("protocol_module")


def send_message(sock, msg_type, *msg_params):
    """
    Constructs and sends an encrypted message over the socket.
    :param sock: The socket through which the message is sent.
    :param msg_type: The type of message being sent.
    :param msg_params: Additional parameters for the message.
    :return: None
    """
    try:
        message = construct_message(msg_type, *msg_params)
        encrypted_message = encrypt_object(message)
        sock.sendall(encrypted_message)
    except (OSError, ValueError) as e:
        logger.error(f"Failed to send message: {e}")
        raise


def receive_message(sock):
    """
    Receives and decrypts an encrypted message from the socket.
    :param sock: The socket from which the message is received.
    :return: A tuple of message type and the decoded message object
    """
    try:
        encrypted_msg_type, encrypted_raw_object = receive_encrypted_message(sock)
        msg_type = decrypt_object(encrypted_msg_type)
        object_bytes = decrypt_object(encrypted_raw_object)
        msg_object = pickle.loads(object_bytes)

        # If the first item is a dictionary string, attempt to rehydrate it
        if isinstance(msg_object[0], dict):
            match
            msg_object[0] = msg_object[0].__class__.from_dict(msg_object[0])

        return msg_type, msg_object
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
    Receives an encrypted message, extracting message length, type, and parameters.
    :param sock: The socket from which the message is received.
    :return: A tuple of encrypted message type and parameters
    """
    try:
        # Step 1: Read and decrypt the message length field
        length_field_bytes = bytearray()
        while len(length_field_bytes) < ProtocolSettings.LENGTH_FIELD_SIZE:
            byte = sock.recv(1)
            if not byte:
                raise ConnectionError("Socket connection closed unexpectedly")
            length_field_bytes.extend(byte)

        encrypted_length = bytes(length_field_bytes)
        decrypted_length = decrypt_object(encrypted_length)
        msg_length = struct.unpack('!I', decrypted_length)[0]  # Unpack as an integer

        # Step 2: Read the message type field
        message_type_bytes = bytearray()
        while len(message_type_bytes) < ProtocolSettings.MSG_TYPE_LENGTH:
            byte = sock.recv(1)
            if not byte:
                raise ConnectionError("Socket connection closed unexpectedly")
            message_type_bytes.extend(byte)

        encrypted_message_type = bytes(message_type_bytes)

        # Step 3: Read the exact number of bytes for the message parameters
        params_data = bytearray()
        while len(params_data) < msg_length:
            byte = sock.recv(1)
            if not byte:
                raise ConnectionError("Socket connection closed unexpectedly")
            params_data.extend(byte)

        encrypted_params = bytes(params_data)
        return encrypted_message_type, encrypted_params

    except (OSError, ConnectionError) as e:
        logger.error(f"Failed to receive encrypted message: {e}")
        raise


def construct_message(message_type: str, *message_params) -> bytes:
    """
    Constructs a message according to protocol, serializing and structuring the components.
    :param message_type: The type of message, encoded as a fixed-length field.
    :param message_params: Message parameters to be serialized.
    :return: The constructed message as bytes
    """
    try:
        if len(message_params) > 0 and hasattr(message_params[0], "to_dict"):
            # Convert the first parameter to a dictionary if it has to_dict method
            message_params = (message_params[0].to_dict(),) + message_params[1:]

        params_data = pickle.dumps(list(message_params))
        params_max_size = 2 ** (ProtocolSettings.LENGTH_FIELD_SIZE * 8)
        if len(params_data) > params_max_size:
            raise ValueError("Encoded message exceeds maximum allowable length.")

        message_type_encoded = message_type.encode('utf-8')
        if len(message_type_encoded) > ProtocolSettings.MSG_TYPE_LENGTH:
            raise ValueError("Message type exceeds maximum allowable length.")
        message_type_encoded = message_type_encoded.ljust(ProtocolSettings.MSG_TYPE_LENGTH, b'\x00')

        full_message = message_type_encoded + params_data
        message_length = len(params_data)
        length_format = {1: '!B', 2: '!H', 4: '!I', 8: '!Q'}.get(ProtocolSettings.LENGTH_FIELD_SIZE, '!I')
        length_prefix = struct.pack(length_format, message_length)

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
    assert construct_message("test", "param1", 123)  # Checking construct_message functionality

    # Encrypt/decrypt placeholders should round-trip without changes
    test_object = b"sample_object"
    encrypted = encrypt_object(test_object)
    decrypted = decrypt_object(encrypted)
    assert decrypted == test_object, "Encrypt/Decrypt test failed"

    # Additional tests as needed for all protocol functions
    logger.info("All assertions passed.")


if __name__ == "__main__":
    assertion_check()
