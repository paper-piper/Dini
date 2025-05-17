import sqlite3
from flask import g
from utils.logging_utils import setup_basic_logger
from utils.config import FilesSettings
logger = setup_basic_logger()


class DatabaseManager:
    """Handles all interactions with the SQLite database."""

    @staticmethod
    def get_db():
        """Opens a new database connection per request."""
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(FilesSettings.SERVER_DATABASE_FILENAME)
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
                    salt TEXT,
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
        """
        Executes a database query safely and logs errors.
        Returns the query result (if fetching) or True (if modifying data).
        """
        try:
            db = DatabaseManager.get_db()
            cursor = db.cursor()
            cursor.execute(query, params)

            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                db.commit()
                result = True  # ✅ Return True when INSERT/UPDATE/DELETE succeeds

            return result
        except sqlite3.Error as e:
            logger.error(f"Database error: {e} - Query: {query} - Params: {params}")
            return None  # ✅ Return None when an error occurs
