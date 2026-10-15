# Content Authoring

Family Markdown is canonical. Start from `templates/question_family_template.md`; include provenance, representation, hidden prerequisites, expected answer form, the decision path, errors, variation boundaries, and at least five progression layers. Runtime problems must include `source_refs`, `family_id`, `difficulty_layer`, `variant_reason`, final answer, and reasoning checkpoints.

Never use `MODEL-INFERENCE-PENDING-SOURCE-REVIEW` after a prompt has been source verified; replace it with stable registry IDs and record disagreements rather than silently reconciling them.
