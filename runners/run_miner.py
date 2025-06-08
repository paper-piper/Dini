from network.bootstrap import Bootstrap
from network.miner.miner import Miner
from threading import Event
from core.transaction import get_sk_pk_pair

MINER_NAME = "koki"


def run_miner():
    miner_sk, miner_pk = get_sk_pk_pair()
    print("Loading mining miner...")
    miner = Miner(
        miner_pk,
        miner_sk,
        name=MINER_NAME
    )
    miner.start_mining(-1)
    # Keep the script running
    stop_event = Event()

    try:
        print("miner is running!💚")
        stop_event.wait()
    except KeyboardInterrupt:
        print("miner shutting down...")


if __name__ == "__main__":
    run_miner()
