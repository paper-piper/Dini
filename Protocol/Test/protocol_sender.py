import socket
from Protocol.protocol import send_message
from dini_Settings import ProtocolSettings
from Blockchain.transaction import Transaction, get_sk_pk_pair
from logging_utils import setup_logger

logger = setup_logger("protocol_sender")


def main():
    # Create a socket to connect to the receiver on localhost
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('127.0.0.1', 65432))  # Use port 65432 (can be any free port)

        # create a sample transaction
        sk, pk = get_sk_pk_pair()
        _, receiver_pk = get_sk_pk_pair()
        transaction = Transaction(pk, receiver_pk, 100)
        # Send a test message
        test_type = ProtocolSettings.SEND_OBJECT
        test_params = [transaction, ProtocolSettings.DONT_PASS]
        send_message(sock, test_type, *test_params)
        logger.info(f"Message type: {test_type} \n\r message parameters: {test_params}")


if __name__ == "__main__":
    main()
