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
    blockchain_length = len(miner.blockchain.chain)
    miner.connect_to_node(("127.0.0.1", 8000))
    # try and update the blockchain

    while blockchain_length == len(miner.blockchain.chain):
        time.sleep(1)

    print("Got block!")
    # wait for response

