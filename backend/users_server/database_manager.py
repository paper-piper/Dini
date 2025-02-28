import sqlite3
from flask import g
from utils.logging_utils import setup_basic_logger

logger = setup_basic_logger()
DATABASE = 'users.db'


class DatabaseManager:
    """Handles all interactions with the SQLite database."""

    @staticmethod
    def get_db():
        """Opens a new database connection per request."""
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
            db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def init_db():
        """Creates the users table if it does not exist."""
        with DatabaseManager.get_db() as db:
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    pk TEXT,
                    sk TEXT,
                    session_id TEXT
                )
            ''')
            db.commit()
            logger.info("Database initialized successfully.")

    @staticmethod
    def close_connection(exception=None):
        """Closes the database connection at the end of each request."""
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    @staticmethod
    def execute_query(query, params=(), fetchone=False, fetchall=False):
        """Executes a database query safely and logs errors."""
        try:
            db = DatabaseManager.get_db()
            cursor = db.cursor()
            cursor.execute(query, params)
            db.commit()
            if fetchone:
                return cursor.fetchone()
            elif fetchall:
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return None
