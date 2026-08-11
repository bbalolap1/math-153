from __future__ import annotations

from .models import ErrorCategory, GeneratedProblem
from .practice_catalog import FAMILY_SPECS, generate_practice_problem


def generate_problem(family_id: str, seed: int, variant: int = 0) -> GeneratedProblem:
    """Compatibility adapter around the canonical PracticeProblem generator."""
    p = generate_practice_problem(family_id, seed, variant)
    recognition = p.family_title
    first = p.worked_solution.inference
    return GeneratedProblem(
        problem_id=p.problem_id,
        family_id=p.family_id,
        construction_id=p.structural_variant_type,
        difficulty_layer=p.difficulty_layer,
        prompt=p.prompt,
        expected_answer=p.expected_answer,
        validator="solution_set" if p.answer_type == "solution_set" else "expression",
        recognition_options=[recognition],
        correct_recognition=recognition,
        first_decision_options=[first],
        correct_first_decision=first,
        source_refs=p.source_refs,
        source_construction_refs=p.source_refs,
        source_concept_refs=p.source_refs,
        generation_method="controlled_template",
        parameter_seed=seed,
        required_skills=p.required_skills,
        variant_reason=p.variant_reason,
        reasoning_checkpoints=p.reasoning_checkpoints,
        exact_form_required=p.answer_type in {"fraction","radical","logarithmic_expression"},
        critical_checks=[
            *("domain" if p.requires_domain_check else "",),
            *("extraneous" if p.requires_extraneous_check else "",),
        ] if (p.requires_domain_check or p.requires_extraneous_check) else [],
        targeted_feedback={
            ErrorCategory.RECOGNITION: f"Identify the family: {p.family_title}.",
            ErrorCategory.FIRST_STEP: p.worked_solution.inference,
            ErrorCategory.DOMAIN: p.worked_solution.check,
            ErrorCategory.ALGEBRA: "Compare your algebra one line at a time with the worked solution.",
        },
        structural_signature=p.structural_signature,
        complexity_evidence=p.complexity_evidence,
    )


# Backward-compatible narrow names used by older callers.
def available_families() -> list[str]:
    return list(FAMILY_SPECS)
