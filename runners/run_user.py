from network.user import User
from threading import Event
from core.transaction import get_sk_pk_pair

USERNAME = "john"


def run_user():
    user_sk, user_pk = get_sk_pk_pair()
    print("Loading mining miner...")
    user = User(
        user_pk,
        user_sk,
        name=USERNAME
    )
    # Keep the script running
    stop_event = Event()

    try:
        print("user is running!💚")
        stop_event.wait()
    except KeyboardInterrupt:
        print("user shutting down...")


if __name__ == "__main__":
    run_user()
