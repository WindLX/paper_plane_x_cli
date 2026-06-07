---
name: ppx-research-audit-iteration
description: Audit and iterate Paper Plane X compatible research artifacts, claims, diffs, experiments, literature syntheses, and drafts. Use when reviewing a research document, checking git changes, validating evidence, finding unsupported claims, comparing versions, archiving failed routes, or running reviewer-style cleanup passes.
---

# Research Audit and Iteration

## Purpose

Make research work safer to trust by checking what changed, whether claims are supported, whether conclusions still match evidence, and what should be revised or archived.

## Trigger

Use this skill for review requests, post-draft checks, result audits, configuration audits, evidence traceability checks, stale conclusion detection, git diff review, and cleanup after AI-generated work.

## Inputs

- Files or diffs to audit.
- Evidence locks, literature notes, experiment logs, configs, or prior versions.
- Review goal: correctness, traceability, writing quality, novelty, reproducibility, or consistency.
- Available tools: git, rg, file readers, subagents, validators.

## Paper Plane X Toolchain

- Pair with `ppx-researcher` when auditing Paper Plane X project files, librarian-derived claims, paper notes, or sync/upload decisions.
- Pair with `ppx-mineru-pdf-to-markdown` when auditing whether PDF-derived claims are supported by generated Markdown rather than guessed PDF content.
- In reviewer subagents, explicitly include `ppx-researcher` or `ppx-mineru-pdf-to-markdown` when those tools are needed for evidence checks.

## Workflow

1. Establish scope:
   - Current git state.
   - Target files.
   - Relevant prior locks or conclusions.
2. Inspect diffs before judging content when files were recently edited.
3. Check claims against evidence:
   - Supported.
   - Unsupported.
   - Overstated.
   - Contradicted.
   - Stale.
4. Check reproducibility:
   - Parameters and configs named.
   - Data/result provenance recorded.
   - Failed or rejected routes archived.
5. For broad audits, run independent reviewer passes when subagents are available:
   - Technical correctness.
   - Evidence traceability.
   - Writing clarity and concision.
6. Apply or recommend revisions with the smallest safe change.
7. Record important audit conclusions in local notes or locks.

## Human Gates

Ask the user before:

- Reverting or deleting prior work.
- Archiving a route as obsolete.
- Changing publication-level claims.
- Treating an audit finding as settled when evidence conflicts.

## Outputs

Review format:

```markdown
# Research Audit: [Artifact]

## Findings
## Unsupported or Overstated Claims
## Evidence Gaps
## Suggested Revisions
## Residual Risk
```

For code-review-style audits, lead with findings ordered by severity and include file/line references when available.

## Quality Checks

- Findings cite files, diffs, source notes, or locks.
- The audit separates bugs from preferences.
- Suggested fixes are scoped and actionable.
- Stale or rejected conclusions are preserved in archive rather than silently forgotten.
- The final state is clearer than the starting state.

## Failure Modes

- Reviewing prose without checking evidence.
- Using chat memory as the source of truth.
- Rewriting style while missing factual drift.
- Deleting old analysis instead of archiving it.
- Running reviewer subagents without clear scopes or output criteria.
