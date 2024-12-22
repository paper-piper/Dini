from network.bootstrap import Bootstrap
from threading import Event


if __name__ == "__main__":
    # Define peer connections for Bootstrap1
    initial_peers = {
        ("127.0.0.1", 9090): None  # Sample peer to be shared with Bootstrap2
    }

    # Use localhost for same-computer testing
    bootstrap_ip = "127.0.0.1"

    # Initialize Bootstrap1 with peer_connections
    bootstrap1 = Bootstrap(
        is_bootstrap=True,
        port=8080,
        node_connections=initial_peers,
        ip=bootstrap_ip,
    )
    # Keep the script running
    stop_event = Event()

    try:
        print("Initiated Bootstrap is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("Bootstrap1 shutting down...")
