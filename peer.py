import logging
import json
import os

class Peer:
    def __init__(self, blockchain, peer_type):
        self.blockchain = blockchain
        self.peer_type = peer_type
        self.peers = []  # List of connected peers
        self.logger = logging.getLogger(f"{peer_type}_peer")

    def save_blockchain(self, filename="blockchain.json"):
        """Saves the current blockchain to a file in JSON format."""
        with open(filename, "w") as f:
            json.dump(self.blockchain.to_dict(), f)
        self.logger.info("Blockchain saved to %s", filename)

    def load_blockchain(self, filename="blockchain.json"):
        """Loads the blockchain from a file if it exists."""
        if os.path.exists(filename):
            with open(filename, "r") as f:
                self.blockchain.from_dict(json.load(f))
            self.logger.info("Blockchain loaded from %s", filename)
        else:
            self.logger.warning("No blockchain file found to load.")

    def request_block(self, block_hash):
        """Request a specific block from other peers."""
        # Network request logic to be implemented
        self.logger.info("Requesting block with hash: %s", block_hash)

    def pass_block(self, block):
        """Pass the mined or received block to other peers."""
        # Network broadcast logic to be implemented
        self.logger.info("Broadcasting block with hash: %s", block.hash)

    def add_peer(self, peer_info):
        """Adds a new peer to the network list."""
        self.peers.append(peer_info)
        self.logger.info("New peer added: %s", peer_info)
