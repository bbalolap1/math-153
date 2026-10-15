from __future__ import annotations

import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from typing import Literal

from pydantic import BaseModel

from .assessment import build_assessment
from .complexity import diversity_report, normalized_prompt_structure
from .course_content import PROBLEM_FAMILY_INDEX
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
    mapping_status: Literal[
        "CORRECT FAMILY","OVERLY BROAD FAMILY","WRONG FAMILY","NO ADEQUATE FAMILY"
    ]
    mapping_reason: str=""


class MatrixRecord(BaseModel):
    family_id: str
    source_question: str
    generated_question: str
    seed: int
    difficulty: str
    correct_answer: str
    solution: list[str]
    validation_status: str
    source_refs: list[str]
    structural_signature: str=""
    normalized_source: str=""
    normalized_generated: str=""


def _answer_type(text: str, family_id: str) -> str:
    lower=text.casefold()
    if "interval notation" in lower: return "interval"
    if "a+bi" in lower: return "complex_number"
    if "domain" in lower: return "domain"
    if "range" in lower: return "range"
    if "intercept" in lower: return "ordered_pairs"
    if "graph" in lower or "sketch" in lower: return "graph"
    if "all real" in lower or "solutions" in lower: return "solution_set"
    return "expression_or_number"


def _score_family(entry: SourceManifestEntry, record: ExtractedRecord, family_id: str) -> float:
    family=PROBLEM_FAMILY_INDEX[family_id]
    score=0.0
    text=f"{record.label}\n{record.content}".casefold()
    source_names={r.document.casefold() for r in family.source_refs}
    entry_name=entry.actual_path.split("/")[-1].casefold()
    if entry_name in {name.split("/")[-1] for name in source_names}: score+=6
    if entry.chapter_or_section == next((s.id for s in []), ""): score+=0
    for clue in family.recognition_features:
        words=[w for w in re.findall(r"[a-z]{4,}",clue.casefold()) if w not in {"with","from","into","that","this"}]
        score+=sum(0.6 for w in set(words) if w in text)
    for verb in family.professor_verbs:
        if verb.casefold() in text: score+=0.5
    for concept in family.required_concepts:
        for word in re.findall(r"[a-z]{4,}",concept.casefold()):
            if word in text: score+=0.35
    return score


def classify_question(entry: SourceManifestEntry, record: ExtractedRecord) -> QuestionAudit:
    scores=sorted(
        ((_score_family(entry,record,fid),fid) for fid in FAMILY_SPECS),
        reverse=True,
    )
    best_score,best_id=scores[0]
    if best_score < 1.0:
        return QuestionAudit(
            source_path=entry.actual_path,question_number=record.label,
            question_text=record.content or record.label,
            mathematical_structure="unmapped source structure",
            required_method="requires manual/source review",
            answer_type=_answer_type(record.content,best_id),
            mapped_family_id="",
            mapping_status="NO ADEQUATE FAMILY",
            mapping_reason=f"Best canonical match score {best_score:.2f} was below threshold.",
        )
    family=PROBLEM_FAMILY_INDEX[best_id]
    second=scores[1][0] if len(scores)>1 else 0
    ambiguous=best_score-second<0.5 and best_score<6
    return QuestionAudit(
        source_path=entry.actual_path,question_number=record.label,
        question_text=record.content or record.label,
        mathematical_structure="; ".join(family.recognition_features),
        required_method=" → ".join(family.required_procedures) or "conceptual/source-supported reasoning",
        answer_type=_answer_type(record.content,best_id),
        mapped_family_id=best_id,
        mapping_status="OVERLY BROAD FAMILY" if ambiguous else "CORRECT FAMILY",
        mapping_reason=f"score={best_score:.2f}; next={second:.2f}; canonical family={family.title}",
    )


def audit_questions(entries: list[SourceManifestEntry]) -> list[QuestionAudit]:
    return [
        classify_question(entry,record)
        for entry in entries
        for record in entry.extracted_records
        if record.record_type=="question"
    ]


def build_test_matrix(
    audits: list[QuestionAudit],
    family_source_map: dict[str,list[str]],
    seed: int=15300,
) -> list[MatrixRecord]:
    examples: dict[str,list[QuestionAudit]]=defaultdict(list)
    for audit in audits:
        if audit.mapped_family_id: examples[audit.mapped_family_id].append(audit)
    matrix=[]
    for index,family_id in enumerate(FAMILY_SPECS):
        problem=generate_practice_problem(family_id,seed+index*101,index%8)
        valid=validate_practice_answer(problem,problem.expected_answer).correct
        source_question=(
            examples[family_id][0].question_text
            if examples[family_id]
            else (family_source_map.get(family_id) or problem.source_refs or ["No source exemplar extracted"])[0]
        )
        matrix.append(MatrixRecord(
            family_id=family_id,source_question=source_question,generated_question=problem.prompt,
            seed=problem.parameter_seed,difficulty=problem.difficulty_layer.value,
            correct_answer=problem.expected_answer,
            solution=[problem.worked_solution.setup,*problem.worked_solution.calculation,problem.worked_solution.check],
            validation_status="passed" if valid else "failed",source_refs=problem.source_refs,
            structural_signature=problem.structural_signature,
            normalized_source=normalized_prompt_structure(source_question),
            normalized_generated=normalized_prompt_structure(problem.prompt),
        ))
    return matrix


def source_fidelity_score(source: str, generated: str) -> dict[str,float]:
    """
    Similarity is not used as a goal by itself—the generated question should be novel.
    It is surfaced to audit whether generation is either a copy or completely detached.
    """
    s=normalized_prompt_structure(source); g=normalized_prompt_structure(generated)
    ratio=SequenceMatcher(None,s,g).ratio()
    return {"normalized_similarity":ratio,"novel_surface":float(ratio<0.92),"not_detached":float(ratio>0.10)}


def quality_metrics(
    audits: list[QuestionAudit],
    matrix: list[MatrixRecord],
    family_source_map: dict[str,list[str]],
) -> dict[str,object]:
    statuses=Counter(a.mapping_status for a in audits)
    representative=[
        generate_practice_problem(fid,71530+i,i%8) for i,fid in enumerate(FAMILY_SPECS)
    ]
    detailed=[teaching_solution(p) for p in representative]
    final=build_assessment(["Math 153"],30,50153,assessment_type="Exam")
    diversity=diversity_report(final)
    variant_tests=[
        generate_practice_problem(fid,61000+i*100+v,v)
        for i,fid in enumerate(FAMILY_SPECS)
        for v in range(4)
    ]
    return {
        "source_questions_audited":len(audits),
        "correct_family_mappings":statuses["CORRECT FAMILY"],
        "ambiguous_or_overbroad_mappings":statuses["OVERLY BROAD FAMILY"],
        "unmapped_questions":statuses["NO ADEQUATE FAMILY"],
        "canonical_family_count":len(FAMILY_SPECS),
        "families_with_source_refs":sum(bool(v) for v in family_source_map.values()),
        "matrix_expected_answer_validation_passes":sum(r.validation_status=="passed" for r in matrix),
        "generated_variants_tested":len(variant_tests),
        "generated_variants_valid":sum(validate_practice_answer(p,p.expected_answer).correct for p in variant_tests),
        "families_with_detailed_execution":sum(s.quality_status=="detailed" for s in detailed),
        "final_exam_diversity":diversity,
        "acceptance_rule":(
            "Generated questions must preserve source mathematical DNA and answer form while "
            "remaining novel in normalized prompt/structural signature; number-only duplicates fail."
        ),
    }
