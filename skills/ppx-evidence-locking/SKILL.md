---
name: ppx-evidence-locking
description: Create Paper Plane X compatible status locks and evidence locks for research projects. Use before paper writing, after major experiments, after literature route decisions, or whenever facts, parameters, results, rejected routes, assumptions, and open items must be frozen into a traceable ground-truth document.
---

# Evidence Locking

## Purpose

Create a durable checkpoint between exploration and downstream writing or decisions. A lock document records what is known, what is assumed, what is rejected, and what still needs verification.

## Trigger

Use this skill before drafting high-stakes claims, after completing experiments, after a literature synthesis, before coauthor review, before external upload, or when the user says to lock current status.

## Inputs

- Current analysis notes, plans, drafts, experiment results, configs, and literature outputs.
- Git state and recent diffs.
- Source paths, paper IDs, command outputs, logs, or data files supporting each claim.
- User decisions made during the research process.

## Paper Plane X Toolchain

- Pair with `ppx-researcher` when locked facts come from Paper Plane X project files, librarian results, paper IDs, deep-dive outputs, or paper notes.
- Pair with `ppx-mineru-pdf-to-markdown` when locked evidence comes from locally converted PDFs; record both the original PDF path and generated Markdown path.
- Keep locks local first. Use `ppx-researcher` to upload or write lock documents into Paper Plane X only after user confirmation.

## Workflow

1. Inspect current state:
   - `git status`.
   - Relevant diffs.
   - Existing lock files.
   - Latest analysis, result, and draft artifacts.
2. Group lock content:
   - Research objective and date.
   - Fixed facts and parameters.
   - Evidence-backed results.
   - Literature conclusions.
   - Rejected routes and reasons.
   - Design choices and rationale.
   - Open items.
3. For each important claim, record its support:
   - File path.
   - Command or tool.
   - Paper/source.
   - Human decision.
4. Label certainty:
   - Locked fact.
   - Working assumption.
   - Inference.
   - Pending verification.
5. Write locally first. Do not upload the lock to external systems without user confirmation.
6. Downstream writing should cite the lock rather than rediscovering facts from chat.

## Human Gates

Ask the user before:

- Marking a disputed or inferred claim as locked.
- Retiring a route as rejected.
- Locking final numbers for publication.
- Uploading the lock outside the local repository.

## Outputs

Recommended file names:

- `docs/locks/status-lock-YYYY-MM-DD.md`
- `docs/analysis/status-lock-YYYY-MM-DD.md` if the project already uses analysis locks.

Template:

```markdown
# Status Lock: [Project or Topic] ([Date])

## Scope
## Locked Facts
## Locked Results
## Literature Conclusions
## Rejected Routes
## Design Rationale
## Open Items
## Evidence Index
```

## Quality Checks

- Every locked claim has traceable support.
- Assumptions and inferences are visibly labeled.
- The lock records what changed since the previous lock when one exists.
- Open items are actionable, not vague worries.
- The document is usable as ground truth for writing.

## Failure Modes

- Locking conversation memory instead of files and sources.
- Mixing speculative narrative into fixed facts.
- Forgetting rejected routes, causing future agents to repeat them.
- Updating a lock without checking git diff.
- Uploading before the user confirms.
