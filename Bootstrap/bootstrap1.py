from Bootstrap.bootstrap import Bootstrap
from threading import Event
from logging_utils import setup_logger

logger = setup_logger("bootstrap1")

if __name__ == "__main__":
    # Define peer connections for Bootstrap1
    initial_peers = {
        ("127.0.0.1", 9090): None  # Sample peer to be shared with Bootstrap2
    }

    # Initialize Bootstrap1 with peer_connections
    bootstrap1 = Bootstrap(
        is_bootstrap=True,
        port=8080,
        peer_connections=initial_peers
    )

    # Keep the script running
    stop_event = Event()

    try:
        print("Bootstrap1 is running. Waiting for communication...")
        #stop_event.wait()
    except KeyboardInterrupt:
        print("Bootstrap1 shutting down...")
