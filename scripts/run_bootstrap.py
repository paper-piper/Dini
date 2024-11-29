from utils.logging_utils import setup_logger
from utils.config import PortSettings
from network.bootstrap import Bootstrap
from communication.port_manager import PortManager
from threading import Event
logger = setup_logger("bootstrap manager")


def run_bootstraps(servers_num, initial_peers=None):
    port_manager = PortManager(*PortSettings.BOOTSTRAP_RANGE)
    bootstraps = []
    stop_event = Event()
    for i in range(servers_num):
        bootstrap_server = Bootstrap(peer_connections=initial_peers, port_manager=port_manager)
        # add the class to the list to avoid deletion.
        bootstraps.append(bootstrap_server)

    stop_event.wait()
