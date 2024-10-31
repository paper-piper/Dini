import socket
from Protocol.protocol import receive_message
from dini_Settings import ProtocolSettings
from logging_utils import setup_logger

# Setup logger for receiver file
logger = setup_logger("receiver_module", "..\\..\\Logs\\")


def main():
    """
    Sets up a socket to listen for incoming messages on localhost and processes received messages.
    Connects to the sender, receives a message, and logs message type and parameters.
    :return: None
    """
    try:
        # Set up a socket to listen for connections on localhost
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('127.0.0.1', 65432))  # Port 65432 for local testing
            sock.listen(1)
            logger.info("Receiver is ready and waiting for connection...")

            # Accept the incoming connection
            conn, addr = sock.accept()
            with conn:
                logger.info(f"Connected by {addr}")

                # Receive and process the message
                msg_type, msg_sub_type, params = receive_message(conn)
                logger.info(f"Received message type: {msg_type}")
                logger.info(f"Received message sub-type: {msg_sub_type}")
                logger.info(f"Received parameters: {params}")

    except (OSError, ConnectionError) as e:
        logger.error(f"Failed to receive message: {e}")
        raise


if __name__ == "__main__":
    logger.info("hallo")
    #main()
