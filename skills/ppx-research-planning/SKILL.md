---
name: ppx-research-planning
description: Create structured, execution-ready Paper Plane X compatible research plans. Use whenever a user asks to plan a study, literature review, experiment campaign, proof strategy, paper section, proposal, survey, or multi-step academic investigation. The plan must define hypotheses, workflow, deliverables, quality standards, risks, and human decision points.
---

# Research Planning

## Purpose

Turn an ambiguous research request into an executable plan that preserves scientific intent, separates assumptions from facts, and defines what evidence will decide the question.

## Trigger

Use this skill before complex research execution, especially when the task has multiple routes, uncertain feasibility, literature dependence, experiments, or writing deliverables.

## Inputs

- Research question or desired artifact.
- Current project state: existing plans, notes, drafts, datasets, code, and constraints.
- Target audience: self, supervisor, coauthors, reviewers, grant panel, or implementation team.
- Available tools and evidence sources.

## Paper Plane X Toolchain

- Pair with `ppx-researcher` when the plan depends on Paper Plane X project files, literature library state, `ppx librarian` operations, or paper notes.
- Pair with `ppx-mineru-pdf-to-markdown` when the plan includes local PDF ingestion, scanned papers, formula/table-heavy documents, or PDF-to-Markdown preprocessing.
- In the plan, name these required skills explicitly under tools or workflow phases so the executor does not rediscover the toolchain.

## Workflow

1. Inspect first. Read relevant local files, prior conclusions, configs, and git state before asking questions.
2. State the task understanding in one paragraph: goal, audience, scope, and expected artifact.
3. Separate:
   - Known facts.
   - Working assumptions.
   - Open questions.
   - Out-of-scope items.
4. Define hypotheses or candidate routes. For each route, state what evidence would support, weaken, or falsify it.
5. Design the workflow in phases:
   - Evidence gathering.
   - Analysis or experiment.
   - Synthesis.
   - Locking.
   - Writing or delivery.
6. Define deliverables with filenames or artifact shapes when useful.
7. Add quality standards, risks, mitigation, and human gates.
8. Keep the plan decision-complete enough that another agent can execute it without inventing major choices.

## Human Gates

Ask the user to decide when:

- The research goal or acceptable claim strength is ambiguous.
- Multiple routes imply different scientific positioning.
- A plan would require changing experimental design, data collection, or publication scope.
- A deadline or expected artifact format materially changes the plan.

## Outputs

Use this compact structure:

```markdown
# [Research Plan Title]

## Task Understanding
## Known Facts and Assumptions
## Workflow
## Deliverables
## Quality Standards
## Risks and Human Gates
```

For small tasks, collapse sections but keep the same logic.

## Quality Checks

- The plan says what will be done, where outputs go, and how success is judged.
- Assumptions are labeled and do not masquerade as facts.
- Each phase has a concrete output.
- Human gates are few but meaningful.
- The plan avoids rerunning already rejected routes unless conditions changed.

## Failure Modes

- Asking before inspecting discoverable context: read files first.
- Creating a literature plan without search criteria or evidence fields.
- Creating an experiment plan without acceptance metrics.
- Creating a writing plan before facts are locked.
- Making the plan too generic to execute.
