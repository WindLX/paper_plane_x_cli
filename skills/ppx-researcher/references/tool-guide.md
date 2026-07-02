# Paper Plane X CLI Tool Guide

`ppx` is the HTTP bridge from external agents to Paper Plane X. It calls FastAPI endpoints and prints JSON.

## Contents

- Context
- Project files
- Paper notes
- Librarian commands
- Query rules
- Matrix field paths
- File editing examples
- Output handling

## Context

```bash
ppx context set --base-url http://127.0.0.1:8000/api/v1 --project-id prj_x
ppx context set --local --project-id prj_y
ppx context show
```

Context precedence:

1. Command flags: `--base-url`, `--project-id`
2. Environment variables: `PPX_BASE_URL`, `PPX_PROJECT_ID`
3. Local context: `./.paper-plane-x/context.json`
4. Global context: `~/.config/paper-plane-x/context.json`
5. Default base URL: `http://127.0.0.1:8000/api/v1`

Run `ppx context show` before project-scoped work. Most project file and librarian commands require `project_id`.

## Project Files

| Researcher action     | CLI command                                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------------------- |
| List files            | `ppx files list --dir /`                                                                              |
| Read whole file       | `ppx files read --path /notes/idea.md`                                                                |
| Read line range       | `ppx files lines --path /draft.md --start-line 10 --end-line 20`                                      |
| Find text             | `ppx files find --path /draft.md --query "Related Work"`                                              |
| Write/overwrite file  | `ppx files write --path /notes/summary.md --content "..."`                                            |
| Upload local file     | `ppx files upload --source ./summary.md --path /notes/summary.md`                                     |
| Replace line range    | `ppx files replace-lines --path /draft.md --start-line 4 --end-line 6 --new-text "..."`               |
| Replace exact text    | `ppx files replace-text --path /draft.md --old-text "..." --new-text "..."`                           |
| Anchor patch          | `ppx files patch --path /draft.md --action insert_after --anchor-text "## Methods\n" --content "..."` |
| Delete file/empty dir | `ppx files delete --path /tmp/old.md`                                                                 |

File editing rules:

- Inspect before editing: use `list`, `read`, `lines`, or `find`.
- Prefer the smallest reliable edit: `replace-lines` for known line ranges, `replace-text` for unique fixed text, `patch` for anchor-based edits.
- Use `write` only for new files or intentional full-file regeneration.
- Use `upload` when a local file already exists; do not paste large local files into `write`.
- `replace-text` and `patch` support `--expected-occurrences`; use it for safety. `replace-text` also supports `--replace-all`.
- If an edit command fails because line numbers, matches, or paths changed, re-read or re-find before retrying.
- Line numbers are 1-based, and `end_line` is inclusive.
- Project files must stay inside the sandbox and use one of: `.csv`, `.json`, `.md`, `.txt`, `.yaml`, `.yml`, `.toml`.
- Single-file size limit is 10485760 bytes.

## Paper Notes

| Researcher action | CLI command                                          |
| ----------------- | ---------------------------------------------------- |
| Read note         | `ppx paper-note get --paper-id p1`                   |
| Write/update note | `ppx paper-note write --paper-id p1 --content "..."` |
| Delete note       | `ppx paper-note delete --paper-id p1`                |

Paper notes are for stable, reusable conclusions about one paper. Read existing notes before overwriting.

## Librarian Commands

| Researcher action | CLI command                                                                                             |
| ----------------- | ------------------------------------------------------------------------------------------------------- |
| Project overview  | `ppx project global-finder`                                                                             |
| Search papers     | `ppx librarian search --query-expr "(meta.title CONTAINS transformer)" --limit 20`                      |
| Matrix fields     | `ppx librarian matrix --paper-ids p1,p2 --field-paths quick_scan,synthesis_data.methodology.innovation` |
| Deep dive         | `ppx librarian deep-dive --paper-id p1 --question "What is the main control objective?" --timeout 240`  |

Selection guide:

- Use `search` to find candidate `paper_id`s by topic, keyword, title, venue, year, or structured field condition.
- Use `global-finder` for project-wide browsing or when you do not yet know useful keywords.
- Use `matrix` for multi-paper comparison and structured extraction. Prefer specific field paths.
- Use `deep-dive` for focused single-paper questions that cannot be answered from structured fields. You can set timeout parameters to replace the default value (=240).

If `search` returns no results, retry once with fewer conditions, broader fields, or synonyms. If `global-finder` shows no relevant candidates, tell the user what was tried.

