from threading import Event
from network.user import User
from core.transaction import get_sk_pk_pair


def run_user(port_manager):
    sk, pk = get_sk_pk_pair()
    user = User(pk, sk, port_manager=port_manager)

    stop_event = Event()

    try:
        stop_event.wait()  # Keep the program running
    except KeyboardInterrupt:
        print("program shutting down...")
