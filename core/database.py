"""
SQLite Database Layer for persisting history and favorites.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional


class LyricsDatabase:
    """Manages SQLite database for lyrics history and favorites."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file.
                     Defaults to 'lyrics_data.db' in the app directory.
        """
        if db_path is None:
            # Store database in the same directory as the script
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(app_dir, 'lyrics_data.db')

        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they don't exist."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    raw_content TEXT NOT NULL,
                    converted_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    raw_content TEXT NOT NULL,
                    converted_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
        finally:
            conn.close()

    # ──────────────────── History Operations ────────────────────

    def save_history(self, title: str, raw_content: str, converted_json: str) -> int:
        """
        Save a conversion to history. Limits to 100 entries (oldest deleted first).

        Returns:
            The ID of the newly inserted row.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Insert new entry
            cursor.execute(
                'INSERT INTO history (title, raw_content, converted_json) VALUES (?, ?, ?)',
                (title, raw_content, converted_json)
            )
            new_id = cursor.lastrowid

            # Enforce 100-entry limit by deleting oldest
            cursor.execute('''
                DELETE FROM history WHERE id NOT IN (
                    SELECT id FROM history ORDER BY created_at DESC LIMIT 100
                )
            ''')

            conn.commit()
            return new_id
        finally:
            conn.close()

    def get_history(self) -> list[dict]:
        """Get all history entries, newest first."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, title, raw_content, converted_json, created_at '
                'FROM history ORDER BY created_at DESC'
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete_history(self, entry_id: int):
        """Delete a history entry by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM history WHERE id = ?', (entry_id,))
            conn.commit()
        finally:
            conn.close()

    # ──────────────────── Favorites Operations ────────────────────

    def save_favorite(self, title: str, raw_content: str, converted_json: str) -> int:
        """
        Save a conversion to favorites.

        Returns:
            The ID of the newly inserted row.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO favorites (title, raw_content, converted_json) VALUES (?, ?, ?)',
                (title, raw_content, converted_json)
            )
            new_id = cursor.lastrowid
            conn.commit()
            return new_id
        finally:
            conn.close()

    def get_favorites(self) -> list[dict]:
        """Get all favorite entries, newest first."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, title, raw_content, converted_json, created_at '
                'FROM favorites ORDER BY created_at DESC'
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete_favorite(self, entry_id: int):
        """Delete a favorite entry by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM favorites WHERE id = ?', (entry_id,))
            conn.commit()
        finally:
            conn.close()

    # ──────────────────── Shared Operations ────────────────────

    def load_entry(self, table: str, entry_id: int) -> Optional[dict]:
        """
        Load a single entry from history or favorites.

        Args:
            table: 'history' or 'favorites'
            entry_id: The entry ID

        Returns:
            Dict with entry data, or None if not found.
        """
        if table not in ('history', 'favorites'):
            raise ValueError(f"Invalid table: {table}")

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f'SELECT id, title, raw_content, converted_json, created_at '
                f'FROM {table} WHERE id = ?',
                (entry_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def update_title(self, table: str, entry_id: int, new_title: str):
        """Rename an entry in history or favorites."""
        if table not in ('history', 'favorites'):
            raise ValueError(f"Invalid table: {table}")

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f'UPDATE {table} SET title = ? WHERE id = ?',
                (new_title, entry_id)
            )
            conn.commit()
        finally:
            conn.close()

    def update_converted_json(self, table: str, entry_id: int, converted_json: str):
        """Update the converted JSON for an entry (e.g., after polyphonic correction)."""
        if table not in ('history', 'favorites'):
            raise ValueError(f"Invalid table: {table}")

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f'UPDATE {table} SET converted_json = ? WHERE id = ?',
                (converted_json, entry_id)
            )
            conn.commit()
        finally:
            conn.close()
