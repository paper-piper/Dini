from threading import Lock
import time
from typing import Dict, Optional
from user_types import UserInstanceProtocol
import logging

logger = logging.getLogger(__name__)


class UserSessionManager:
    _instance = None
    _lock = Lock()
    
    def __init__(self):
        self.active_users: Dict[str, tuple[UserInstanceProtocol, float]] = {}
        self.cleanup_threshold = 300  # 5 minutes inactivity threshold
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def add_user(self, session_id: str, user_instance: UserInstanceProtocol):
        """Add or update a user session"""
        logger.info(f"Adding user session: {session_id}")
        self.active_users[session_id] = (user_instance, time.time())
    
    def get_user(self, session_id: str) -> Optional[UserInstanceProtocol]:
        """Get user instance and update last active time"""
        if session_id in self.active_users:
            user_instance, _ = self.active_users[session_id]
            self.active_users[session_id] = (user_instance, time.time())
            return user_instance
        return None
    
    def remove_user(self, session_id: str):
        """Remove user session"""
        if session_id in self.active_users:
            logger.info(f"Removing user session: {session_id}")
            user_instance, _ = self.active_users[session_id]
            user_instance.cleanup()  # Cleanup user resources
            del self.active_users[session_id]
    
    def cleanup_inactive_sessions(self):
        """Remove inactive sessions"""
        current_time = time.time()
        inactive_sessions = [
            session_id for session_id, (_, last_active) in self.active_users.items()
            if current_time - last_active > self.cleanup_threshold
        ]
        for session_id in inactive_sessions:
            logger.info(f"Cleaning up inactive session: {session_id}")
            self.remove_user(session_id)
    
    def get_all_active_users(self):
        """Get list of all active usernames"""
        return [user.username for user, _ in self.active_users.values()]