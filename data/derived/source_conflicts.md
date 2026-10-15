# Source Conflicts and Provenance Gaps

Record disagreements, typos, uncertain transcription, solution inconsistencies, and unresolved provenance here. Do not silently resolve them.

| Conflict ID | Sources | Exact disagreement or gap | Possible interpretations | Current decision | Confidence | Reviewer | Date |
|---|---|---|---|---|---|---|---|
| GAP-001 | `TRANSCRIPT-CH5-LOGS`; repository tree | The seed family cited a transcript ID, but no transcript file or stable registry record is present. | The transcript may exist only in an unavailable archive, or the ID may be provisional. | Removed the unresolvable claim from runtime seed content; use explicit model-inference provenance until reviewed. | high that the file is absent; none on course content | Codex | 2026-08-06 |
| GAP-002 | Both source inventory text files; repository tree | Inventories list PDFs and screenshots, but the source binaries are absent and cannot be visually reviewed. | Assets may intentionally be stored outside Git or were not copied into this workspace. | Block claims of professor fidelity and label all four milestone constructions pending source review. | high | Codex | 2026-08-06 |
| GAP-003 | `data/derived/source_manifest.csv`; both filename inventories | The manifest can classify 222 unique filenames and infer obvious filename pairs, but every referenced binary is absent, so hashes, pages, topics, exact question text, and visual review cannot be supplied. | The files may exist only in the original archives or an external course-material store. | Preserve each record as `inventory_only`, `binary_present=false`; never use filename inference as mathematical/source verification. | high | Codex | 2026-08-07 |

## Integration reconciliation — 2026-10-15

GAP-001 through GAP-003 above describe the earlier inventory-only state. The PR subsequently
added a 53-file Markdown corpus and computed mappings. The restored root corpus now supplies
that evidence and its content hashes; the original PDFs/screenshots remain unavailable for
independent visual verification. Automated topic mapping and algebra validation do not establish
that every generated question preserves every professor method.

The nested rebuild and its report are retained as historical evidence. The root application,
canonical family Markdown, registry, authoring template, and tests are the active learning system.
The rebuild's replacement UI is not promoted because it omits original learning workflows.
