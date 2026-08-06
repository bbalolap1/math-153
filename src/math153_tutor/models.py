from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class DifficultyLayer(str, Enum):
    FOUNDATION = "L0"
    DIRECT = "L1"
    GUIDED = "L2"
    REPRESENTATION = "L3"
    MIXED = "L4"
    PROFESSOR = "L5"
    TIMED = "L6"
    CUMULATIVE = "L7"


class ErrorCategory(str, Enum):
    RECOGNITION = "recognition_error"
    REPRESENTATION = "representation_error"
    FIRST_STEP = "first_step_error"
    PREREQUISITE = "prerequisite_gap"
    ALGEBRA = "algebra_execution_error"
    SIGN = "sign_error"
    DOMAIN = "domain_error"
    EXTRANEOUS = "extraneous_solution_error"
    ENDPOINT = "endpoint_error"
    FORMULA = "formula_selection_error"
    ANSWER_FORMAT = "answer_format_error"
    CALCULATOR = "calculator_entry_error"
    TIME = "time_management_error"


class SourceRef(BaseModel):
    source_id: str
    page: int | None = None
    question_number: str | None = None
    role: Literal["lecture", "question", "solution", "review", "image"]


class QuestionFamily(BaseModel):
    family_id: str
    title: str
    chapter: int
    section: str
    status: str = "draft"
    source_refs: list[str] = Field(default_factory=list)
    purpose: str
    professor_surface_construction: str
    underlying_mathematical_structure: str
    recognition_clues: str
    first_decision: str
    decision_path: str
    restrictions_and_required_checks: str = ""
    common_errors: str = ""
    mastery_rule: str = ""


class Attempt(BaseModel):
    question_id: str
    family_id: str
    layer: DifficultyLayer
    correct: bool
    recognition_correct: bool | None = None
    first_decision_correct: bool | None = None
    critical_check_correct: bool | None = None
    error_categories: list[ErrorCategory] = Field(default_factory=list)
    hints_used: int = 0
    duration_seconds: int = Field(ge=0)
