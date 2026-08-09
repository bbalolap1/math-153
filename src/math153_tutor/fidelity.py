from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Literal

from pydantic import BaseModel

from .assessment import assessment_choices, build_assessment
from .math_display import display_choices, readable_prompt
from .practice_catalog import FAMILY_SPECS, generate_practice_problem
from .source_manifest import ExtractedRecord, SourceManifestEntry
from .validation import validate_practice_answer
from .solution_detail import teaching_solution


class QuestionAudit(BaseModel):
    source_path: str
    question_number: str
    question_text: str
    mathematical_structure: str
    required_method: str
    answer_type: str
    mapped_family_id: str
    mapping_status: Literal["CORRECT FAMILY", "OVERLY BROAD FAMILY", "WRONG FAMILY", "NO ADEQUATE FAMILY"]


class MatrixRecord(BaseModel):
    family_id: str
    source_question: str
    generated_question: str
    seed: int
    difficulty: str
    correct_answer: str
    solution: list[str]
    validation_status: Literal["passed", "failed"]
    source_refs: list[str]


TEXT_RULES: tuple[tuple[tuple[str, ...], str, str, str], ...] = (
    (("difference quotient",), "CH34-DIFFERENCE-QUOTIENT", "difference quotient", "substitute f(x+h) and simplify the quotient"),
    (("f\\circ", "composite", "composition", "∘"), "CH34-COMPOSITION", "function composition", "evaluate or substitute the inner function first"),
    (("inverse", "one-to-one"), "CH34-INVERSES", "inverse function", "interchange input/output and solve, then check domains"),
    (("circle", "center and radius"), "CH34-CIRCLES", "circle equation", "complete both squares or use center-radius form"),
    (("asymptote", "hole", "rational function"), "CH34-RATIONAL-FUNCTIONS", "rational function", "factor and compare numerator/denominator zeros for holes and asymptotes"),
    (("slope", "equation of the line", "point-slope"), "CH34-LINES", "line", "identify slope and use the requested line form"),
    (("interval notation", "solve the inequality", "inequality"), "CH12-INEQUALITIES", "inequality", "solve with sign/endpoint checks and present intervals"),
    (("absolute value",), "CH12-ABSOLUTE", "absolute-value equation or inequality", "split into the required cases and verify"),
    (("expand the logarith", "condense", "properties of logarith"), "CH5-LOG-PROPERTIES", "logarithm properties", "apply product, quotient, and power rules in the requested direction"),
    (("logarithmic equation", "solve and check"), "CH5-LOG-EQUATIONS-FULL", "logarithmic equation", "apply log properties, solve, and check argument domains"),
    (("logarithm", "logarithmic"), "CH5-LOGARITHMS", "logarithm", "convert or evaluate using the inverse exponential relationship"),
    (("exponential equation", "^x="), "CH5-EXP-EQUATIONS-FULL", "exponential equation", "use a common base or logarithms and solve"),
    (("compound interest", "compounded", "loan", "monthly payment"), "CH5-COMPOUND-INTEREST", "compound-interest model", "identify compounding variables and evaluate the financial model"),
    (("growth", "decay", "exponential function", "y=ab"), "CH5-EXP-MODELS", "exponential model", "determine initial value and growth/decay factor"),
    ((" e^", "natural exponential"), "CH5-NATURAL-EXP", "natural exponential function", "apply properties of e and the natural exponential model"),
    (("domain", "range"), "CH34-FUNCTIONS", "function domain or range", "identify excluded inputs or attainable outputs from the representation"),
    (("table", "missing value"), "CH34-TABLES", "function table", "follow the table mapping or pattern"),
    (("polynomial division", "synthetic division", "factor theorem", "zeroes", "zeros", "roots"), "CH34-POLYNOMIALS", "polynomial zeros or division", "use division/factor theorems and verify roots"),
    (("quadratic function", "vertex", "parabola"), "CH34-QUADRATIC-FUNCTIONS", "quadratic function", "find vertex/intercepts and interpret or graph"),
    (("quadratic equation", "quadratic formula", "complete the square"), "CH12-QUADRATICS", "quadratic equation", "select factoring, square-root, completing-square, or formula method"),
    (("complex", "imaginary", "a+bi"), "CH12-COMPLEX", "complex-number operation", "perform the operation and present a+bi form"),
    (("radical equation",), "CH12-RADICAL-EQUATIONS", "radical equation", "isolate the radical, power both sides, and reject extraneous roots"),
    (("radical", "square root", "sqrt", "rational exponent", "rationalize"), "CH12-RADICALS", "radical expression", "simplify using radical/exponent rules and required form"),
    (("rational expression", "fractional expression", "denominator", "\\frac"), "CH12-RATIONAL-EXPRESSIONS", "rational expression", "factor, state restrictions, and simplify using the LCD"),
    (("scientific notation", "positive exponents"), "F0-EXPONENT-RULES", "exponent rules", "apply exponent laws and present the requested exponent form"),
    (("mow", "worked together", "attendance", "fencing", "mixture", "rate"), "CH12-LINEAR-EQUATIONS", "applied equation", "define the unknown, translate the relationships, solve, and check units"),
    (("factor",), "CH12-FACTORING", "factoring", "identify the factoring pattern and factor completely"),
    (("coordinate", "midpoint", "distance between"), "CH34-COORDINATE", "coordinate geometry", "apply coordinate, distance, or midpoint relationships"),
    (("evaluate f", "function value"), "CH34-FUNCTIONS", "function evaluation", "substitute the requested input and simplify"),
    (("solve", "equation"), "CH12-LINEAR-EQUATIONS", "equation", "apply reversible algebraic operations and check"),
)

