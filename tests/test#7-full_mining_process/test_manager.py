import time
from network.bootstrap import Bootstrap
from network.miner.miner import Miner
from network.user import User
from threading import Event
from core.transaction import get_sk_pk_pair


if __name__ == "__main__":

    # Use localhost for same-computer testing
    ip = "127.0.0.1"
    bootstrap_port = 8001
    miner_port = 8000
    spending_user_port = 9000
    receiving_user_port = 9001
    spending_user_sk, spending_user_pk = get_sk_pk_pair()
    miner_sk, miner_pk = get_sk_pk_pair()
    receiving_user_sk, receiving_user_pk = get_sk_pk_pair()
    print("Loading bootstrap...")
    bootstrap = Bootstrap(ip=ip, port=bootstrap_port)
    print("Loading spending user...")
    spending_user = User(
        spending_user_pk,
        spending_user_sk,
        ip=ip,
        port=spending_user_port
    )
    print("Loading mining miner...")
    miner = Miner(
        miner_pk,
        miner_sk,
        ip=ip,
        port=miner_port,
    )
    print("Loading receiving user...")
    print(f"Finished loading! starting to cook 👨‍🍳")
    spending_user.add_transaction(receiving_user_pk, 100, 10)
    miner.start_mining(-1)

    while spending_user.wallet.balance == 0:
        time.sleep(1)

    print(f"Received transaction! {spending_user.wallet.get_recent_transactions(-1)}")
