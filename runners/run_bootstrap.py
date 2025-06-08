from network.bootstrap import Bootstrap
from threading import Event


def run_bootstrap():
    print("Loading bootstrap...")
    bootstrap = Bootstrap()
    stop_event = Event()

    try:
        print("bootstrap is running!💚")
        stop_event.wait()
    except KeyboardInterrupt:
        print("bootstrap shutting down...")


if __name__ == "__main__":
    run_bootstrap()
