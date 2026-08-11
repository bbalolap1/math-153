from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


DocumentType = Literal[
    "lecture","activity","quiz","quiz_solution","test","test_solution",
    "review","practice_final","practice_final_solution","supplement","unknown",
]


class ExtractedRecord(BaseModel):
    record_type: Literal["question","example","formula","solution","topic","instruction","image"]
    label: str
    content: str
    locator: str = ""
    instructional_verb: str = ""
    answer_form: str = ""
    representation: str = ""
    source_hash: str = ""


class SourceManifestEntry(BaseModel):
    source_id: str
    actual_path: str
    document_type: DocumentType
    chapter_or_section: str = ""
    title: str
    topics: list[str] = Field(default_factory=list)
    question_count: int = 0
    solution_count: int = 0
    formula_count: int = 0
    content_length: int
    content_hash: str
    extraction_status: Literal["complete","partial","failed"]
    extracted_records: list[ExtractedRecord] = Field(default_factory=list)


HEADING = re.compile(r"(?m)^(#{1,6})\s+(.+?)\s*$")
SECTION = re.compile(r"(?<!\d)([1-5]\.\d)(?!\d)")
DISPLAY_FORMULA = re.compile(r"\$\$(.+?)\$\$|\\\[(.+?)\\\]", re.DOTALL)
INLINE_FORMULA = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)")
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
QUESTION_HEADING = re.compile(
    r"(?i)^(?:q(?:uestion)?\.?\s*)?\d+(?:[.)]|\b)|^(?:problem|exercise)\s+\d+"
)
VERBS = (
    "find all","find","solve","simplify","factor","evaluate","compute","determine",
    "write","state","classify","graph","sketch","show","verify","express","convert",
    "rationalize","identify","select","approximate","calculate","use",
)

TOPIC_TERMS = {
    "absolute value": ("absolute value",),
    "applied problems": ("applied problem","rate problem","mixture","work rate","distance"),
    "complex numbers": ("complex number","imaginary","conjugate"),
    "completing the square": ("completing the square","complete the square"),
    "compound interest": ("compound interest","compounded","continuous compounding"),
    "coordinate geometry": ("coordinate","midpoint","distance formula","perpendicular bisector"),
    "difference quotient": ("difference quotient","f(x+h)"),
    "equations": ("solve the equation","equation"),
    "exponential equations": ("exponential equation",),
    "exponential functions": ("exponential function","growth","decay"),
    "factoring": ("factor","factoring"),
    "function composition": ("composite function","composition","f \\circ g","f∘g"),
    "functions": ("function","domain","range","increasing","decreasing"),
    "inequalities": ("inequalit","interval notation","sign chart"),
    "inverse functions": ("inverse function","one-to-one","horizontal line test"),
    "lines": ("slope","equation of the line","parallel","perpendicular"),
    "logarithmic equations": ("logarithmic equation","solve and check"),
    "logarithms": ("logarithm","logarithmic","ln"),
    "polynomials": ("polynomial","long division","remainder theorem","zeros","multiplicity"),
    "quadratic equations": ("quadratic equation","quadratic formula","discriminant"),
    "radicals": ("radical","square root","rational exponent","rationalize"),
    "rational expressions": ("rational expression","fractional expression","lcd","excluded value"),
    "circles": ("circle","radius","center"),
}


def source_root(repository_root: Path) -> Path:
    return repository_root / "sources"


