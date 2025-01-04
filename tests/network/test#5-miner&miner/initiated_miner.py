from network.miner.miner import Miner
from threading import Event
from core.transaction import get_sk_pk_pair
from core.blockchain import create_sample_blockchain


if __name__ == "__main__":

    # Use localhost for same-computer testing
    miner_ip = "127.0.0.1"
    sk, pk = get_sk_pk_pair()
    # Initialize Bootstrap1 with peer_connections
    miner = Miner(
        pk,
        sk,
        ip=miner_ip,
        port=8000,
        blockchain=create_sample_blockchain()
    )

    print(miner.blockchain)

    # Keep the script running
    stop_event = Event()

    try:
        print("initiated miner is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("miner shutting down...")
