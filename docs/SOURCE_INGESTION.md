# Source Ingestion Plan

## Available source collections

### `math153(1).zip`
Contains section PDFs 1.1–3.4, activities, completing-the-square material, quizzes and solutions, tests/reviews, and three final-exam versions with and without solutions.

### `math153.zip`
Contains a large screenshot sequence. These should be grouped by capture time and visually classified as exercise pages, assessment pages, solutions, or lecture material.

### Transcript-derived files
- `Algebra Help and Advice.txt`
- `Math Lecture Overview.txt`
- review transcript files

## Pipeline

1. Extract archives into a read-only `sources/` directory.
2. Compute SHA-256 for every source.
3. Create a manifest with type, probable chapter/section, and pairing information.
4. Pair assessment PDFs with solution PDFs by normalized filename.
5. Render PDF pages for visual inspection; do not rely only on extracted text.
6. Register screenshots in chronological groups.
7. Human-review each source item and assign question-family tags.
8. Create source-backed Markdown templates.

## Required provenance fields

- source_id
- file_name
- source_kind
- chapter
- section
- assessment_name
- question_number
- page
- solution_source_id
- visual_review_status
- extraction_status
- notes

## Conflict policy

When lecture, assessment, and solution disagree:

- preserve each statement;
- mark the conflict;
- do not silently repair it;
- use the official solution as grading authority only after explicit review.