def discover_markdown_sources(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def _document_type(path: Path) -> DocumentType:
    lower = path.as_posix().casefold()
    name = path.stem.casefold()
    if "completing_the_square" in name:
        return "supplement"
    if "/lectures/" in lower:
        return "lecture"
    if "/activities/" in lower:
        return "activity"
    if "/quizzes/" in lower:
        return "quiz_solution" if "solution" in name else "quiz"
    if "/tests/" in lower:
        if "solution" in name:
            return "test_solution"
        return "review" if "review" in name else "test"
    if "/final exam review/" in lower:
        return "practice_final_solution" if "with_solutions" in name else "practice_final"
    return "unknown"


def _title(text: str, path: Path) -> str:
    m=HEADING.search(text)
    return m.group(2).strip() if m else path.stem.replace("_"," ")


def _topics(text: str, title: str) -> list[str]:
    hay=f"{title}\n{text}".casefold()
    return [topic for topic,terms in TOPIC_TERMS.items() if any(term in hay for term in terms)] or [title.casefold()]


def _instructional_verb(text: str) -> str:
    lower=text.casefold()
    for verb in sorted(VERBS,key=len,reverse=True):
        if re.search(rf"\b{re.escape(verb)}\b",lower):
            return verb
    return ""


def _answer_form(text: str) -> str:
    lower=text.casefold()
    if "interval notation" in lower: return "interval"
    if "a+bi" in lower or "a + bi" in lower: return "complex_number"
    if "ordered pair" in lower or "intercept" in lower: return "ordered_pairs"
    if "equation" in lower and any(v in lower for v in ("write","find the line","circle")): return "equation"
    if "multiple choice" in lower or re.search(r"(?m)^\s*[A-D][.)]\s+",text): return "multiple_choice"
    if "graph" in lower or "sketch" in lower: return "graph"
    if "domain" in lower: return "domain"
    if "range" in lower: return "range"
    if "all real" in lower or "solutions" in lower: return "solution_set"
    return "expression_or_number"


def _representation(text: str) -> str:
    lower=text.casefold()
    if IMAGE.search(text) or "graph" in lower or "sketch" in lower: return "graph"
    if "table" in lower or re.search(r"(?m)^\s*\|.+\|\s*$",text): return "table"
    if any(k in lower for k in ("miles","hours","dollars","investment","mixture","worker","account","population","years")):
        return "context"
    if re.search(r"(?m)^\s*[A-D][.)]\s+",text): return "multiple_choice"
    return "symbolic"


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _heading_blocks(text: str):
    headings=list(HEADING.finditer(text))
    for i,m in enumerate(headings):
        end=headings[i+1].start() if i+1<len(headings) else len(text)
        yield m.group(2).strip(), text[m.end():end].strip(), m.start()


def _records(text: str, document_type: DocumentType, topics: list[str]) -> list[ExtractedRecord]:
    records: list[ExtractedRecord]=[]
    for heading,body,pos in _heading_blocks(text):
        block=(heading+"\n"+body).strip()
        loc=f"char:{pos}"
        if QUESTION_HEADING.search(heading):
            records.append(ExtractedRecord(
                record_type="question",label=heading,content=body[:8000],locator=loc,
                instructional_verb=_instructional_verb(block),answer_form=_answer_form(block),
                representation=_representation(block),source_hash=_hash(block),
            ))
        elif "example" in heading.casefold():
            records.append(ExtractedRecord(
                record_type="example",label=heading,content=body[:8000],locator=loc,
                instructional_verb=_instructional_verb(block),answer_form=_answer_form(block),
                representation=_representation(block),source_hash=_hash(block),
            ))
        elif any(v in heading.casefold() for v in ("instructions","directions")):
            records.append(ExtractedRecord(
                record_type="instruction",label=heading,content=body[:4000],locator=loc,
                instructional_verb=_instructional_verb(block),answer_form=_answer_form(block),
                representation=_representation(block),source_hash=_hash(block),
            ))
    # Preserve visual evidence rather than reducing it to a filename only.
    for idx,m in enumerate(IMAGE.finditer(text),1):
        records.append(ExtractedRecord(
            record_type="image",label=f"image-{idx}",content=f"alt={m.group(1)} path={m.group(2)}",
            locator=f"char:{m.start()}",representation="graph",source_hash=_hash(m.group(0)),
        ))
    for idx,m in enumerate(DISPLAY_FORMULA.finditer(text),1):
        formula=next(g for g in m.groups() if g is not None).strip()
        records.append(ExtractedRecord(record_type="formula",label=f"formula-{idx}",content=formula[:4000],source_hash=_hash(formula)))
    for topic in topics:
        records.append(ExtractedRecord(record_type="topic",label=topic,content=topic,source_hash=_hash(topic)))
    if "solution" in document_type:
        # Solution documents are retained as solution evidence even when question headings are sparse.
        question_records=[r for r in records if r.record_type=="question"]
        if question_records:
            for q in question_records:
                records.append(ExtractedRecord(record_type="solution",label=q.label,content=q.content,locator=q.locator,source_hash=q.source_hash))
        else:
            records.append(ExtractedRecord(record_type="solution",label="worked-solutions",content=text[:12000],source_hash=_hash(text[:12000])))
    return records


def extract_markdown_source(path: Path, repository_root: Path) -> SourceManifestEntry:
    text=path.read_text(encoding="utf-8",errors="replace")
    title=_title(text,path); topics=_topics(text,title); dtype=_document_type(path)
    records=_records(text,dtype,topics)
    relative=path.relative_to(repository_root).as_posix()
    section_hits=SECTION.findall(f"{path.stem} {title}")
    digest=hashlib.sha256(text.encode("utf-8")).hexdigest()
    return SourceManifestEntry(
        source_id="SRC-MD-"+digest[:12].upper(),
        actual_path=relative,
        document_type=dtype,
        chapter_or_section=section_hits[0] if section_hits else "cumulative",
        title=title,
        topics=topics,
        question_count=sum(r.record_type=="question" for r in records),
        solution_count=sum(r.record_type=="solution" for r in records),
        formula_count=sum(r.record_type=="formula" for r in records),
        content_length=len(text),
        content_hash=digest,
        extraction_status="complete",
        extracted_records=records,
    )


def build_markdown_manifest(repository_root: Path) -> list[SourceManifestEntry]:
    return [extract_markdown_source(p,repository_root) for p in discover_markdown_sources(source_root(repository_root))]


def write_manifest(entries: list[SourceManifestEntry], output: Path) -> None:
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.suffix==".json":
        output.write_text(json.dumps([e.model_dump() for e in entries],indent=2)+"\n",encoding="utf-8")
        return
    fields=list(SourceManifestEntry.model_fields)
    with output.open("w",newline="",encoding="utf-8") as handle:
        w=csv.DictWriter(handle,fieldnames=fields,lineterminator="\n"); w.writeheader()
        for e in entries:
            row=e.model_dump(); row["topics"]=json.dumps(row["topics"]); row["extracted_records"]=json.dumps(row["extracted_records"])
            w.writerow(row)


def read_manifest(path: Path) -> list[SourceManifestEntry]:
    if not path.is_file(): return []
    if path.suffix==".json":
        return [SourceManifestEntry.model_validate(v) for v in json.loads(path.read_text(encoding="utf-8"))]
    with path.open(newline="",encoding="utf-8") as handle: rows=list(csv.DictReader(handle))
    for row in rows:
        row["topics"]=json.loads(row["topics"]); row["extracted_records"]=json.loads(row["extracted_records"])
    return [SourceManifestEntry.model_validate(row) for row in rows]


def coverage_report(entries: list[SourceManifestEntry]) -> dict[str,object]:
    sections=sorted({e.chapter_or_section for e in entries if SECTION.fullmatch(e.chapter_or_section)})
    return {
        "documents":len(entries),
        "sections_detected":sections,
        "document_types":dict(sorted(Counter(e.document_type for e in entries).items())),
        "questions_extracted":sum(e.question_count for e in entries),
        "solutions_extracted":sum(e.solution_count for e in entries),
        "formulas_extracted":sum(e.formula_count for e in entries),
        "representations":dict(sorted(Counter(r.representation for e in entries for r in e.extracted_records if r.representation).items())),
        "instructional_verbs":dict(sorted(Counter(r.instructional_verb for e in entries for r in e.extracted_records if r.instructional_verb).items())),
        "topics":dict(sorted(Counter(t for e in entries for t in e.topics).items())),
    }


def question_exemplars(entries: list[SourceManifestEntry]) -> list[dict[str,str]]:
    """Flatten actual source questions into reusable fidelity evidence."""
    out=[]
    for entry in entries:
        for record in entry.extracted_records:
            if record.record_type!="question": continue
            out.append({
                "source_id":entry.source_id,
                "path":entry.actual_path,
                "section":entry.chapter_or_section,
                "label":record.label,
                "prompt":record.content,
                "instructional_verb":record.instructional_verb,
                "answer_form":record.answer_form,
                "representation":record.representation,
                "source_hash":record.source_hash,
            })
    return out


def build_family_source_map(entries: list[SourceManifestEntry], family_ids: list[str]) -> dict[str,list[str]]:
    """Compatibility helper; canonical family provenance now lives in course_content.py."""
    from .course_content import PROBLEM_FAMILY_INDEX
    mapping: dict[str,list[str]]={}
    for fid in family_ids:
        family=PROBLEM_FAMILY_INDEX.get(fid)
        wanted={r.document.casefold() for r in family.source_refs} if family else set()
        hits=[]
        for entry in entries:
            name=Path(entry.actual_path).name.casefold()
            if any(Path(doc).name.casefold()==name for doc in wanted):
                hits.append(entry.actual_path)
        mapping[fid]=sorted(set(hits))
    return mapping
