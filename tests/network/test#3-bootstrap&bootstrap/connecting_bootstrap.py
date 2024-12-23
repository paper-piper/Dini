from network.bootstrap import Bootstrap
from threading import Event


if __name__ == "__main__":

    # Use localhost for same-computer testing
    bootstrap_ip = "127.0.0.1"

    # Initialize Bootstrap2 without peer_connections
    bootstrap2 = Bootstrap(
        is_bootstrap=False,
        port=9090,
        ip=bootstrap_ip
    )
    print(f"tried to connect to peers, got the addresses:  {bootstrap2.node_connections}")
    # Keep the script running
    stop_event = Event()

    try:
        print("Bootstrap2 is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("Bootstrap2 shutting down...")
