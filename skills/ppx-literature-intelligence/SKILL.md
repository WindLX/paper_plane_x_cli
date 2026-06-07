---
name: ppx-literature-intelligence
description: Perform Paper Plane X compatible literature discovery, screening, comparison, deep reading, and evidence extraction for academic research. Use whenever the user asks for paper search, survey writing, related work, method comparison, theorem extraction, citation-backed claims, or analysis across ppx, Zotero, Semantic Scholar, local PDFs, Markdown notes, or other literature sources.
---

# Literature Intelligence

## Purpose

Convert scattered papers into structured, source-grounded research intelligence: what each paper claims, how it proves or tests it, what assumptions it needs, and how it applies to the user's question.

## Trigger

Use this skill for literature searches, annotated bibliographies, paper matrices, deep-dives, related work sections, method comparisons, and citation-backed technical claims.

## Inputs

- Research question and target claim.
- Known papers, paper IDs, PDFs, notes, or search terms.
- Available literature tools: ppx, Zotero, Semantic Scholar, Google Scholar, local Markdown/PDF parsers.
- Required output: shortlist, matrix, deep-dive report, synthesis, or draft prose.

## Workflow

1. Define the evidence need:
   - Background mapping.
   - Method extraction.
   - Theorem/proof assumptions.
   - Experiment/result comparison.
   - Citation support for writing.
2. Search broadly enough to avoid tunnel vision, then screen using explicit criteria.
3. Build a compact matrix before deep reading when comparing multiple papers.
4. Deep-dive only the papers that can materially affect the conclusion.
5. Extract evidence in structured fields:
   - Bibliographic identity.
   - Problem setting.
   - Method.
   - Assumptions.
   - Claims/results.
   - Limitations.
   - Relevance to the current research question.
6. Separate direct evidence from interpretation. Mark inferences clearly.
7. Save reusable outputs locally before syncing to external paper notes or databases.

## Human Gates

Ask the user before:

- Declaring a literature route exhausted.
- Excluding a major paper family for scope reasons.
- Promoting a paper's claim into the user's own paper narrative.
- Uploading local summaries into an external literature system.

## Outputs

For a multi-paper comparison:

```markdown
# Literature Intelligence: [Topic]

## Search Scope
## Screening Criteria
## Paper Matrix
## Deep-Dive Findings
## Synthesis
## Open Questions
```

For a single-paper deep dive:

```markdown
# Deep Dive: [Paper]

## Why This Paper Matters
## Method and Assumptions
## Key Claims and Evidence
## Transferability
## Limitations
## Usable Citations or Notes
```

## Quality Checks

- Important claims have paper-level support.
- The synthesis does not overstate what the literature proves.
- Negative findings include the missing assumption, incompatible setting, or failed transfer condition.
- Search terms, paper IDs, or source paths are recorded.
- The output can support writing without another search pass.

## Failure Modes

- Reading only abstracts for technical claims.
- Treating one paper as a field consensus.
- Losing source identity while summarizing.
- Extracting quotes without explaining their relevance.
- Binding the workflow to one literature tool when another source is available.
