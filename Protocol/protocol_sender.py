import socket
from Protocol.protocol import send_message
from Blockchain.transaction import create_sample_transaction
from dini_settings import MsgTypes, MsgSubTypes
from logging_utils import setup_logger

# Setup logger for sender file
logger = setup_logger("protocol_sender")


def main():
    """
    Creates a test Transaction and sends it to the receiver.
    Connects to localhost, constructs a SEND message with TRANSACTION subtype, and sends it.
    :return: None
    """
    try:
        # Initialize a test Transaction object
        transaction = create_sample_transaction(100)

        # Connect to the receiver on localhost
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('127.0.0.1', 65432))  # Port 65432 for local testing
            send_message(sock, MsgTypes.SEND_OBJECT, MsgSubTypes.TRANSACTION, transaction, "Pass")
            logger.info("Transaction message sent successfully!")

    except (OSError, ConnectionError) as e:
        logger.error(f"Failed to send transaction message: {e}")
        raise


if __name__ == "__main__":
    main()
