from network.bootstrap import Bootstrap
from threading import Event
from utils.config import IPSettings

if __name__ == "__main__":

    # Use localhost for same-computer testing
    bootstrap_ip = IPSettings.LOCAL_IP

    # Initialize Bootstrap2 without peer_connections
    bootstrap2 = Bootstrap(
        port=9090,
        ip=bootstrap_ip,
        name="main_bootstrap"
    )
    print(f"tried to connect to peers, got the addresses:  {bootstrap2.node_connections}")
    # Keep the script running
    stop_event = Event()

    try:
        print("Bootstrap2 is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("Bootstrap2 shutting down...")
