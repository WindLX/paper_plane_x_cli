# Paper Plane X CLI

English | [中文](README.zh.md)

Standalone HTTP CLI and external-agent skills for Paper Plane X.

This package contains:

- `ppx`: a JSON-first CLI that talks to a running Paper Plane X FastAPI server.
- `skills/ppx-researcher`: the Researcher skill for Codex, Claude Code, Pi agents, and other agent tools.
- `skills/ppx-pdf-to-markdown`: a PDF-to-Markdown workflow skill backed by the Paper Plane X API.

All commands call HTTP endpoints under `/api/v1` on a running Paper Plane X server.

## Install

The CLI uses [uv](https://docs.astral.sh/uv/) for installation and upgrades:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For released versions, install from PyPI:

```bash
uv tool install paper-plane-x-cli
```

Upgrade:

```bash
uv tool upgrade paper-plane-x-cli
```

Uninstall the CLI:

```bash
uv tool uninstall paper-plane-x-cli
```

For local development, or before the package is published to PyPI, install from the CLI directory:

```bash
uv tool install .
```

After `uv tool install`, use `ppx` directly.

## Context

`ppx` resolves context in this order:

1. command line options: `--base-url`, `--project-id`
2. environment variables: `PPX_BASE_URL`, `PPX_PROJECT_ID`
3. local context file: `./.paper-plane-x/context.json` (in the current working directory)
4. global context file: `~/.config/paper-plane-x/context.json`
5. default base URL: `http://127.0.0.1:8000/api/v1`

The local context overrides the global context. This allows per-project settings without changing your global defaults.

```bash
# Global context (default)
ppx context set --base-url http://127.0.0.1:8000/api/v1
ppx context set --project-id prj_x

# Local context (current directory only)
ppx context set --local --project-id prj_y

ppx context show
```

## Common Commands

```bash
ppx project global-finder
ppx librarian search --query-expr "(meta.title CONTAINS transformer)" --limit 20
ppx librarian matrix --paper-ids p1,p2 --field-paths quick_scan,synthesis_data.methodology.innovation
ppx librarian deep-dive --paper-id p1 --question "What is the core contribution?"

ppx paper markdown --paper-id p1 --save-dir ./paper-markdown

ppx files list --dir /
ppx files read --path /notes/idea.md
ppx files upload --source ./idea.md --path /notes/idea.md
ppx files find --path /draft.md --query "Related Work"
ppx files patch --path /draft.md --action insert_after --anchor-text "## Related Work" --content "..."

ppx paper-note get --paper-id p1
ppx paper-note write --paper-id p1 --content "..."
ppx paper-note delete --paper-id p1
```

All tool commands print JSON to stdout. HTTP and validation failures print structured JSON to stderr and exit non-zero.

`files upload` uses the same sandbox rules as project files: allowed text/data extensions only, no path traversal, and a 10MB per-file limit.

`paper markdown` downloads the paper's stored parsed Markdown. The output filename
defaults to `<paper-id>.md`; use `--output-md-name full-paper.md` to override it.

## PDF Parsing

Use the PDF parser when an external agent needs to read or process a local PDF as Markdown:

```bash
ppx pdf parse --source ./paper.pdf --save-dir ./paper-pdf
```

The command sends the PDF to the Paper Plane X API, writes Markdown plus referenced images, and prints JSON:

```json
{
  "md_path": "paper-pdf/paper.md",
  "image_paths": ["paper-pdf/images/fig1.png"],
  "parser_type": "local_mineru"
}
```

## Skill

Bundled skills live under `skills/`:

```text
skills/ppx-researcher/SKILL.md
skills/ppx-pdf-to-markdown/SKILL.md
```

Use `ppx-researcher` when an external agent should follow the same research workflow as Paper Plane X: verify project context, search and compare papers through `ppx`, write durable results into project files or paper notes, and cite only evidence actually fetched through the CLI/API.

Use `ppx-pdf-to-markdown` when an external agent encounters local PDFs and should convert them to Markdown before reading, summarizing, extracting, or uploading the result.

For Codex, the default target is `${CODEX_HOME:-~/.codex}/skills`, which is Codex's default user skill directory:

```bash
ppx skills list
ppx skills install
ppx skills install --force
ppx skills uninstall
```

After installation, restart Codex or open a new session to make `ppx-researcher` and `ppx-pdf-to-markdown` available.

You can also pass an explicit target directory for the agent you use:

| Tool / scope | Install command | Notes |
| --- | --- | --- |
| Codex default | `ppx skills install` | Installs into `${CODEX_HOME:-~/.codex}/skills` |
| Generic Agent Skills / compatibility path | `ppx skills install --target-dir ~/.agents/skills` | Useful for Codex/agent setups that already read from `~/.agents/skills` |
| Pi agent | `ppx skills install --target-dir ~/.pi/agent/skills` | Uses the Pi agent skill directory |
| Claude Code user scope | `ppx skills install --target-dir ~/.claude/skills` | Available to Claude Code sessions for the current user |
| Claude Code project scope | `ppx skills install --target-dir ./.claude/skills` | Checked into a repository when the team should share the skills |

```bash
ppx skills install --target-dir ~/.agents/skills
ppx skills install --target-dir ~/.pi/agent/skills
ppx skills install --target-dir ~/.claude/skills
ppx skills install --target-dir ./.claude/skills
```

`install` copies every bundled `ppx-*` skill into the target directory. Existing skill directories are skipped unless `--force` is passed. `uninstall` removes only the bundled `ppx-*` skill names, leaving unrelated skills in the target directory alone.

To fully remove both the CLI and installed skills, uninstall skills first, then uninstall the CLI:

```bash
ppx skills uninstall
uv tool uninstall paper-plane-x-cli
```

If you installed skills into a custom directory, pass the same directory when uninstalling:

```bash
ppx skills uninstall --target-dir ~/.agents/skills
```

## License

Paper Plane X CLI is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE).
