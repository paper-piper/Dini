from utils.logging_utils import clean_logs
# clean logs before creaing new ones using the imports
clean_logs()
import time
from network.bootstrap import Bootstrap
from network.user import User
from core.transaction import get_sk_pk_pair

if __name__ == "__main__":

    # Use localhost for same-computer testing
    ip = "127.0.0.1"
    bootstrap_port = 8001
    spending_user_port = 9000
    receiving_user_port = 8002
    spending_user_sk, spending_user_pk = get_sk_pk_pair()
    receiving_user_sk, receiving_user_pk = get_sk_pk_pair()
    print("Loading bootstrap...")
    bootstrap = Bootstrap(ip=ip, port=bootstrap_port, name="connecting_bootstrap")
    print("Loading spending user...")
    spending_user = User(
        spending_user_pk,
        spending_user_sk,
        ip=ip,
        port=spending_user_port,
        name="spending_user_(kobi)"
    )
    print("Loading receiving user...")
    receiving_user = User(
        receiving_user_pk,
        receiving_user_sk,
        ip=ip,
        port=receiving_user_port,
        name="receiving_user_(roni)"
    )
    print(f"Finished loading! starting to cook 👨‍🍳")

    while len(spending_user.nodes_names_addresses) == 0:
        time.sleep(1)

    print(f"Connected to name! {spending_user.nodes_names_addresses}")
