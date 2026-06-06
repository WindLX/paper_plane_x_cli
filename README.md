# Paper Plane X CLI

Standalone HTTP CLI and external-agent skill for Paper Plane X.

This package contains:

- `ppx`: a JSON-first CLI that talks to a running Paper Plane X FastAPI server.
- `skills/paper-plane-x-researcher`: the Researcher skill for Codex, Claude Code, and other agent tools.
- `skills/mineru-pdf-to-markdown`: a PDF-to-Markdown workflow skill backed by MinerU.

Most CLI commands do not import backend tools or access the database directly. Project and librarian commands only call HTTP endpoints under `/api/v1`. The MinerU command is a standalone local utility that calls a MinerU HTTP service directly.

## Install

From the monorepo root:

```bash
uvx --from ./paper_plane_x_cli ppx --help
uv tool install ./paper_plane_x_cli
```

From the backend directory:

```bash
uvx --from ../paper_plane_x_cli ppx --help
uv tool install ../paper_plane_x_cli
```

From a Git repository that contains this package as a subdirectory:

```bash
uvx --from "git+https://github.com/<owner>/<repo>.git#subdirectory=paper_plane_x_cli" ppx --help
uv tool install "git+https://github.com/<owner>/<repo>.git#subdirectory=paper_plane_x_cli"
```

After `uv tool install`, use `ppx` directly.

## Context

`ppx` resolves context in this order:

1. command line options: `--base-url`, `--project-id`, `--mineru-url`
2. environment variables: `PPX_BASE_URL`, `PPX_PROJECT_ID`, `PPX_MINERU_URL`
3. local context file: `./.paper-plane-x/context.json` (in the current working directory)
4. global context file: `~/.config/paper-plane-x/context.json`
5. default base URL: `http://127.0.0.1:8000/api/v1`, default MinerU URL: `http://127.0.0.1:8888`

The local context overrides the global context. This allows per-project settings without changing your global defaults.

```bash
# Global context (default)
ppx context set --base-url http://127.0.0.1:8000/api/v1
ppx context set --project-id prj_x
ppx context set --mineru-url http://127.0.0.1:8888

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

## MinerU PDF Conversion

Use MinerU when an external agent needs to read or process a local PDF as Markdown:

```bash
ppx mineru parse --source ./paper.pdf --save-dir ./paper-mineru
```

The MinerU URL is resolved in the same order as other context values: `--mineru-url` option, `MINERU_BASE_URL` environment variable, local/global context file (`ppx context set --mineru-url`), then the default `http://127.0.0.1:8888`.

The command writes Markdown plus referenced images and prints JSON:

```json
{
  "md_path": "paper-mineru/paper.md",
  "image_paths": ["paper-mineru/images/fig1.png"]
}
```

Useful options:

```bash
ppx mineru parse --source ./scan.pdf --save-dir ./scan-mineru --parse-method ocr
ppx mineru parse --source ./paper.pdf --save-dir ./paper-mineru --lang-list ch,en
ppx mineru parse --source ./paper.pdf --save-dir ./paper-mineru --start-page-id 0 --end-page-id 10
```

## Skill

Bundled skills live under `skills/`:

```text
skills/paper-plane-x-researcher/SKILL.md
skills/mineru-pdf-to-markdown/SKILL.md
```

Use it when an external agent should follow the same research workflow as Paper Plane X: verify project context, search and compare papers through `ppx`, write durable results into project files or paper notes, and cite only evidence actually fetched through the CLI/API.

Use the MinerU skill when an external agent encounters local PDFs and should convert them to Markdown before reading, summarizing, extracting, or uploading the result.
