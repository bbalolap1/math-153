from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import AssessmentRecord, Attempt, PracticeAttempt, RepairRecord


class _SQLiteRepo:
    def __init__(self,path:str|Path)->None:
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def _connect(self):
        connection=sqlite3.connect(self.path)
        connection.execute("PRAGMA journal_mode=WAL")
        return connection


class AttemptRepository(_SQLiteRepo):
    """Recognition/procedure attempts, stored as full version-tolerant JSON payloads."""
    def __init__(self,path:str|Path)->None:
        super().__init__(path)
        with self._connect() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY, problem_id TEXT, family_id TEXT, created_at TEXT,
                correct INTEGER, recognition_correct INTEGER, first_decision_correct INTEGER,
                payload TEXT NOT NULL)""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_attempt_family ON attempts(family_id)")
    def add(self,attempt:Attempt)->None:
        with self._connect() as c:
            c.execute(
                "INSERT INTO attempts (problem_id,family_id,created_at,correct,recognition_correct,first_decision_correct,payload) VALUES (?,?,?,?,?,?,?)",
                (attempt.problem_id,attempt.family_id,attempt.created_at.isoformat(),int(attempt.correct),
                 None if attempt.recognition_correct is None else int(attempt.recognition_correct),
                 None if attempt.first_decision_correct is None else int(attempt.first_decision_correct),
                 json.dumps(attempt.model_dump(mode="json"))),
            )
    def list(self,family_id:str|None=None)->list[Attempt]:
        q="SELECT payload FROM attempts"; params=()
        if family_id: q+=" WHERE family_id=?"; params=(family_id,)
        q+=" ORDER BY id"
        with self._connect() as c:
            return [Attempt.model_validate_json(row[0]) for row in c.execute(q,params)]


class PracticeAttemptRepository(_SQLiteRepo):
    """Professor-mode practice including the learner's written work."""
    def __init__(self,path:str|Path)->None:
        super().__init__(path)
        with self._connect() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS practice_attempts (
                id INTEGER PRIMARY KEY, family_id TEXT, correct INTEGER, payload TEXT NOT NULL)""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_practice_family ON practice_attempts(family_id)")
    def add(self,attempt:PracticeAttempt)->None:
        with self._connect() as c:
            c.execute("INSERT INTO practice_attempts (family_id,correct,payload) VALUES (?,?,?)",
                      (attempt.family_id,int(attempt.correct),json.dumps(attempt.model_dump(mode="json"))))
    def list(self,family_id:str|None=None)->list[PracticeAttempt]:
        q="SELECT payload FROM practice_attempts"; params=()
        if family_id: q+=" WHERE family_id=?"; params=(family_id,)
        q+=" ORDER BY id"
        with self._connect() as c:
            return [PracticeAttempt.model_validate_json(row[0]) for row in c.execute(q,params)]


class LearningRecordRepository(_SQLiteRepo):
    """Completed Quiz/Test/Exam records and repair records."""
    def __init__(self,path:str|Path)->None:
        super().__init__(path)
        with self._connect() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS assessments (
                assessment_id TEXT PRIMARY KEY, completed_at TEXT, assessment_type TEXT, payload TEXT NOT NULL)""")
            # migrate databases created by the prior shell
            cols={r[1] for r in c.execute("PRAGMA table_info(assessments)")}
            if "assessment_type" not in cols:
                c.execute("ALTER TABLE assessments ADD COLUMN assessment_type TEXT DEFAULT ''")
            c.execute("""CREATE TABLE IF NOT EXISTS repairs (
                id INTEGER PRIMARY KEY, assessment_id TEXT, problem_id TEXT, payload TEXT NOT NULL)""")
    def add_assessment(self,record:AssessmentRecord)->None:
        with self._connect() as c:
            c.execute(
                "INSERT OR REPLACE INTO assessments (assessment_id,completed_at,assessment_type,payload) VALUES (?,?,?,?)",
                (record.assessment_id,record.completed_at.isoformat(),record.assessment_type,
                 json.dumps(record.model_dump(mode="json"))),
            )
    def list_assessments(self,assessment_type:str|None=None)->list[AssessmentRecord]:
        q="SELECT payload FROM assessments"; params=()
        if assessment_type: q+=" WHERE assessment_type=?"; params=(assessment_type,)
        q+=" ORDER BY completed_at DESC"
        with self._connect() as c:
            return [AssessmentRecord.model_validate_json(row[0]) for row in c.execute(q,params)]
    def get_assessment(self,assessment_id:str)->AssessmentRecord|None:
        with self._connect() as c:
            row=c.execute("SELECT payload FROM assessments WHERE assessment_id=?",(assessment_id,)).fetchone()
        return AssessmentRecord.model_validate_json(row[0]) if row else None
    def add_repair(self,record:RepairRecord)->None:
        with self._connect() as c:
            c.execute("INSERT INTO repairs (assessment_id,problem_id,payload) VALUES (?,?,?)",
                      (record.assessment_id,record.problem_id,json.dumps(record.model_dump(mode="json"))))
    def list_repairs(self)->list[RepairRecord]:
        with self._connect() as c:
            return [RepairRecord.model_validate_json(r[0]) for r in c.execute("SELECT payload FROM repairs ORDER BY id DESC")]
