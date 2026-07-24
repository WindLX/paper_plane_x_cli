# Paper Plane X CLI

[![PyPI](https://img.shields.io/pypi/v/paper-plane-x-cli)](https://pypi.org/project/paper-plane-x-cli/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-AGPL--3.0--or--later-blue.svg)](LICENSE)

English | [中文](README.zh.md)

`ppx` is the JSON-first command-line client and external-agent integration package for [Paper Plane X](https://github.com/WindLX/paper_plane_x). It provides stable HTTP commands for project discovery, literature search, paper comparison, PDF parsing, project-file editing, and durable paper notes.

The package also ships two Agent Skills:

- `ppx-researcher`: evidence-driven literature research through a Paper Plane X project.
- `ppx-pdf-to-markdown`: local PDF conversion through the configured Paper Plane X parser.

Every remote command calls a running Paper Plane X Backend under `/api/v1`; the CLI never reads the backend database directly.

## Who should use it

- Researchers who prefer terminal and scriptable workflows.
- Automation that needs predictable JSON output and non-zero failure codes.
- Codex, Claude Code, Pi agent, and other Agent Skills-compatible tools.
- Developers integrating Paper Plane X into local research pipelines.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- A running Paper Plane X Backend for remote commands
- A project ID for project-scoped commands

## Installation

Install the released package from PyPI:

```bash
uv tool install paper-plane-x-cli
ppx --help
```

Upgrade or uninstall:

```bash
uv tool upgrade paper-plane-x-cli
uv tool uninstall paper-plane-x-cli
```

Install the current source checkout for development:

```bash
uv tool install .
```

## Quick start

Configure the backend and a default project:

```bash
ppx context set --base-url http://127.0.0.1:8000/api/v1
ppx context set --project-id prj_x
ppx context show
```

Explore and compare project papers:

```bash
ppx project global-finder
ppx librarian search \
  --query-expr "(meta.title CONTAINS transformer)" \
  --limit 20
ppx librarian matrix \
  --paper-ids pap_a,pap_b \
  --field-paths meta.title,quick_scan.quick_summary
ppx librarian deep-dive \
  --paper-id pap_a \
  --question "What is the core contribution?"
```

Persist a result in the project workspace:

```bash
ppx files upload --source ./comparison.md --path /notes/comparison.md
```

## Context resolution

`ppx` resolves configuration in this order:

1. command-line options: `--base-url`, `--project-id`;
2. environment variables named `PPX_<CONFIG_KEY>`, for example `PPX_BASE_URL` and `PPX_PROJECT_ID`;
3. local context: `./.paper-plane-x/context.json`;
4. global context: `~/.config/paper-plane-x/context.json`;
5. default base URL: `http://127.0.0.1:8000/api/v1`.

For context sources, the precedence is `ENV > local JSON > global JSON`. Local context is enabled by default, which is useful when each working directory maps to a different Paper Plane X project. Use `--global` only when saving shared defaults.

```bash
# Current directory (default)
ppx context set --base-url http://127.0.0.1:8000/api/v1
ppx context set --project-id prj_current

# Global defaults
ppx context set --global --base-url http://127.0.0.1:8000/api/v1
ppx context set --global --project-id prj_default

# Clear project_id from the local context
ppx context set --project-id null
```

`project_id` treats `none`, `null`, `None`, and `NULL` as explicit null values. With `context set`, they clear the key from the target JSON file; with the top-level `--project-id` option or `PPX_PROJECT_ID`, they disable the resolved project for that invocation.

For temporary or CI usage:

```bash
PPX_BASE_URL=http://127.0.0.1:8000/api/v1 \
PPX_PROJECT_ID=prj_x \
ppx project global-finder
```

Do not store secrets in context files. The CLI context contains server and project identifiers, not LLM API keys.

## Command groups

| Group            | Purpose                                                    |
| ---------------- | ---------------------------------------------------------- |
| `ppx context`    | Set and inspect global or local context                    |
| `ppx project`    | Project-level discovery                                    |
| `ppx librarian`  | Search, matrix comparison, and deep dive                   |
| `ppx pdf`        | Convert a local PDF to Markdown and images                 |
| `ppx paper`      | Download stored paper Markdown                             |
| `ppx paper-note` | Read, write, or delete durable paper notes                 |
| `ppx files`      | List, read, write, upload, patch, and delete project files |
| `ppx skills`     | Install or remove bundled Agent Skills                     |

Run `ppx <group> --help` for authoritative options.

## Project files

```bash
ppx files list --dir /
ppx files read --path /notes/idea.md
ppx files lines --path /draft.md --start-line 1 --end-line 40
ppx files find --path /draft.md --query "Related Work"
ppx files write --path /notes/idea.md --content "# Idea"
ppx files upload --source ./idea.md --path /notes/idea.md
ppx files patch \
  --path /draft.md \
  --action insert_after \
  --anchor-text "## Related Work" \
  --content "..."
ppx files delete --path /notes/obsolete.md
```

Project files are sandboxed by the backend: path traversal is rejected, only approved text/data extensions are accepted, and uploads are limited to 10 MB per file.

Prefer targeted `find`, `lines`, `replace-*`, or `patch` operations when an Agent modifies an existing document. This reduces accidental overwrites and makes failures explicit.

## Paper Markdown and notes

Download the parsed Markdown stored for a paper:

```bash
ppx paper markdown --paper-id pap_x --save-dir ./paper-markdown
```

The default filename is `<paper-id>.md`; override it with `--output-md-name`.

Maintain a durable paper note:

```bash
ppx paper-note get --paper-id pap_x
ppx paper-note write --paper-id pap_x --content "Stable research note"
ppx paper-note delete --paper-id pap_x
```

Use paper notes for stable conclusions about one paper. Use project files for cross-paper synthesis, matrices, plans, and drafts.

## PDF to Markdown

```bash
ppx pdf parse --source ./paper.pdf --save-dir ./paper-pdf
```

The command uploads the PDF to the configured backend parser, writes Markdown and referenced images, prunes unreferenced images, and prints a JSON summary:

```json
{
  "md_path": "paper-pdf/paper.md",
  "image_paths": ["paper-pdf/images/fig1.png"],
  "parser_type": "local_mineru"
}
```

Parser choice and credentials are managed by the backend Settings, not by the CLI.

## Agent Skills

Bundled skills:

```text
skills/ppx-researcher/SKILL.md
skills/ppx-pdf-to-markdown/SKILL.md
```

List and install them:

```bash
ppx skills list
ppx skills install
```

The default target is `${CODEX_HOME:-~/.codex}/skills`. Use an explicit target for other tools:

| Tool or scope                  | Command                                              |
| ------------------------------ | ---------------------------------------------------- |
| Codex default                  | `ppx skills install`                                 |
| Generic Agent Skills directory | `ppx skills install --target-dir ~/.agents/skills`   |
| Pi agent                       | `ppx skills install --target-dir ~/.pi/agent/skills` |
| Claude Code user scope         | `ppx skills install --target-dir ~/.claude/skills`   |
| Claude Code project scope      | `ppx skills install --target-dir ./.claude/skills`   |

Existing bundled skill directories are skipped unless `--force` is provided. `uninstall` removes only the bundled `ppx-*` skill names:

```bash
ppx skills uninstall
ppx skills uninstall --target-dir ~/.agents/skills
```

Restart the Agent application or open a new session after installation.

## Output and automation contract

- Successful remote commands print JSON to stdout.
- HTTP, context, and validation failures print structured JSON to stderr.
- Failures return a non-zero exit code.
- Download commands write files only to the requested local directory.
- The CLI does not log or persist backend LLM credentials.

Scripts should parse JSON rather than human-readable terminal formatting.

## Development

```bash
git clone https://github.com/WindLX/paper_plane_x_cli.git
cd paper_plane_x_cli
uv sync
uv run ppx --help
```

Quality checks:

```bash
just lint
just format-check
just typecheck
just test
just build
just pre-commit
```

Equivalent uv commands:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pyright
uv run pytest
uv build
```

## Contributing and pull requests

1. Create a focused branch from the latest `main`.
2. Preserve JSON output compatibility unless the change explicitly introduces a breaking contract.
3. Add tests for command parsing, context precedence, request payloads, and file output.
4. Update both `README.md` and `README.zh.md` for user-visible changes.
5. Update bundled Skill instructions when the workflow or CLI contract changes.
6. Run `just pre-commit` before opening a PR.

PR descriptions should include motivation, affected commands, compatibility impact, and verification commands. Never include API keys, private paper content, or local context files in issues or test fixtures.

Report problems at [GitHub Issues](https://github.com/WindLX/paper_plane_x_cli/issues).

## Release

The CLI version is managed by the Paper Plane X monorepo `VERSION` file. A top-level `vX.Y.Z` release builds the wheel and source distribution and publishes them to PyPI through GitHub Actions Trusted Publishing.

Do not bump the CLI version independently; use the monorepo release process.

## License

Paper Plane X CLI is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE).
