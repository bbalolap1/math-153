from __future__ import annotations

from enum import Enum
from datetime import UTC, datetime
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
    hidden_prerequisites: str
    difficulty_ladder: dict[DifficultyLayer, str]
    expected_answer_presentation: str
    restrictions_and_required_checks: str = ""
    common_errors: str = ""
    mastery_rule: str = ""


class Attempt(BaseModel):
    problem_id: str
    family_id: str
    layer: DifficultyLayer
    correct: bool
    recognition_correct: bool | None = None
    first_decision_correct: bool | None = None
    critical_check_correct: bool | None = None
    error_categories: list[ErrorCategory] = Field(default_factory=list)
    hints_used: int = 0
    duration_seconds: int = Field(ge=0)
    mode: Literal["handwritten", "professor", "assessment"] = "handwritten"
    recognition_answer: str | None = None
    first_decision_answer: str | None = None
    final_answer: str
    confidence: int | None = Field(default=None, ge=1, le=5)
    self_reported_error: ErrorCategory | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GeneratedProblem(BaseModel):
    """A deterministic runtime problem produced by a reviewed template."""

    problem_id: str
    family_id: str
    construction_id: str
    difficulty_layer: DifficultyLayer
    prompt: str
    expected_answer: str
    validator: Literal["numeric", "exact_numeric", "expression", "solution_set"]
    recognition_options: list[str]
    correct_recognition: str
    first_decision_options: list[str]
    correct_first_decision: str
    source_refs: list[str]
    source_construction_refs: list[str]
    source_concept_refs: list[str]
    generation_method: Literal["controlled_template"] = "controlled_template"
    parameter_seed: int
    required_skills: list[str]
    variant_reason: str
    reasoning_checkpoints: list[str]
    exact_form_required: bool = False
    critical_checks: list[str] = Field(default_factory=list)
    targeted_feedback: dict[ErrorCategory, str] = Field(default_factory=dict)


class WorkedSolution(BaseModel):
    """Learner-facing solution revealed only after an answer is submitted."""

    rule: str
    setup: str
    calculation: list[str]
    final_answer: str
    check: str
    inference: str = "Identify the requested mathematical structure."
    prerequisite: str = "Accurate arithmetic and algebraic notation."
    family_reason: str = "The prompt uses the defining operation of this family."


class PracticeProblem(BaseModel):
    """A selectable exam-review problem with validation and provenance."""

    problem_id: str
    group: str
    chapter: str
    section: str
    family_id: str
    family_title: str
    difficulty: Literal["direct", "standard", "professor", "mixed"]
    prompt: str
    answer_type: Literal[
        "integer", "decimal", "fraction", "expression", "equation", "ordered_pair",
        "ordered_pairs", "interval", "solution_set", "complex_number", "radical",
        "logarithmic_expression", "multiple_choice", "multi_select", "table", "domain",
        "range",
    ]
    expected_answer: str
    wrong_answer: str
    choices: list[str] = Field(default_factory=list)
    source_type: str
    source_file: str
    source_question_or_page: str
    construction_notes: str
    rule_or_formula: str
    required_skills: list[str]
    worked_solution: WorkedSolution
    parameter_seed: int


class PracticeAttempt(BaseModel):
    problem_id: str
    family_id: str
    answer: str
    correct: bool
    answer_type: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
