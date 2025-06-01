from network.user import User
from threading import Event
from core.transaction import get_sk_pk_pair
from core.wallet import create_sample_wallet
from utils.config import IPSettings

if __name__ == "__main__":

    # Use localhost for same-computer testing
    user_ip = IPSettings.LOCAL_IP

    sk, pk = get_sk_pk_pair()
    wallet = create_sample_wallet(pk, sk, f"{user_ip}-9091")
    # Initialize User
    user = User(
        pk,
        sk,
        ip=user_ip,
        port=9091,
        wallet=wallet,
        name="initiated_user"
    )
    # Keep the script running
    stop_event = Event()

    try:
        print("initiated user is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("Bootstrap2 shutting down...")
