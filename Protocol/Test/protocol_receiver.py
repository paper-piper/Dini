import socket
from Protocol.protocol import receive_message


def main():
    # Create a socket to listen for incoming connections on localhost
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 65432))  # Bind to the same port as the sender
        sock.listen(1)

        print("Receiver ready, waiting for a connection...")

        # Accept the incoming connection
        conn, addr = sock.accept()
        with conn:
            print(f"Connected by {addr}")
            # Receive and print the message
            msg_type, msg_params = receive_message(conn)
            print(f"Received message type: {msg_type}")
            print(f"Received message parameters: {msg_params}")


if __name__ == "__main__":
    main()
