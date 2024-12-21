from network.miner.miner import Miner
from core.transaction import get_sk_pk_pair
from core.blockchain import create_sample_blockchain
from threading import Event


def run_miner(port_manager=None):
    # Generate key pair for the miner
    sk, pk = get_sk_pk_pair()
    miner = Miner(pk, sk, port_manager=port_manager, blockchain=create_sample_blockchain())

    stop_event = Event()

    try:
        stop_event.wait()  # Keep the program running
    except KeyboardInterrupt:
        print("program shutting down...")

    other = miner


if __name__ == "__main__":
    run_miner()
