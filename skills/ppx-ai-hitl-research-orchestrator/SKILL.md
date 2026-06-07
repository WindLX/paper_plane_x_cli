---
name: ppx-ai-hitl-research-orchestrator
description: Orchestrate Paper Plane X compatible AI + human-in-the-loop research workflows. Use whenever a user asks for a complex research project, literature survey, paper writing plan, experiment analysis, research audit, multi-agent investigation, or a reusable AI-assisted research process. This skill selects and combines ppx research planning, literature intelligence, delegation, evidence locking, writing, and audit skills.
---

# AI+HITL Research Orchestrator

## Purpose

Coordinate complex academic or technical research work so AI does the searchable, parallel, traceable work and the human makes direction-setting decisions. Treat conversation as coordination, but treat files as the durable research record.

## Trigger

Use this skill when the task involves more than one research phase, unclear scope, multiple evidence sources, paper drafting, literature review, experiment interpretation, or subagent delegation. For single-phase work, select the smallest relevant specialized skill.

## Inputs

- User goal, audience, deadline, and expected artifact.
- Current project files, if available.
- Known constraints, hypotheses, forbidden routes, or prior conclusions.
- Available tools: git, shell search, literature systems, PDF parsers, subagents, external knowledge bases.

## Paper Plane X Toolchain

Use this skill as the research workflow router, not as a replacement for tool-specific skills.

- Pair with `ppx-researcher` whenever the task needs Paper Plane X project context, `ppx` CLI commands, project files, librarian search/matrix/deep-dive, or paper-note operations.
- Pair with `ppx-mineru-pdf-to-markdown` whenever local PDFs need close reading, extraction, citation support, formula/table recovery, or conversion before upload.
- When delegating subagents, include these skill names explicitly in the child task if the child must use Paper Plane X or MinerU. Example: `skill: "ppx-researcher,ppx-literature-intelligence"`.

## Workflow

1. Classify the task:
   - Planning: use `ppx-research-planning`.
   - Literature discovery or paper analysis: use `ppx-literature-intelligence`.
   - Parallel investigation: use `ppx-parallel-research-delegation`.
   - Fact/parameter/result freeze: use `ppx-evidence-locking`.
   - Drafting or revision: use `ppx-research-writing`.
   - Review, regression check, or cleanup: use `ppx-research-audit-iteration`.
2. Select toolchain skills when needed:
   - Paper Plane X project/library work: add `ppx-researcher`.
   - Local PDF parsing: add `ppx-mineru-pdf-to-markdown`.
3. Ground in the environment before asking questions. Inspect relevant files, git state, existing plans, drafts, analysis notes, and available tools.
4. For complex tasks, create a short execution plan with phases, outputs, human gates, and quality checks.
5. Execute progressively: gather evidence, write local artifacts, lock conclusions, then draft or revise.
6. Keep external synchronization opt-in. Do not upload to paper notes, team systems, or shared knowledge bases until the user confirms.
7. Use git to track changes. Before modifying files, know what is already dirty and avoid overwriting unrelated user work.

## Human Gates

Ask the user before:

- Choosing between materially different research directions.
- Treating an uncertain claim as accepted ground truth.
- Uploading or syncing local outputs to external systems.
- Archiving, deleting, or replacing prior research conclusions.
- Making claims that affect publication positioning, novelty, ethics, safety, or experimental validity.

Do not ask for facts that can be discovered from local files, git, configs, or available research tools.

## Outputs

- A selected skill path or multi-skill workflow.
- Local research artifacts in conventional locations such as `docs/plans/`, `docs/literature/`, `docs/analysis/`, `docs/locks/`, `docs/drafts/`, or `docs/archive/`.
- Explicit open questions and decisions when human judgment is required.
- A concise final report: what changed, what evidence supports it, and what remains uncertain.

## Quality Checks

- The workflow has clear phase boundaries and deliverables.
- Every important conclusion is traceable to a file, source, command output, or locked assumption.
- AI-generated analysis distinguishes evidence from inference.
- Human decisions are recorded in the resulting artifact, not left only in chat.
- The final output can be picked up by another agent without needing hidden conversation context.

## Failure Modes

- Over-planning without reading the project first: inspect files before designing the workflow.
- Treating AI synthesis as evidence: cite sources, files, or experiments.
- Letting subagent output become ground truth without review: synthesize and audit it.
- Mixing project-specific tool instructions into general methods: keep reusable skills generic and tool-adaptive.
- Skipping the lock step before writing: for high-stakes claims, freeze facts before drafting.
