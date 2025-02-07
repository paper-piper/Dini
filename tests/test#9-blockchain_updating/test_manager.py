import time

from core.blockchain import create_sample_blockchain
from network.bootstrap import Bootstrap
from network.miner.miner import Miner
from network.user import User
from core.transaction import get_sk_pk_pair

if __name__ == "__main__":

    # Use localhost for same-computer testing
    ip = "127.0.0.1"
    bootstrap_port = 8001
    user_port = 8002
    user_sk, user_pk = get_sk_pk_pair()
    miner_sk, miner_pk = get_sk_pk_pair()

    print("Loading bootstrap...")
    bootstrap = Bootstrap(ip=ip, port=bootstrap_port, name="connecting_bootstrap")

    print("Loading mining miner...")
    miner = Miner(
        miner_pk,
        miner_sk,
        ip=ip,
        name="roni the miner",
        blockchain=create_sample_blockchain(recipient_pk=user_pk)
    )
    print("Loading receiving user...")
    user = User(
        user_pk,
        user_sk,
        ip=ip,
        port=user_port,
        name="receiving_user_(roni)"
    )

    print(f"Finished loading! starting to cook 👨‍🍳")
    print(f"User port: {user.port}. miner port: {miner.port}")

    while user.wallet.balance == 0:
        time.sleep(1)

    print(f"Recieved blockchain updates!")
