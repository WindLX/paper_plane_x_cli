---
name: ppx-researcher
description: Use Paper Plane X as a project-scoped academic research assistant through the ppx HTTP CLI. Use for project literature search, paper comparison, single-paper deep dives, full parsed Markdown retrieval, research synthesis, project notes, drafts, and paper-level AI notes.
---

# Paper Plane X Researcher

Use this skill when the user asks you to work inside a Paper Plane X research project: inspect project papers, search or compare literature, deep-dive a paper, synthesize findings, continue notes/drafts, or maintain paper-level AI notes.

Paper Plane X access is through the `ppx` CLI only. Do not call imagined same-name tools.

## Start Here

For any project-scoped task, run:

```bash
ppx context show
```

If no `project_id` is available from flags, environment, local context, or global context, ask the user for it. Do not invent a `project_id`. After the user provides one, either set local context:

```bash
ppx context set --local --project-id <project_id>
```

or pass `--project-id <project_id>` on subsequent commands.

Read `references/tool-guide.md` when you need exact CLI syntax, query rules, file editing commands, matrix field paths, or examples.

## Operating Principles

- Use evidence for project-paper facts. Search, matrix, deep-dive, project files, or paper notes before making claims about papers.
- Keep command chains minimal but sufficient. Each `ppx` call should answer a specific question.
- Prefer structured fields via `ppx librarian matrix` before deep-diving; use `deep-dive` for focused questions that structured reports do not answer.
- Download a paper's parsed Markdown when the task needs its complete original text rather than selected structured fields or a focused deep-dive answer.
- For reusable outputs, consider saving or updating project files or paper notes instead of leaving long-lived work only in chat.
- Preserve existing project documents. Inspect before editing, prefer local edits, and avoid whole-file overwrite unless the file is intentionally being regenerated.
- If a command fails or returns JSON `error`, treat it as failed evidence. Re-check context, path, query syntax, or current file contents before retrying.

## Task Routing

### Direct Answer

If the user asks a conceptual question that does not depend on project-specific papers or files, answer directly. If project evidence would materially change the answer, say so and fetch it.

### Literature Search

Use `ppx librarian search` when the user has keywords, topics, years, titles, venues, or field conditions. If search returns nothing, retry once with a simpler or broader query before concluding nothing was found.

Use `ppx project global-finder` when the user wants a project-wide overview, when you need to discover what is in the library, or when keyword search is too narrow.

### Paper Comparison or Review

Use `ppx librarian matrix` to compare multiple papers or extract structured fields. Choose narrow `--field-paths` first; request broad roots only when the task truly needs full reports.

For unclear mechanisms, equations, experiments, or claims in one important paper, use `ppx librarian deep-dive --paper-id ... --question ...`.

### Single-Paper Notes

Use `ppx paper-note get` before relying on or replacing an existing AI note. Use `ppx paper-note write` for stable, reusable conclusions about one paper.

### Full Paper Text

Use `ppx paper markdown --paper-id <paper_id> --save-dir <directory>` when the user needs the complete parsed Markdown or when close reading requires the full source text. Read the returned `md_path`; do not reparse a local PDF when the paper already exists in Paper Plane X.

Full paper Markdown is usually long. When sub-agent or delegation tools are available, prefer assigning focused sections or questions to sub-agents and synthesize their evidence-backed findings. Otherwise, inspect the file in targeted chunks instead of loading the whole document into context at once.

### Project Files and Drafts

Before writing or continuing drafts, inspect existing files with `ppx files list`, `read`, `lines`, or `find`. Use line, anchor, or exact-text edits when possible. Use `write` only for new files or intentional full regeneration.

## Common Workflows

### Answer a Research Question

1. Decide whether current context is enough.
2. If not, search papers, inspect files, or read notes.
3. Use matrix for structured evidence; deep-dive only for focused gaps.
4. Answer with the conclusion first, then the evidence and uncertainty.

### Write or Continue a Draft

1. Inspect project files and any existing draft.
2. Gather paper evidence if the draft depends on literature claims.
3. Produce clean Markdown that can be saved directly.
4. Save or update the project file when the user requested persistence or the result is clearly reusable.

### Compare Papers

1. Clarify or infer comparison dimensions.
2. Use matrix with field paths matching those dimensions.
3. Deep-dive only for missing high-value details.
4. Present a short verdict plus dimension-by-dimension comparison.

## Output Rules

- Be concise, professional, and useful for project progress.
- Cite only papers actually inspected in this turn or already present in trusted context.
- When citing project papers, use wiki links: `[[paper_id | short_title]]`.
- State uncertainty when evidence is incomplete, and name the next command or source that would reduce it.
- Do not fabricate paper details, IDs, citations, or project file contents.
