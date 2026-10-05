"""EAGLE - SQLite FTS5 full-text search for AETHER content."""
from __future__ import annotations
import sqlite3
from pathlib import Path

class Eagle:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._conn() as c:
            c.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS docs
                USING fts5(title, content, source UNINDEXED, tokenize='porter')
            """)

    def index(self, title, content, source=""):
        with self._conn() as c:
            c.execute("INSERT INTO docs(title, content, source) VALUES (?,?,?)",
                      (title, content, source))

    def search(self, query, limit=20):
        with self._conn() as c:
            cur = c.execute("""
                SELECT title, source, snippet(docs, 1, '[', ']', '...', 20)
                FROM docs WHERE docs MATCH ? ORDER BY rank LIMIT ?
            """, (query, limit))
            return [{"title": r[0], "source": r[1], "snippet": r[2]} for r in cur.fetchall()]

    def count(self):
        with self._conn() as c:
            return c.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
