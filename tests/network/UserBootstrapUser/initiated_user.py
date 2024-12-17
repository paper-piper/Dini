from network.user import User
from threading import Event
from utils.logging_utils import setup_logger
from core.transaction import get_sk_pk_pair

logger = setup_logger()


if __name__ == "__main__":

    # Use localhost for same-computer testing
    user_ip = "127.0.0.1"

    sk, pk = get_sk_pk_pair()
    # Initialize User
    user = User(
        pk,
        sk,
        ip=user_ip,
        port=9091
    )
    # Keep the script running
    stop_event = Event()

    try:
        print("Bootstrap2 is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("Bootstrap2 shutting down...")
