from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

from math153_tutor.assessment import build_assessment
from math153_tutor.complexity import normalized_prompt_structure
from math153_tutor.practice_catalog import FAMILY_SPECS, family_source_refs, family_variants


def main(repository_root: str = ".") -> None:
    root = Path(repository_root).resolve()
    derived = root / "data" / "derived"
    audits = []
    number_only = []
    structural = []
    for family_id in FAMILY_SPECS:
        variants = family_variants(family_id)
        structures = sorted({normalized_prompt_structure(problem.prompt) for problem in variants})
        if len(structures) == 1:
            number_only.append(family_id)
        else:
            structural.append(family_id)
        audits.append({
            "family_id": family_id,
            "variation_dimensions_observed": {
                "A_numbers": True,
                "B_coefficients_constants": True,
                "C_wording": len(structures) > 1,
                "D_representation": len({problem.representation_type for problem in variants}) > 1,
                "E_prerequisite_structure": len({problem.prerequisite_count for problem in variants}) > 1,
                "F_reasoning_path": len({problem.decision_count for problem in variants}) > 1,
                "G_concept_combination": any(problem.requires_multiple_methods for problem in variants),
            },
            "diversity_status": "LOW-DIVERSITY" if len(structures) == 1 else "STRUCTURAL-VARIATION",
            "structural_variant_count": len(structures),
            "structural_variants": structures,
            "source_support_for_each_variant": {
                structure: family_source_refs()[family_id] for structure in structures
            },
        })

    scopes = sorted({spec.group for spec in FAMILY_SPECS.values()})
    questions = build_assessment(
        scopes, 50, 91530, complexity_profile="Final Exam Challenge"
    )
    levels = Counter(problem.complexity_level.value for problem in questions)
    prompts = [problem.prompt for problem in questions]
    normalized = [normalized_prompt_structure(prompt) for prompt in prompts]
    signatures = [problem.structural_signature for problem in questions]
    family_counts = Counter(problem.family_id for problem in questions)
    steps = [problem.estimated_solution_steps for problem in questions]
    high = sum(int(problem.complexity_level.value[1]) >= 4 for problem in questions)
    exam_pressure = sum(int(problem.complexity_level.value[1]) >= 6 for problem in questions)
    multi = sum(
        problem.prerequisite_count > 1 or problem.decision_count > 1 for problem in questions
    )
    report = {
        "structural_complexity_complete": not number_only,
        "limitation": (
            "Families listed under families_with_number_only_variation remain intentionally "
            "blocked from claims of deep structural diversity until additional source-supported "
            "templates and validators are authored. They are not counted as upgraded."
            if number_only else "none"
        ),
        "families_audited": len(FAMILY_SPECS),
        "families_with_number_only_variation": number_only,
        "families_with_structural_variation": structural,
        "families_upgraded": ["CH34-DIFFERENCE-QUOTIENT"],
        "structural_variant_count_by_family": {
            audit["family_id"]: audit["structural_variant_count"] for audit in audits
        },
        "source_support_for_each_variant": {
            audit["family_id"]: audit["source_support_for_each_variant"] for audit in audits
        },
        "final_exam_review": {
            "questions_generated": len(questions),
            "difficulty_distribution": {f"L{index}_count": levels[f"L{index}"] for index in range(8)},
            "unique_question_texts": len(set(prompts)),
            "unique_structural_signatures": len(set(signatures)),
            "families_used": len(family_counts),
            "max_questions_from_single_family": max(family_counts.values()),
            "exact_duplicates": len(prompts) - len(set(prompts)),
            "near_duplicates": len(normalized) - len(set(normalized)),
            "average_solution_steps": statistics.mean(steps),
            "minimum_solution_steps": min(steps),
            "maximum_solution_steps": max(steps),
            "questions_requiring_multiple_prerequisites": multi,
            "questions_requiring_method_selection": sum(problem.decision_count > 1 for problem in questions),
            "questions_requiring_verification": sum(bool(problem.worked_solution.check) for problem in questions),
            "questions_l4_or_higher": high,
            "questions_l6_or_l7": exam_pressure,
            "family_distribution": dict(sorted(family_counts.items())),
        },
    }
    final = report["final_exam_review"]
    if not (
        final["questions_generated"] == 50
        and final["unique_question_texts"] == 50
        and final["exact_duplicates"] == 0
        and final["questions_l4_or_higher"] >= 25
        and final["questions_l6_or_l7"] >= 10
        and final["questions_requiring_multiple_prerequisites"] >= 15
    ):
        raise ValueError(f"Final-exam complexity gates failed: {final}")
    (derived / "complexity_family_audit.json").write_text(
        json.dumps(audits, indent=2) + "\n", encoding="utf-8"
    )
    (derived / "complexity_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
