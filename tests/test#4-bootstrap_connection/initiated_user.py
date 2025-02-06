from network.user import User
from threading import Event
from core.transaction import get_sk_pk_pair
from core.wallet import create_sample_wallet


if __name__ == "__main__":

    # Use localhost for same-computer testing
    user_ip = "127.0.0.1"

    sk, pk = get_sk_pk_pair()
    wallet = create_sample_wallet(pk, sk)
    # Initialize User
    user = User(
        pk,
        sk,
        ip=user_ip,
        port=9091,
        wallet=wallet
    )
    # Keep the script running
    stop_event = Event()

    try:
        print("initiated user is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("Bootstrap2 shutting down...")
