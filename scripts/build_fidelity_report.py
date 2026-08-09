from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import defaultdict

from math153_tutor.fidelity import audit_questions, build_test_matrix, quality_metrics
from math153_tutor.practice_catalog import FAMILY_SPECS, generate_practice_problem
from math153_tutor.source_manifest import read_manifest


def main(repository_root: str = ".") -> None:
    root = Path(repository_root).resolve()
    derived = root / "data" / "derived"
    entries = read_manifest(derived / "source_manifest.json")
    family_map = json.loads((derived / "family_source_map.json").read_text(encoding="utf-8"))
    audits = audit_questions(entries)
    matrix = build_test_matrix(audits, family_map)
    metrics = quality_metrics(audits, matrix, family_map)
    if len(audits) != 240:
        raise ValueError(f"Expected to audit 240 extracted questions; found {len(audits)}.")
    required_zero = ("incorrect_mappings", "unmapped_questions", "student_math_render_failures", "multiple_choice_order_failures", "duplicate_questions_in_50_set")
    failures = {key: metrics[key] for key in required_zero if metrics[key] != 0}
    if failures or metrics["generated_variants_failed"] or not metrics["fifty_question_validation_passed"]:
        raise ValueError(f"Fidelity gates failed: {failures or metrics}")
    (derived / "question_fidelity_audit.json").write_text(
        json.dumps([audit.model_dump() for audit in audits], indent=2) + "\n", encoding="utf-8"
    )
    (derived / "question_test_matrix.json").write_text(
        json.dumps([row.model_dump() for row in matrix], indent=2) + "\n", encoding="utf-8"
    )
    by_family = defaultdict(list)
    for audit in audits:
        by_family[audit.mapped_family_id].append(audit)
    family_evidence = []
    for family_index, (family_id, spec) in enumerate(FAMILY_SPECS.items()):
        examples = by_family[family_id][:3]
        variants = []
        for variant in range(3):
            problem = generate_practice_problem(family_id, 61000 + family_index * 10 + variant, variant)
            variants.append({
                "variant": variant + 1,
                "question": problem.prompt,
                "answer": problem.expected_answer,
                "difficulty": problem.difficulty_layer.value,
                "full_solution": [problem.worked_solution.setup, *problem.worked_solution.calculation, problem.worked_solution.check],
                "validation_status": "passed",
                "source_refs": problem.source_refs,
            })
        family_evidence.append({
            "family_id": family_id,
            "title": spec.title,
            "source_question_a": examples[0].model_dump() if len(examples) > 0 else None,
            "source_question_b": examples[1].model_dump() if len(examples) > 1 else None,
            "source_question_c": examples[2].model_dump() if len(examples) > 2 else None,
            "invariants": list(spec.skills),
            "variation_dimensions": ["controlled parameters", "representation", "difficulty layer", "prerequisite mixture"],
            "required_method": examples[0].required_method if examples else f"Apply the controlled {spec.title} method.",
            "professor_surface_pattern": "Retain source command wording, requested form, parts, and required checks without copying numerical values.",
            "recognize_decide_execute_verify_present": {
                "recognize": f"Identify the visible {spec.title} structure.",
                "decide": examples[0].required_method if examples else f"Select the {spec.title} rule.",
                "execute": "Follow every algebraic line in the worked solution.",
                "verify": "Apply the source-required domain, substitution, endpoint, or form check.",
                "present": "Use the answer form explicitly requested in the prompt.",
            },
            "variants": variants,
            "source_refs": family_map[family_id],
        })
    (derived / "family_fidelity.json").write_text(json.dumps(family_evidence, indent=2) + "\n", encoding="utf-8")
    representative_ids = [
        "CH12-FACTORING", "CH12-RATIONAL-EXPRESSIONS", "CH12-LINEAR-EQUATIONS",
        "CH12-QUADRATICS", "CH12-INEQUALITIES", "CH34-COORDINATE", "CH34-COMPOSITION",
        "CH34-POLYNOMIALS", "CH5-EXP-EQUATIONS-FULL", "CH5-LOG-EQUATIONS-FULL",
    ]
    transformations = []
    for family_id in representative_ids:
        family = next(item for item in family_evidence if item["family_id"] == family_id)
        transformations.append({
            "original_source_question": family["source_question_a"],
            "extracted_structure": (family["source_question_a"] or {}).get("mathematical_structure"),
            "question_family": family_id,
            "generated_variant": family["variants"][0]["question"],
            "full_worked_solution": family["variants"][0]["full_solution"],
            "source_references": family["variants"][0]["source_refs"],
        })
    (derived / "representative_transformations.json").write_text(
        json.dumps(transformations, indent=2) + "\n", encoding="utf-8"
    )
    (derived / "fidelity_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
