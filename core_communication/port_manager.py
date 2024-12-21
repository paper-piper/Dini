import threading
from utils.logging_utils import setup_logger

# Setup logger for file
logger = setup_logger("port_manager")


class PortManager:
    """
    Manages the allocation and release of ports in a specified range to ensure no conflicts.
    """

    def __init__(self, start_port=5000, end_port=6000):
        """
        Initializes the Port Manager with a range of ports.

        :param start_port: The starting port number.
        :param end_port: The ending port number.
        """
        self.lock = threading.Lock()
        self.available_ports = set(range(start_port, end_port + 1))
        self.in_use_ports = set()
        logger.info(f"PortManager initialized with range {start_port}-{end_port}.")

    def allocate_port(self):
        """
        Allocates an available port.

        :return: A unique port number.
        :raises RuntimeError: If no ports are available.
        """
        try:
            with self.lock:
                if not self.available_ports:
                    raise RuntimeError("No available ports.")
                port = self.available_ports.pop()
                self.in_use_ports.add(port)
                logger.info(f"Allocated port {port}.")
                return port
        except RuntimeError as e:
            logger.error(f"Failed to allocate port: {e}")
            raise

    def release_port(self, port):
        """
        Releases a port back to the pool of available ports.

        :param port: The port number to release.
        :return: None
        """
        try:
            with self.lock:
                if port in self.in_use_ports:
                    self.in_use_ports.remove(port)
                    self.available_ports.add(port)
                    logger.info(f"Released port {port}.")
                else:
                    logger.warning(f"Attempted to release a port not in use: {port}.")
        except Exception as e:
            logger.error(f"Failed to release port {port}: {e}")
            raise


def assertion_check():
    """
    Function to test the PortManager class with assertions.

    :return: None
    """
    logger.info("Starting assertion tests for PortManager.")

    # Test initialization and basic functionality
    port_manager = PortManager(start_port=6000, end_port=6002)
    assert len(port_manager.available_ports) == 3, "Incorrect number of initial available ports."

    # Test allocate_port
    port1 = port_manager.allocate_port()
    assert port1 in range(6000, 6003), "Allocated port is out of range."
    assert port1 not in port_manager.available_ports, "Allocated port should not be in available ports."
    assert port1 in port_manager.in_use_ports, "Allocated port should be in in-use ports."

    # Test release_port
    port_manager.release_port(port1)
    assert port1 in port_manager.available_ports, "Released port should be back in available ports."
    assert port1 not in port_manager.in_use_ports, "Released port should not be in in-use ports."

    # Test allocate until no ports are available
    port1 = port_manager.allocate_port()
    port2 = port_manager.allocate_port()
    port3 = port_manager.allocate_port()
    assert len(port_manager.available_ports) == 0, "All ports should be allocated."

    # Test exception when no ports are available
    try:
        port_manager.allocate_port()
    except RuntimeError as e:
        assert str(e) == "No available ports.", "Incorrect exception message when no ports are available."

    # Release all ports
    port_manager.release_port(port1)
    port_manager.release_port(port2)
    port_manager.release_port(port3)
    assert len(port_manager.available_ports) == 3, "All ports should be available after release."

    logger.info("All assertion tests passed.")


if __name__ == "__main__":
    assertion_check()
