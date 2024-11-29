from utils.logging_utils import setup_logger
from network.miner.miner import Miner
from core.transaction import get_sk_pk_pair
from utils.config import PortSettings
from network.bootstrap import Bootstrap
from communication.port_manager import PortManager
from threading import Event

logger = setup_logger("miner manager")


def run_miner():
    # Generate key pair for the miner
    sk, pk = get_sk_pk_pair()
    miner = Miner(pk, sk)
    logger.info("Miner initialized and ready.")

    print("Miner Manager CLI")
    print("Available commands:")
    print("1. mine blocks <how many>")
    print("2. make transaction <to who> <amount>")
    print("3. buy coins <amount>")
    print("4. sell coins <amount>")
    print("5. exit")

    while True:
        # Get user input
        command = input("\nEnter command: ").strip()
        args = command.split()

        if not args:
            print("No command entered. Please try again.")
            continue

        # Parse the command
        action = args[0].lower()

        # Handle commands
        if action == "mine":
            if len(args) == 3 and args[1] == "blocks":
                try:
                    count = int(args[2])
                    logger.info(f"Starting to mine {count} block(s).")
                    miner.start_mining(count)  # Assuming the Miner class has a `mine_block` method
                    print(f"Successfully mined {count} block(s).")
                except ValueError:
                    print("Invalid number of blocks. Please provide a valid integer.")
            else:
                print("Usage: mine blocks <how many>")

        elif action == "make":
            if len(args) == 4 and args[1] == "transaction":
                to_address = args[2]
                try:
                    amount = float(args[3])
                    logger.info(f"Making transaction: To={to_address}, Amount={amount}")
                    transaction = miner.make_transaction(to_address, amount)  # Assuming `create_transaction` exists
                    print(f"Transaction created: {transaction}")
                except ValueError:
                    print("Invalid amount. Please provide a valid number.")
            else:
                print("Usage: make transaction <to who> <amount>")

        elif action == "buy":
            if len(args) == 3 and args[1] == "coins":
                try:
                    amount = float(args[2])
                    logger.info(f"Buying coins: Amount={amount}")
                    miner.buy_dinis(amount)  # Assuming `buy_coins` exists in the Miner class
                    print(f"Successfully bought {amount} coins.")
                except ValueError:
                    print("Invalid amount. Please provide a valid number.")
            else:
                print("Usage: buy coins <amount>")

        elif action == "sell":
            if len(args) == 3 and args[1] == "coins":
                try:
                    amount = float(args[2])
                    logger.info(f"Selling coins: Amount={amount}")
                    miner.sell_dinis(amount)  # Assuming `sell_coins` exists in the Miner class
                    print(f"Successfully sold {amount} coins.")
                except ValueError:
                    print("Invalid amount. Please provide a valid number.")
            else:
                print("Usage: sell coins <amount>")

        elif action == "exit":
            logger.info("Shutting down the miner.")
            print("Exiting Miner Manager CLI. Goodbye!")
            break

        else:
            print("Unknown command. Please try again.")


if __name__ == "__main__":
    run_miner()
