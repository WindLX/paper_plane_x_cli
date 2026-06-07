---
name: ppx-research-writing
description: Write and revise Paper Plane X compatible academic research artifacts from locked evidence. Use for paper sections, related work, methodology, experiment analysis, proposals, rebuttals, technical reports, and survey prose. Emphasizes citation-backed claims, local drafts, section briefs, evidence locks, and iterative human review.
---

# Research Writing

## Purpose

Produce research prose that is useful, defensible, and traceable. Write from locked evidence and source-backed notes rather than from conversation memory.

## Trigger

Use this skill when the user asks for a paper draft, section rewrite, related work, method description, experiment narrative, proposal, report, rebuttal, or polishing pass.

## Inputs

- Writing goal and target venue or audience.
- Locked facts, literature synthesis, experiment results, and prior drafts.
- Required tone, length, claim strength, and citation style.
- Files to edit or create.

## Paper Plane X Toolchain

- Pair with `ppx-researcher` when drafting from Paper Plane X project files, librarian evidence, paper notes, or when writing drafts back into the project sandbox.
- Pair with `ppx-mineru-pdf-to-markdown` when the draft needs claims grounded in local PDFs that have not yet been converted to Markdown.
- Prefer writing from local locks and notes first; use `ppx-researcher` for external project-note sync only after the user confirms.

## Workflow

1. Locate ground truth:
   - Evidence locks.
   - Literature matrices or deep-dives.
   - Experiment notes and results.
   - Existing draft sections.
2. If facts are not locked and claims are high-stakes, create or request an evidence lock first.
3. Write a section brief:
   - Purpose of the section.
   - Claims to make.
   - Evidence for each claim.
   - Claims to avoid.
4. Draft locally in the requested file or a draft file.
5. Use citations or source references where the project supports them.
6. Keep AI-generated prose subordinate to evidence. Do not inflate novelty, certainty, or generality.
7. After drafting, run an audit pass for unsupported claims, contradictions, verbosity, and missing transitions.

## Human Gates

Ask the user before:

- Choosing a strong claim over a conservative one.
- Reframing the paper's novelty or main contribution.
- Removing a coauthor's existing prose.
- Submitting, uploading, or syncing drafts externally.

## Outputs

For section planning:

```markdown
# Writing Brief: [Section]

## Section Purpose
## Claims and Evidence
## Structure
## Avoided Claims
## Open Questions
```

For draft work, produce edited prose plus a short change note naming the evidence used.

## Quality Checks

- Major claims are grounded in locked facts or cited sources.
- The prose distinguishes theory, empirical evidence, and design rationale.
- The section has a clear role in the larger paper.
- No project-specific numbers or citations are invented.
- The draft is concise enough for human revision.

## Failure Modes

- Writing before evidence is locked.
- Turning limitations into claims of generality.
- Creating plausible but uncited related work.
- Over-polishing away technical precision.
- Leaving important decisions hidden in chat.
