import socket
from communication.protocol import send_protocol_message
from core.transaction import create_sample_transaction
from utils.config import MsgTypes, MsgSubTypes
from utils.logging_utils import setup_logger

# Setup logger for sender file
logger = setup_logger()


def main():
    """
    Creates a test Transaction and sends it to the receiver.
    Connects to localhost, constructs a SEND message with TRANSACTION subtype, and sends it.
    :return: None
    """
    try:

        # Connect to the receiver on localhost
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('127.0.0.1', 8080))  # Port 65432 for local testing
            send_protocol_message(
                sock,
                MsgTypes.RESPONSE,
                MsgSubTypes.TRANSACTION,
                create_sample_transaction(10),
                "My friend"
            )
            logger.info("Transaction message sent successfully!")

    except (OSError, ConnectionError) as e:
        logger.error(f"Failed to send transaction message: {e}")
        raise


if __name__ == "__main__":
    main()
