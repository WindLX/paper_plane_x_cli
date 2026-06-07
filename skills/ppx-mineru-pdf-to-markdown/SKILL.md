---
name: ppx-mineru-pdf-to-markdown
description: Use when an agent needs to read, summarize, extract, cite, or process local PDF files by first converting them to Markdown with the Paper Plane X CLI MinerU tool. Trigger for PDF-heavy research, scanned PDFs, papers with formulas/tables, or requests to transform PDFs into Markdown assets.
---

# MinerU PDF To Markdown

When the task involves a local PDF, convert it to Markdown before doing close reading, extraction, rewriting, or downstream upload. Prefer Markdown over raw PDF parsing because it preserves text flow, formulas, tables, and referenced images more consistently.

## Workflow

1. Confirm the PDF exists locally.
2. Run MinerU conversion:

```bash
ppx mineru parse --source ./paper.pdf --save-dir ./paper-mineru
```

3. Read the generated Markdown from the returned `md_path`.
4. Use the Markdown as the evidence source for summaries, structured extraction, comparison, or edits.
5. If the result should become a Paper Plane X project asset, upload or write the Markdown through the researcher/project-file workflow.

## Command

```bash
ppx mineru parse \
  --source ./paper.pdf \
  --save-dir ./paper-mineru \
```

Important options:

- `--source`: local PDF file path.
- `--save-dir`: local directory where Markdown and `images/` are written.
- `--mineru-url`: MinerU HTTP service base URL. If omitted, it is resolved from context (set with `ppx context set --mineru-url`), then the `MINERU_BASE_URL` environment variable, then the default `http://127.0.0.1:8888`.
- `--output-md-name`: Markdown filename. Defaults to the PDF stem plus `.md`.
- `--lang-list`: comma-separated language codes to assist parsing, e.g. `en` or `ch,en`.
- `--start-page-id` / `--end-page-id`: parse a page range for large PDFs.
- `timeout`: HTTP timeout in seconds.

The command prints JSON:

```json
{
  "md_path": "./paper-mineru/paper.md",
  "image_paths": ["./paper-mineru/images/fig1.png"]
}
```

## Reading Rules

- Base claims on the generated Markdown, not on guessed PDF contents.
- If conversion fails, report the MinerU error and ask whether to retry with a different `--mineru-url`.
- Preserve image references when moving Markdown; copy or upload the associated `images/` files if the target workflow needs figures.
