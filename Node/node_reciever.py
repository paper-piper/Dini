# NodeReceiver.py
import socket
import threading
import time

from node import TestNode


def handle_connection(node, conn):
    """
    Handle incoming messages from the sender node.
    """
    node.receive_messages(conn)


def main():
    # Create a TestNode instance for the receiver
    receiver_node = TestNode("Receiver")

    # Start a server socket to listen for connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_host = "127.0.0.1"
    server_port = 8001
    server_socket.bind((server_host, server_port))
    server_socket.listen(1)
    print(f"Receiver node listening on {server_host}:{server_port}")

    # Accept a connection from the sender node
    conn, _ = server_socket.accept()
    print("Connected to sender")

    # Add the connection to peer connections and start a thread to handle it
    receiver_node.peer_connections[("127.0.0.1", 8000)] = conn
    threading.Thread(target=handle_connection, args=(receiver_node, conn)).start()


if __name__ == "__main__":
    main()
