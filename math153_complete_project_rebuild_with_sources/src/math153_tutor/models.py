from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class DifficultyLayer(str, Enum):
    """Cognitive/assessment demand, not a cosmetic difficulty label."""
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
    locator: str | None = None
    role: Literal[
        "lecture", "question", "solution", "review", "image", "activity",
        "quiz", "test", "final", "supplement",
    ]


class QuestionFamily(BaseModel):
    """Markdown-loaded family specification retained for authored family files."""
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
    professor_traps: str
    professor_style_templates: str
    mastery_rule: str = ""


class ComplexityEvidence(BaseModel):
    """Observable reasons a problem is difficult or structurally novel."""
    numeric_variation: int = Field(default=0, ge=0, le=3)
    wording_variation: int = Field(default=0, ge=0, le=3)
    representation_shift: int = Field(default=0, ge=0, le=3)
    prerequisite_depth: int = Field(default=1, ge=1)
    decision_points: int = Field(default=1, ge=1)
    reasoning_steps: int = Field(default=1, ge=1)
    concept_count: int = Field(default=1, ge=1)
    method_count: int = Field(default=1, ge=1)
    verification_burden: int = Field(default=0, ge=0, le=3)
    interpretation_burden: int = Field(default=0, ge=0, le=3)
    time_pressure: int = Field(default=0, ge=0, le=3)
    source_style_distance: int = Field(
        default=0, ge=0, le=3,
        description="0 means source-faithful surface grammar; higher means intentionally farther transfer.",
    )

    @property
    def structural_score(self) -> int:
        return (
            self.wording_variation
            + 2 * self.representation_shift
            + self.prerequisite_depth
            + 2 * self.decision_points
            + self.reasoning_steps
            + self.concept_count
            + 2 * self.method_count
            + self.verification_burden
            + self.interpretation_burden
            + self.time_pressure
        )


class ProfessorGrammar(BaseModel):
    """Features extracted from source questions that generation should preserve."""
    instructional_verbs: list[str] = Field(default_factory=list)
    answer_forms: list[str] = Field(default_factory=list)
    hidden_requirements: list[str] = Field(default_factory=list)
    surface_patterns: list[str] = Field(default_factory=list)
    allowed_variations: list[str] = Field(default_factory=list)
    invariants: list[str] = Field(default_factory=list)
    source_examples: list[str] = Field(default_factory=list)


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
    generation_method: Literal["controlled_template", "source_exemplar"] = "controlled_template"
    parameter_seed: int
    required_skills: list[str]
    variant_reason: str
    reasoning_checkpoints: list[str]
    exact_form_required: bool = False
    critical_checks: list[str] = Field(default_factory=list)
    targeted_feedback: dict[ErrorCategory, str] = Field(default_factory=dict)
    structural_signature: str = ""
    complexity_evidence: ComplexityEvidence = Field(default_factory=ComplexityEvidence)


class WorkedSolution(BaseModel):
    rule: str
    setup: str
    calculation: list[str]
    final_answer: str
    check: str
    inference: str = "Identify the requested mathematical structure."
    prerequisite: str = "Accurate arithmetic and algebraic notation."
    family_reason: str = "The required operation defines this problem family."


class ExecutionStep(BaseModel):
    step_title: str
    before_expression: str
    operation: str
    why: str
    after_expression: str


class TeachingSolution(BaseModel):
    recognize: str
    decide: str
    original_rule_or_formula: str
    execute: list[ExecutionStep]
    verify: str
    final_answer: str
    quality_status: Literal["detailed", "insufficient_step_detail"] = "detailed"


AnswerType = Literal[
    "integer", "decimal", "fraction", "expression", "equation", "ordered_pair",
    "ordered_pairs", "interval", "solution_set", "complex_number", "radical",
    "logarithmic_expression", "multiple_choice", "multi_select", "table", "domain",
    "range", "text",
]


class PracticeProblem(BaseModel):
    """Source-grounded runtime problem with explicit structural metadata."""
    problem_id: str
    group: str
    chapter: str
    section: str
    family_id: str
    family_title: str
    difficulty: Literal["direct", "standard", "professor", "mixed"]
    prompt: str
    answer_type: AnswerType
    expected_answer: str
    wrong_answer: str = ""
    choices: list[str] = Field(default_factory=list)
    source_type: str
    source_file: str
    source_question_or_page: str
    construction_notes: str
    rule_or_formula: str
    required_skills: list[str]
    worked_solution: WorkedSolution
    parameter_seed: int
    difficulty_layer: DifficultyLayer
    representation: Literal[
        "symbolic", "context", "table", "graph", "classification", "verbal", "multipart"
    ]
    source_refs: list[str]
    variant_reason: str
    reasoning_checkpoints: list[str]
    complexity_level: DifficultyLayer
    decision_count: int = Field(ge=1)
    prerequisite_count: int = Field(ge=1)
    estimated_solution_steps: int = Field(ge=1)
    representation_type: str
    structural_variant_type: str
    structural_signature: str
    application_context: str = "none"
    requires_domain_check: bool = False
    requires_extraneous_check: bool = False
    requires_factoring: bool = False
    requires_graph: bool = False
    requires_interpretation: bool = False
    requires_multiple_methods: bool = False
    professor_grammar: ProfessorGrammar = Field(default_factory=ProfessorGrammar)
    complexity_evidence: ComplexityEvidence = Field(default_factory=ComplexityEvidence)
    source_exemplar_id: str = ""


class PracticeAttempt(BaseModel):
    problem_id: str
    family_id: str
    answer: str
    correct: bool
    answer_type: str
    shown_work: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AssessmentQuestionResult(BaseModel):
    problem: PracticeProblem
    selected_answer: str
    correct: bool
    shown_work: str = ""
    error_code: str | None = None
    error_category: str | None = None


class AssessmentBlueprint(BaseModel):
    assessment_type: Literal["Quiz", "Test", "Exam"]
    scopes: list[str]
    question_count: int
    min_l4: int = 0
    min_l6: int = 0
    min_structural_signatures: int = 0
    min_families: int = 0
    min_multi_method: int = 0
    max_per_family: int = 3
    require_no_exact_duplicates: bool = True
    require_no_near_duplicates: bool = True


class AssessmentRecord(BaseModel):
    assessment_id: str
    assessment_type: Literal["Quiz", "Test", "Exam"]
    scopes: list[str]
    question_results: list[AssessmentQuestionResult]
    duration_seconds: int = Field(ge=0)
    started_at: datetime
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    blueprint: AssessmentBlueprint | None = None

    @property
    def correct_count(self) -> int:
        return sum(result.correct for result in self.question_results)

    @property
    def accuracy(self) -> float:
        return self.correct_count / len(self.question_results) if self.question_results else 0.0


class RepairRecord(BaseModel):
    assessment_id: str
    problem_id: str
    family_id: str
    rule_check_correct: bool
    transfer_problem_id: str | None = None
    transfer_correct: bool | None = None
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
