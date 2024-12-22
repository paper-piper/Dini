from network.miner.miner import Miner
from threading import Event
from core.transaction import get_sk_pk_pair


if __name__ == "__main__":

    # Use localhost for same-computer testing
    miner_ip = "127.0.0.1"
    sk, pk = get_sk_pk_pair()
    # Initialize Bootstrap1 with peer_connections
    miner = Miner(
        pk,
        sk,
        ip=miner_ip,
        port=8001,
    )
    # Keep the script running
    stop_event = Event()

    try:
        print("initiated miner is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("miner shutting down...")
