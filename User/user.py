from Bootstrap.bootstrap import Bootstrap


class User(Bootstrap):
    def handle_block_request(self):
        print("user handling peer request")

    def handle_block_send(self, params):
        print("user handling block send")

    def handle_transaction_send(self, params):
        raise NotImplementedError("user does not handle transactions")

