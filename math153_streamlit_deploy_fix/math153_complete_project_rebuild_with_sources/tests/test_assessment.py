from math153_tutor.assessment import assessment_presets, build_assessment
from math153_tutor.complexity import diversity_report


def test_source_pattern_presets():
    for kind,count in (("Quiz",5),("Test",15),("Exam",30)):
        for preset in assessment_presets(kind):
            problems=build_assessment([f"preset:{kind}:{preset}"],count,153000+len(preset),assessment_type=kind)
            report=diversity_report(problems)
            assert len(problems)==count
            assert report["exact_duplicates"]==0
            assert report["near_duplicates"]==0


def test_final_50_unique():
    problems=build_assessment(["Math 153"],50,91530,assessment_type="Exam")
    report=diversity_report(problems)
    assert report["unique_visible_prompts"]==50
    assert report["unique_normalized_structures"]==50
    assert report["unique_structural_signatures"]==50
