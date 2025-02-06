import time
from network.bootstrap import Bootstrap
from network.miner.miner import Miner
from network.user import User
from core.transaction import get_sk_pk_pair


if __name__ == "__main__":

    # Use localhost for same-computer testing
    ip = "127.0.0.1"
    bootstrap_port = 8001
    spending_user_port = 9000
    spending_user_sk, spending_user_pk = get_sk_pk_pair()
    miner_sk, miner_pk = get_sk_pk_pair()
    print("Loading bootstrap...")
    bootstrap = Bootstrap(ip=ip, port=bootstrap_port, name="connecting_bootstrap")
    time.sleep(1)
    print("Loading spending user...")
    spending_user = User(
        spending_user_pk,
        spending_user_sk,
        ip=ip,
        port=spending_user_port,
        name="kobi the user"
    )
    time.sleep(1)
    print("Loading mining miner...")
    # don't specify miner port to avoid saved blockchains
    miner = Miner(
        miner_pk,
        miner_sk,
        ip=ip,
        name="roni the miner"
    )
    time.sleep(1)
    print(f"Finished loading! starting to cook 👨‍🍳")
    spending_user.buy_dinis(100)
    miner.start_mining(-1)

    print(f"Miner has {len(miner.blockchain.chain)} blocks (including genesys)")
    while spending_user.wallet.balance == 0:
        time.sleep(1)

    print(f"Received transaction! {spending_user.wallet.get_recent_transactions(-1)}")
    print(spending_user.nodes_names_addresses)
