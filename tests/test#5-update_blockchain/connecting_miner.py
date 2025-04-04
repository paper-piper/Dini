import time

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
    miner.connect_to_node(("127.0.0.1", 8000))
    # try and update the blockchain
    miner.request_blockchain_update()

    # wait for response
    while len(miner.blockchain.chain) == 1:
        print("waiting for block update...")
        time.sleep(2)

    print(miner.blockchain)
    # Keep the script running
    stop_event = Event()

    try:
        print("initiated miner is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("miner shutting down...")
