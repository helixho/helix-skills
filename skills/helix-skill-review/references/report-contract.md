# Evaluation report contract

`scripts/run.py` accepts one JSON object on stdin and emits one JSON result.
First call `{"command":"validate","skill_dir":"/path/to/demo-skill"}`.
Keep its `result.content_hash` before reading the listed files. After review,
submit the following shape, replacing the sample evidence, judgments and scores
with your actual review. The nine score names must match the built-in rubric.

```json
{
  "command": "evaluate",
  "source_project": "example-project",
  "skill_unit": "skills/demo-skill",
  "skill_dir": "/path/to/demo-skill",
  "expected_content_hash": "<hash returned by validate before review>",
  "scores": {
    "Value and fit": 4,
    "Structure maturity": 3,
    "Uniqueness": 4,
    "Maintainability": 3,
    "Portability and configuration": 4,
    "Trust boundary": 4,
    "Trigger quality": 4,
    "Actionability": 3,
    "Evidence quality": 4
  },
  "evidence": [
    {"id":"E1", "kind":"file-backed", "source":"SKILL.md", "line":12,
     "detail":"The workflow promises an output but gives no completion condition."}
  ],
  "findings": [
    {"id":"F1", "detail":"Completion cannot be determined from this workflow.", "evidence_ids":["E1"]}
  ],
  "suggestions": [
    {"detail":"Define the expected artifact and how to inspect it.", "finding_ids":["F1"]}
  ]
}
```

Evidence is nonempty; each item has a unique `id`, `kind`, `source` and `detail`.
Kinds and their meaning are defined in `review-guide.md`. For `file-backed`,
`source` is a file relative to `skill_dir` (or an explicit absolute path) and
`line` is a positive, existing line number. Only the skill directory is covered
by `expected_content_hash`; separately recheck cited files outside it before
delivery. For `external-backed`, `source` is a direct HTTP(S) URL; `detail`
records the actual supporting information and retrieval date where relevant.
For `check-backed`, include command, inspected object and observed result in
`detail`, with the result location or command as `source`. For other kinds,
`source` identifies the user context, reasoning basis or missing material.

Findings have unique IDs, a `detail` explaining the issue and its location or
gap, and nonempty `evidence_ids`. Each finding needs at least one linked
suggestion; a request for evidence or a user decision can be that suggestion.
With no findings, both lists may be empty. The final prose can recommend retention.

The program checks these structures, local citation locations, URL shape,
score dimensions and source drift. AI checks whether evidence actually supports
findings, external sources are authoritative and current, findings are complete,
and recommendations fit the user's goals. `ok: true` is not semantic approval.
Keep final prose readable; this JSON is the evaluation interface, not a mandatory
user-facing report format. Identify automatic, AI, human and unverified results
separately and never invent checks or confirmations.
