---
name: mineru-pdf-to-markdown
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
  --mineru-url http://127.0.0.1:8888 \
  --lang-list ch,en
```

Important options:

- `--mineru-url`: MinerU HTTP service base URL. Can also be set with `MINERU_BASE_URL`.
- `--save-dir`: local directory where Markdown and `images/` are written.
- `--output-md-name`: override the Markdown filename.
- `--backend`: MinerU backend, default `hybrid-auto-engine`.
- `--parse-method`: `auto`, `txt`, or `ocr`; use `ocr` for scanned PDFs when `auto` output is poor.
- `--start-page-id` / `--end-page-id`: parse a page range for large PDFs.
- `--include-content`: include Markdown content in JSON output; avoid for long papers unless the caller explicitly needs stdout content.

The command prints JSON:

```json
{
  "md_path": "./paper-mineru/paper.md",
  "image_paths": ["./paper-mineru/images/fig1.png"]
}
```

## Reading Rules

- Base claims on the generated Markdown, not on guessed PDF contents.
- If conversion fails, report the MinerU error and ask whether to retry with a different `--mineru-url`, `--parse-method ocr`, or page range.
- If Markdown appears incomplete, retry with `--parse-method ocr` for scanned documents or parse smaller page ranges.
- Preserve image references when moving Markdown; copy or upload the associated `images/` files if the target workflow needs figures.
