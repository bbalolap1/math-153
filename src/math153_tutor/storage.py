from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Attempt


class AttemptRepository:
    """Local SQLite persistence for learner attempts."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY, problem_id TEXT, family_id TEXT, created_at TEXT,
                correct INTEGER, recognition_correct INTEGER, first_decision_correct INTEGER,
                payload TEXT NOT NULL)"""
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def add(self, attempt: Attempt) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO attempts (problem_id, family_id, created_at, correct, "
                "recognition_correct, first_decision_correct, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (attempt.problem_id, attempt.family_id, attempt.created_at.isoformat(), attempt.correct,
                 attempt.recognition_correct, attempt.first_decision_correct,
                 json.dumps(attempt.model_dump(mode="json"))),
            )

    def list(self, family_id: str | None = None) -> list[Attempt]:
        query: str = "SELECT payload FROM attempts"
        parameters: tuple[str, ...] = ()
        if family_id:
            query, parameters = query + " WHERE family_id = ?", (family_id,)
        with self._connect() as connection:
            return [Attempt.model_validate_json(row[0]) for row in connection.execute(query, parameters)]
