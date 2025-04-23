from network.bootstrap import Bootstrap
from network.miner.miner import Miner
from threading import Event
from core.transaction import get_sk_pk_pair


if __name__ == "__main__":

    # Use localhost for same-computer testing
    ip = "127.0.0.1"
    bootstrap_port = 8001
    miner_port = 8002
    miner_sk, miner_pk = get_sk_pk_pair()
    print("Loading bootstrap...")
    bootstrap = Bootstrap(ip=ip, port=bootstrap_port)
    print("Loading mining miner...")
    miner = Miner(
        miner_pk,
        miner_sk,
        ip=ip,
        port=miner_port,
        name="Bob The Miner"
    )
    miner.start_mining(-1)
    # Keep the script running
    stop_event = Event()

    try:
        print("user backend background is running!💚")
        stop_event.wait()
    except KeyboardInterrupt:
        print("miner shutting down...")
