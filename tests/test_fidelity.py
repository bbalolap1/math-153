import json
from pathlib import Path

from math153_tutor.fidelity import audit_questions, build_test_matrix, quality_metrics
from math153_tutor.source_manifest import read_manifest


def test_all_extracted_questions_are_audited_and_mapped() -> None:
    root = Path(__file__).parents[1]
    entries = read_manifest(root / "data/derived/source_manifest.json")
    family_map = json.loads((root / "data/derived/family_source_map.json").read_text())
    audits = audit_questions(entries)
    matrix = build_test_matrix(audits, family_map)
    metrics = quality_metrics(audits, matrix, family_map)

    assert len(audits) == 240
    assert metrics["incorrect_mappings"] == 0
    assert metrics["unmapped_questions"] == 0
    assert len(matrix) == metrics["final_question_family_count"] == 35
    assert all(row.validation_status == "passed" and row.source_refs for row in matrix)
    assert metrics["generated_variants_failed"] == 0
    assert metrics["fifty_question_validation_passed"] is True
    assert metrics["duplicate_questions_in_50_set"] == 0
    assert metrics["multiple_choice_order_failures"] == 0
    assert metrics["student_math_render_failures"] == 0


def test_render_matrix_covers_student_math_notation() -> None:
    from math153_tutor.math_display import readable_prompt

    prompts = [
        r"Simplify $\\frac{x+1}{x-2}$.", r"Simplify $\\sqrt{x+4}$.",
        r"Evaluate $x^{3/2}$.", r"Write $2+3i$.", r"Find $(f\\circ g)(x)$.",
        r"Factor $x^3-1$.", r"Solve $x\\le 4$ and use $(-\\infty,4]$.",
        r"Solve $2^x=8$.", r"Solve $\\log_2(x)=3$.",
    ]
    assert all("**" not in readable_prompt(prompt) for prompt in prompts)
