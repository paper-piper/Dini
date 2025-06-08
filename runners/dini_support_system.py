from network.bootstrap import Bootstrap
from network.miner.miner import Miner
from threading import Event
from core.transaction import get_sk_pk_pair


def run_support_system():
    miner_sk, miner_pk = get_sk_pk_pair()
    print("Loading bootstrap...")
    bootstrap = Bootstrap(port=8001)
    print("Loading mining miner...")
    miner = Miner(
        miner_pk,
        miner_sk,
        name="Bob The Miner",
        port=8002
    )
    miner.start_mining(-1)
    # Keep the script running
    stop_event = Event()

    try:
        print("support system is running!💚")
        stop_event.wait()
    except KeyboardInterrupt:
        print("support system shutting down...")


if __name__ == "__main__":
    run_support_system()
