from datetime import datetime

from utils.config import TransactionSettings


class TransactionWrapper:
    """
    Wraps a Transaction object with extra metadata needed by the Wallet.
    """
    def __init__(self, transaction, status, created_at=None):
        """
        :param transaction: The original Transaction object
        :param status: "pending", "approved", or "failed"
        :param created_at: datetime when this wrapper was created
        """
        self.transaction = transaction
        # Use the first few chars of signature as an ID (if signature exists)
        sig = transaction.signature or ""
        self.id = sig[:TransactionSettings.ID_LENGTH] if len(sig) >= TransactionSettings.ID_LENGTH else sig

        self.created_at = created_at or datetime.now()
        self.status = status

    def __repr__(self):
        return (f"<TransactionWrapper id={self.id} status={self.status} "
                f"tx=({self.transaction})>")

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "transaction": self.transaction.to_dict(),
        }

    @classmethod
    def from_dict(cls, data, transaction_class):
        tx = transaction_class.from_dict(data["transaction"])
        created_at = datetime.fromisoformat(data["created_at"])
        return cls(tx, data["status"], created_at)
