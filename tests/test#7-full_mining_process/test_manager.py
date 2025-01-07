import time
from network.bootstrap import Bootstrap
from network.miner.miner import Miner
from network.user import User
from threading import Event
from core.transaction import get_sk_pk_pair


if __name__ == "__main__":

    # Use localhost for same-computer testing
    ip = "127.0.0.1"
    bootstrap_port= 8001
    miner_port = 8000
    spending_user_port = 9000
    receiving_user_port = 9001
    spending_user_sk, spending_user_pk = get_sk_pk_pair()
    miner_sk, miner_pk = get_sk_pk_pair()
    receiving_user_sk, receiving_user_pk = get_sk_pk_pair()
    bootstrap = Bootstrap(ip=ip, port=bootstrap_port)
    spending_user = User(
        spending_user_pk,
        spending_user_sk,
        ip=ip,
        port=spending_user_port
    )
    miner = Miner(
        miner_pk,
        miner_sk,
        ip=ip,
        port=miner_port,
    )

    receiving_user = User(receiving_user_pk, receiving_user_sk, ip=ip, port=receiving_user_port)
    print(f"Finished loading! starting to cook 👨‍🍳")
    spending_user.add_transaction(receiving_user_pk, 100, 10)
    miner.start_mining(1)

    while receiving_user.wallet.balance == 0:
        time.sleep(1)

    print(f"Received transaction! {receiving_user.wallet.transactions}")
    # Keep the script running
    stop_event = Event()

    try:
        print("initiated miner is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("miner shutting down...")
