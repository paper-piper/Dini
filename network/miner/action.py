from datetime import datetime


class Action:
    def __init__(self, action_id, action_type, amount, status, details=None, timestamp=None):
        self.id = action_id
        self.type = action_type
        self.amount = amount
        self.status = status
        self.timestamp = timestamp or datetime.now()
        self.details = details

    def __repr__(self):
        return (
            f"Action(id={self.id}, type={self.type}, amount={self.amount}, "
            f"status={self.status}, timestamp={self.timestamp}, details={self.details})"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "amount": self.amount,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details.to_dict() if self.details and hasattr(self.details, "to_dict") else self.details,
        }

    @classmethod
    def from_dict(cls, data):
        details = data.get("details")
        timestamp = datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None
        return cls(
            action_id=data["id"],
            action_type=data["type"],
            amount=data["amount"],
            status=data["status"],
            details=details,
            timestamp=timestamp
        )