## Query Rules

Examples:

```bash
ppx librarian search --query-expr "(meta.title CONTAINS transformer)"
ppx librarian search --query-expr "(md_content CONTAINS lyapunov)"
ppx librarian search --query-expr "(meta.year BETWEEN [2020, 2025]) AND (quick_scan.verdict CONTAINS 推荐)"
ppx librarian search --query-expr "(meta.title CONTAINS \"deep learning\") OR (meta.publication CONTAINS NeurIPS)"
```

Rules:

- Use parentheses around conditions.
- Combine conditions with `AND` and `OR`.
- Use `CONTAINS` for text fields.
- Use `BETWEEN [start, end]` for `year` or `meta.year`.
- Quote values with spaces or special characters.
- Search filters out papers with failed extraction or failed fact check status.

## Matrix Field Paths

Use dot notation for `--field-paths`. Use `[0]` for array items. Prefer narrow paths over broad roots unless the task needs full reports.

Examples:

```bash
ppx librarian matrix --paper-ids p1,p2 --field-paths meta,quick_scan
ppx librarian matrix --paper-ids p1,p2 --field-paths quick_scan.verdict,quick_scan.tags
ppx librarian matrix --paper-ids p1,p2 --field-paths synthesis_data.methodology.innovation,analysis_report.core_formulation.objective_function
```

Common roots:

- `md_content`: original Markdown full text.
- `meta`: title, authors, year, publication, DOI, raw PDF info, custom metadata.
- `quick_scan`: tags, verdict, reason, short summary.
- `synthesis_data`: research gap, methodology, key results, review summary.
- `analysis_report`: prerequisites, core formulation, derivation steps, related references.

Compact schema:

```ts
type CitationText = {
  text: string;
  citations: Array<{ quote: string; source_header: string }>;
};

type PaperMatrixFields = {
  md_content: string;
  meta: {
    title: string;
    authors: string[];
    year: number;
    publication: string;
    doi: string;
    raw_pdf_path: string;
    raw_pdf_sha256: string;
    custom_meta: Record<string, unknown>;
  };
  quick_scan: {
    tags: string[];
    verdict: string;
    reason: string;
    quick_summary: string;
  };
  synthesis_data: {
    research_gap: {
      context: CitationText;
      existing_limit: CitationText;
      motivation: CitationText;
    };
    methodology: {
      approach_name: string;
      core_logic: CitationText;
      innovation: CitationText;
      disadvantage: CitationText;
      future_direction: CitationText;
    };
    key_results: {
      dataset_env: CitationText;
      baseline: CitationText;
      performance: CitationText;
    };
    review_summary: CitationText;
  };
  analysis_report: {
    prerequisites: Array<{
      concept_name: string;
      brief_explanation: string;
      relevance_to_paper: CitationText;
    }>;
    core_formulation: {
      problem_definition: CitationText;
      objective_function: CitationText;
      algorithm_flow: CitationText;
    };
    derivation_steps: Array<{
      step_order: number;
      step_name: string;
      detail_explanation: CitationText;
    }>;
    related_references: Array<{ title: string; reason: string }>;
  };
};
```

Useful paths:

- `meta.title`
- `quick_scan.tags[0]`
- `synthesis_data.methodology.innovation.text`
- `analysis_report.prerequisites[0].concept_name`
- `analysis_report.core_formulation.objective_function.text`
- `analysis_report.derivation_steps[0].detail_explanation.text`

## File Editing Examples

Inspect before editing:

```bash
ppx files list --dir /
ppx files find --path /draft.md --query "Related Work"
ppx files lines --path /draft.md --start-line 20 --end-line 40
```

Small line edit:

```bash
ppx files replace-lines --path /draft.md --start-line 24 --end-line 29 --new-text "new paragraph"
```

Anchor edit:

```bash
ppx files patch --path /draft.md --action insert_after --anchor-text "## Related Work\n" --content "new content\n"
```

Whole-file write, only when intended:

```bash
ppx files write --path /notes/lit-review.md --content "# Literature Review\n..."
```

Upload a local file into the project sandbox:

```bash
ppx files upload --source ./lit-review.md --path /notes/lit-review.md
```

If `--path` is omitted, upload targets `/<source filename>`.

## Output Handling

- Every command prints JSON.
- Treat non-zero exit status or JSON `error` as a failed tool call.
- Do not infer missing paper facts from filenames, titles, or memory; fetch evidence with librarian tools.
