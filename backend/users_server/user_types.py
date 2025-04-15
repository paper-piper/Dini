from typing import Protocol, Optional
from datetime import datetime

class UserInstanceProtocol(Protocol):
    """Protocol defining the interface for user instances"""
    def get_recent_transactions(self, limit: int) -> list:
        ...
    
    def buy_dinis(self, amount: float) -> str:
        ...
    
    def sell_dinis(self, amount: float) -> str:
        ...
    
    def add_transaction(self, details: str, amount: float) -> str:
        ...
    
    def cleanup(self) -> None:
        ...
    
    @property
    def nodes_names_addresses(self) -> dict:
        ... 