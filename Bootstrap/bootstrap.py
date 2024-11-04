from Node.node import Node


class Bootstrap(Node):
    def handle_block_request(self):
        raise NotImplementedError("Bootstrap does not handle block requests")

    def handle_peer_request(self):
        # Implementation for Bootstrap
        print("Bootstrap handling peer request")

    def handle_block_send(self, params):
        raise NotImplementedError("Bootstrap does not handle block sending")

    def handle_peer_send(self, params):
        # Implementation for Bootstrap
        print("Bootstrap handling peer send")

    def handle_transaction_send(self, params):
        raise NotImplementedError("Bootstrap does not handle transactions")


