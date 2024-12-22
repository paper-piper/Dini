from utils.config import PortSettings
from network.bootstrap import Bootstrap
from communication.port_manager import PortManager
from threading import Event


def run_bootstraps(servers_num, initial_peers=None):
    port_manager = PortManager(*PortSettings.BOOTSTRAP_RANGE)
    bootstraps = []
    for i in range(servers_num):
        bootstrap_server = Bootstrap(node_connections=initial_peers, port_manager=port_manager)
        # add the class to the list to avoid deletion.
        bootstraps.append(bootstrap_server)

    # Event to keep the script alive
    stop_event = Event()

    try:
        stop_event.wait()  # Keep the program running
    except KeyboardInterrupt:
        print("program shutting down...")

def run_bootstrap(port_manager):
    bootstrap = Bootstrap(port_manager=port_manager)
    stop_event = Event()
    stop_event.wait()
    other = bootstrap


