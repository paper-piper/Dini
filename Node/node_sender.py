# NodeSender.py
import socket
import time

from Protocol.protocol import send_message
from node import TestNode
from dini_Settings import ProtocolSettings

def main():
    # Create a TestNode instance for the sender
    sender_node = TestNode("Sender")

    # Connect to the receiver node
    receiver_host = "127.0.0.1"
    receiver_port = 8001  # Port for the receiver node to listen on
    sender_node.add_peer(receiver_host, receiver_port)

    # Send a test message to the receiver
    if (receiver_host, receiver_port) in sender_node.peer_connections:
        peer_socket = sender_node.peer_connections[(receiver_host, receiver_port)]
        send_message(peer_socket, ProtocolSettings.SEND_OBJECT, ProtocolSettings.PEER, "Test Command")
        print("Test command sent to receiver")
        time.sleep(3)


if __name__ == "__main__":
    main()
