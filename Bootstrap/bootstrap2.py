from Bootstrap.bootstrap import Bootstrap
from threading import Event
from logging_utils import setup_logger

logger = setup_logger("bootstrap2")


if __name__ == "__main__":
    # Initialize Bootstrap2 without peer_connections
    bootstrap2 = Bootstrap(
        is_bootstrap=False,
        port=9090
    )


    # Keep the script running
    stop_event = Event()

    try:
        print("Bootstrap2 is running. Waiting for communication...")
        stop_event.wait()
    except KeyboardInterrupt:
        print("Bootstrap2 shutting down...")
