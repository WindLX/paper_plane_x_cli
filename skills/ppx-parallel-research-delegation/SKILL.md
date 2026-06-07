---
name: ppx-parallel-research-delegation
description: Design and manage Paper Plane X compatible parallel subagent research tasks. Use whenever a research problem can be split by paper group, hypothesis, method family, dataset, experiment, code module, review angle, or independent validation pass. Produces concrete task briefs, output formats, review criteria, and synthesis rules for subagents or delegated AI workers.
---

# Parallel Research Delegation

## Purpose

Use multiple agents as a controlled research team: each worker gets a narrow evidence task, writes an auditable output, and the parent synthesizes rather than blindly accepts.

## Trigger

Use this skill when the task benefits from independent exploration, parallel paper deep-dives, competing routes, code/config audits, reviewer passes, or validation by fresh context.

## Inputs

- Parent research goal.
- Candidate task partitions: papers, routes, questions, datasets, modules, or review perspectives.
- Available agent types, tools, skills, permissions, and output locations.
- Constraints on read/write access and external systems.

## Workflow

1. Decide whether delegation is justified. Use it when parallelism reduces uncertainty or improves independence.
2. Partition by independent evidence units:
   - Paper group.
   - Hypothesis or route.
   - Experiment scenario.
   - Code subsystem.
   - Review lens.
3. For each subagent, write a task brief with:
   - Goal.
   - Inputs and source paths or IDs.
   - Required tools/skills.
   - Read/write permissions.
   - Exact output path or return format.
   - Quality criteria.
   - Things not to do.
4. Keep child tasks narrow. Do not ask child agents to own orchestration unless explicitly intended.
5. Run parallel tasks with bounded concurrency.
6. After completion, synthesize:
   - Agreements.
   - Conflicts.
   - Evidence strength.
   - Missing checks.
   - Recommended conclusion.
7. Audit subagent outputs before locking or writing.

## Human Gates

Ask the user before:

- Delegating tasks that may write to important project files.
- Using external paid, private, or rate-limited systems.
- Treating conflicting subagent conclusions as resolved.
- Launching a large or long-running fanout.

## Outputs

Task brief template:

```markdown
## Subagent: [Name]

Goal:
Sources:
Tools/Skills:
Permissions:
Required Output:
Quality Criteria:
Do Not:
```

Synthesis template:

```markdown
# Parallel Research Synthesis

## Task Map
## Agreements
## Conflicts
## Evidence Assessment
## Decision or Next Step
```

## Quality Checks

- Each child task has enough context to act without reading the parent conversation.
- Outputs are file-backed or schema-like enough to compare.
- Permissions are explicit, especially read-only repositories or external systems.
- Parent synthesis cites child outputs and resolves conflicts.
- No child result becomes ground truth without review.

## Failure Modes

- Vague task briefs that produce essays instead of evidence.
- Missing tools or skills in the child configuration.
- Asking every child the same broad question.
- Letting children overwrite shared files.
- Combining outputs without checking contradictions.
