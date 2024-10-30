import socket
import pickle
import json
from dini_Settings import ProtocolSettings

# Message protocol
# <message len>:<message type>:<message parameters>

# Message types
SEND_OBJECT = "send"
REQUEST_OBJECT = "reqt"

# Message parameters
PEER = "peer"
BLOCK = "block"
TRANSACTION = "transaction"

# Message special characters
MESSAGE_DIVIDER = ":"


def send_message(sock, msg_type, *msg_params):
    message = construct_message(msg_type, *msg_params)
    encrypted_message = encrypt_object(message)
    # Convert the message to bytes and send it over the socket
    sock.sendall(encrypted_message)


def receive_message(sock):
    encrypted_msg_type, encrypted_raw_object = get_raw_message(sock)
    msg_type, received_object = decrypt_message(encrypted_raw_object)
    return msg_type, received_object


def get_raw_message(sock):
    # Step 1: Read the message length until encountering ":"
    message_len_str = ""
    while True:
        char = sock.recv(1).decode()  # Read one byte, decode it to a string
        if char == ":":
            break
        message_len_str += char  # Add the character to the length string

    message_len = int(message_len_str)  # Convert the length to an integer
    # Step 2: get the message type

    msg_type = ""
    # TODO: extract message type since message parameter is bytes
    # Step 2: Read the rest of the message with the specified length
    message = ""
    while len(message) < message_len:
        char = sock.recv(1).decode()  # Read one byte at a time
        message += char  # Add the character to the message

    return message


def encrypt_object(message) -> bytes:
    pass


def decrypt_message(message) -> object:
    pass

def construct_message(message_type, *params):
    """
    Constructs a message following the protocol format:
    <parameters length> : <message type> : <parameters>

    :param message_type: The type of message (e.g., "transaction").
    :param params: List of parameters to include in the message.
    :return: Formatted message as a string.
    """
    # Ensure parameters are in a list format
    parameters = list(params)

    # Serialize parameters as a JSON string for consistent formatting
    parameters_data = pickle.dumps(parameters)

    # Check parameter length against the maximum allowed length
    parameters_length = len(parameters_data)
    if parameters_length > ProtocolSettings.MAX_PARAMETER_LENGTH:
        raise (f"Error: Parameters length ({parameters_length}) exceeds the maximum allowed length of"
              f" {ProtocolSettings.MAX_PARAMETER_LENGTH}.")

    # Construct the final message
    return f"{parameters_length}:{message_type}:{parameters_data.hex()}"


def parse_message(received_message):
    """
    Parses a received message following the protocol format and extracts components.

    :param received_message: The message string to parse.
    :return: Tuple containing (message_type, parameters) or None if format is invalid.
    """
    try:
        # Split the message by the protocol delimiter
        parameters_length, message_type, parameters_hex = received_message.split(":", 2)

        # Convert parameters length to integer
        parameters_length = int(parameters_length)

        # Decode the hex-encoded parameters back to bytes
        parameters_data = bytes.fromhex(parameters_hex)

        # Check if the received parameters length matches the actual length
        if parameters_length != len(parameters_data):
            print("Error: Parameters length mismatch.")
            return None

        # Deserialize the parameters using pickle
        parameters = pickle.loads(parameters_data)

        # Ensure parameters are in list format
        if not isinstance(parameters, list):
            print("Error: Parameters must be in list format.")
            return None

        return message_type, parameters

    except (ValueError, pickle.PickleError) as e:
        print(f"Error parsing message: {e}")
        return None