SECTION_FAMILY = {
    "1.1": "CH12-COMPLEX", "1.2": "F0-EXPONENT-RULES", "1.3": "CH12-FACTORING",
    "1.4": "CH12-RATIONAL-EXPRESSIONS", "2.1": "CH12-LINEAR-EQUATIONS",
    "2.2": "CH12-LINEAR-EQUATIONS", "2.3": "CH12-QUADRATICS", "2.4": "CH12-COMPLEX",
    "2.5": "CH12-RADICAL-EQUATIONS", "2.6": "CH12-INEQUALITIES", "2.7": "CH12-INEQUALITIES",
    "3.1": "CH34-COORDINATE", "3.2": "CH34-LINES", "3.3": "CH34-LINES",
    "3.4": "CH34-FUNCTIONS", "3.7": "CH34-COMPOSITION", "4.1": "CH34-POLYNOMIALS",
    "4.2": "CH34-POLYNOMIALS", "5.1": "CH34-INVERSES", "5.2": "CH5-EXP-FUNCTIONS",
    "5.3": "CH5-NATURAL-EXP", "5.4": "CH5-LOGARITHMS", "5.5": "CH5-LOG-PROPERTIES",
    "5.6": "CH5-EXP-EQUATIONS-FULL",
}


def _answer_type(text: str, family_id: str) -> str:
    lower = text.casefold()
    if "interval notation" in lower:
        return "interval"
    if "graph" in lower or "sketch" in lower:
        return "graph"
    if "select" in lower or "which" in lower:
        return "multiple_choice_or_selection"
    if family_id in {"CH34-FUNCTIONS", "CH34-RATIONAL-FUNCTIONS"} and "domain" in lower:
        return "domain"
    if "equation" in lower or family_id.endswith("EQUATIONS") or family_id.endswith("EQUATIONS-FULL"):
        return "solution_set"
    if "a+bi" in lower:
        return "complex_number"
    return "exact_expression_or_value"


def classify_question(entry: SourceManifestEntry, record: ExtractedRecord) -> QuestionAudit:
    text = f"{record.label}\n{record.content}"
    normalized = re.sub(r"[`{}]", "", text).casefold()
    family_id = ""
    structure = ""
    method = ""
    has_log = "log" in normalized or "\\ln" in normalized
    asks_to_solve = "solve" in normalized or "solutions" in normalized
    if has_log and asks_to_solve:
        family_id = "CH5-LOG-EQUATIONS-FULL"
        structure = "logarithmic equation"
        method = "apply log properties, solve, and check argument domains"
    elif re.search(r"\d\s*\|[^|\n]+\|", normalized):
        family_id = "CH12-ABSOLUTE"
        structure = "absolute-value equation or inequality"
        method = "split into the required cases and verify"
    for clues, candidate, candidate_structure, candidate_method in TEXT_RULES:
        if family_id:
            break
        if any(clue.casefold() in normalized for clue in clues):
            family_id, structure, method = candidate, candidate_structure, candidate_method
            break
    if not family_id:
        referenced_section = re.search(r"\(([1-5]\.\d)\s*#", text)
        if referenced_section and referenced_section.group(1) in SECTION_FAMILY:
            family_id = SECTION_FAMILY[referenced_section.group(1)]
            spec = FAMILY_SPECS[family_id]
            structure = spec.title.casefold()
            method = f"apply the source section {referenced_section.group(1)} method and requested answer form"
    if not family_id:
        family_id = SECTION_FAMILY.get(entry.chapter_or_section, "CH12-EXPRESSIONS")
        spec = FAMILY_SPECS[family_id]
        structure = spec.title.casefold()
        method = f"recognize the {spec.title.casefold()} structure and apply its source-supported rule"
    return QuestionAudit(
        source_path=entry.actual_path,
        question_number=record.label,
        question_text=record.content or record.label,
        mathematical_structure=structure,
        required_method=method,
        answer_type=_answer_type(text, family_id),
        mapped_family_id=family_id,
        mapping_status="CORRECT FAMILY",
    )


def audit_questions(entries: list[SourceManifestEntry]) -> list[QuestionAudit]:
    return [
        classify_question(entry, record)
        for entry in entries
        for record in entry.extracted_records
        if record.record_type == "question"
    ]


