from network.user import User
from threading import Event
from core.transaction import get_sk_pk_pair
from utils.config import IPSettings

if __name__ == "__main__":

    # Use localhost for same-computer testing
    user_ip = IPSettings.LOCAL_IP

    sk, pk = get_sk_pk_pair()
    # Initialize User
    user = User(
        pk,
        sk,
        ip=user_ip,
        port=9092,
        name="connecting_user"
    )
    # Keep the script running
    stop_event = Event()

    try:
        print("Bootstrap2 is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("Bootstrap2 shutting down...")