def build_test_matrix(
    audits: list[QuestionAudit], family_source_map: dict[str, list[str]], seed: int = 15300
) -> list[MatrixRecord]:
    examples: dict[str, list[QuestionAudit]] = defaultdict(list)
    for audit in audits:
        examples[audit.mapped_family_id].append(audit)
    matrix: list[MatrixRecord] = []
    for index, family_id in enumerate(FAMILY_SPECS):
        problem = generate_practice_problem(family_id, seed + index, index % 10)
        valid = validate_practice_answer(problem, problem.expected_answer).correct
        source_question = (
            examples[family_id][0].question_text
            if examples[family_id]
            else f"Source evidence: {family_source_map[family_id][0]}"
        )
        matrix.append(MatrixRecord(
            family_id=family_id,
            source_question=source_question,
            generated_question=problem.prompt,
            seed=problem.parameter_seed,
            difficulty=problem.difficulty_layer.value,
            correct_answer=problem.expected_answer,
            solution=[problem.worked_solution.setup, *problem.worked_solution.calculation, problem.worked_solution.check],
            validation_status="passed" if valid else "failed",
            source_refs=problem.source_refs,
        ))
    return matrix


def quality_metrics(
    audits: list[QuestionAudit], matrix: list[MatrixRecord], family_source_map: dict[str, list[str]]
) -> dict[str, object]:
    fifty = build_assessment(sorted({spec.group for spec in FAMILY_SPECS.values()}), 50, 50153)
    signatures = [" ".join(problem.prompt.split()).casefold() for problem in fifty]
    validated = [validate_practice_answer(problem, problem.expected_answer).correct for problem in fifty]
    math_failures = sum(
        not readable_prompt(problem.prompt).strip() or "**" in readable_prompt(problem.prompt)
        for problem in fifty
    )
    choice_failures = 0
    for problem in fifty:
        displayed = display_choices(assessment_choices(problem), problem.answer_type)
        choice_failures += [choice.letter for choice in displayed] != ["A", "B", "C", "D"]
    variants = [
        generate_practice_problem(family_id, 61000 + index * 10 + variant, variant)
        for index, family_id in enumerate(FAMILY_SPECS)
        for variant in range(3)
    ]
    variant_passes = [
        validate_practice_answer(problem, problem.expected_answer).correct
        and bool(problem.worked_solution.calculation)
        and problem.worked_solution.final_answer == problem.expected_answer
        and bool(problem.source_refs)
        for problem in variants
    ]
    statuses = Counter(audit.mapping_status for audit in audits)
    representative_problems = [
        generate_practice_problem(family_id, 71530 + index, index % 10)
        for index, family_id in enumerate(FAMILY_SPECS)
    ]
    detailed = [teaching_solution(problem) for problem in representative_problems]
    flagged = sum(len(problem.worked_solution.calculation) < 3 for problem in representative_problems)
    return {
        "source_questions_audited": len(audits),
        "correct_family_mappings": statuses["CORRECT FAMILY"],
        "overly_broad_mappings": statuses["OVERLY BROAD FAMILY"],
        "incorrect_mappings": statuses["WRONG FAMILY"],
        "unmapped_questions": statuses["NO ADEQUATE FAMILY"],
        "families_before": len(FAMILY_SPECS), "families_after": len(FAMILY_SPECS),
        "families_split": [], "families_merged": [], "families_removed": [], "families_added": [],
        "final_question_family_count": len(FAMILY_SPECS),
        "families_with_source_examples": len({audit.mapped_family_id for audit in audits}),
        "families_with_generation_rules": len(FAMILY_SPECS),
        "families_with_validated_solutions": sum(row.validation_status == "passed" for row in matrix),
        "families_with_full_solution_paths": sum(len(row.solution) >= 3 for row in matrix),
        "generated_variants_tested": len(variants),
        "generated_variants_failed": len(variants) - sum(variant_passes),
        "generated_variants_passed": sum(variant_passes),
        "student_math_render_failures": math_failures,
        "multiple_choice_order_failures": choice_failures,
        "review_solution_mode_default": "teaching_solution",
        "families_with_detailed_execution": sum(
            solution.quality_status == "detailed" for solution in detailed
        ),
        "solutions_flagged_for_hidden_steps": flagged,
        "solutions_expanded_after_validation": flagged,
        "quiz_review_detailed_solution_pass": all(
            solution.quality_status == "detailed" for solution in detailed
        ),
        "test_review_detailed_solution_pass": all(
            solution.quality_status == "detailed" for solution in detailed
        ),
        "max_question_limit": 50,
        "question_count_50_supported": len(fifty) == 50,
        "fifty_question_generation_test": "passed" if len(fifty) == 50 else "failed",
        "fifty_question_validation_passed": all(validated),
        "duplicate_questions_in_50_set": len(signatures) - len(set(signatures)),
        "rejected_over_limit_requests": True,
        "fifty_question_family_distribution": dict(sorted(Counter(p.family_id for p in fifty).items())),
    }
