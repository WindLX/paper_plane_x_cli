---
name: ppx-mineru-pdf-to-markdown
description: Convert local PDF files to Markdown with the Paper Plane X CLI MinerU tool before close reading, summarizing, extracting, citing, or uploading. Use for scanned PDFs, research papers, formulas, tables, figures, or requests to create Markdown assets from PDFs.
---

# MinerU PDF To Markdown

Use this skill when a task depends on the contents of a local PDF. Convert the PDF to Markdown first, then use the generated Markdown as the evidence source for reading, extraction, summarization, citation, comparison, or downstream upload.

## Workflow

1. Confirm the input is a local `.pdf`.
2. Choose parsing options only when the task needs them:
   - long PDF trial run: `--start-page-id` and `--end-page-id`
3. Convert the PDF:

```bash
ppx mineru parse --source ./paper.pdf --save-dir ./paper-mineru
```

4. Read the returned `md_path`.
5. Preserve any referenced images from `image_paths` when moving or uploading the Markdown.
6. If the result should become a Paper Plane X project asset, use the researcher/project-file workflow to upload or write it.

## Command

```bash
ppx mineru parse \
  --source ./paper.pdf \
  --save-dir ./paper-mineru
```

Important options:

- `--source`: local PDF file path.
- `--save-dir`: local directory where Markdown and `images/` are written.
- `--mineru-url`: MinerU HTTP service base URL. Resolution order is CLI option, `MINERU_BASE_URL`, local/global context from `ppx context set --mineru-url`, then `http://127.0.0.1:8888`.
- `--output-md-name`: Markdown filename. Defaults to the PDF stem plus `.md`.
- `--start-page-id` / `--end-page-id`: page range, 0-based start. Use for partial parsing of large PDFs.
- `--timeout`: HTTP timeout in seconds. Default is `300`.

The command prints JSON:

```json
{
  "md_path": "./paper-mineru/paper.md",
  "image_paths": ["./paper-mineru/images/fig1.png"]
}
```

## Reading Rules

- Base claims on the generated Markdown, not guessed PDF contents or filenames.
- If conversion fails, report the CLI error and retry only when there is a clear adjustment: wrong URL, smaller page range, timeout, or different language list.
- If Markdown contains figure links, keep the `images/` directory together with the Markdown when the target workflow needs figures.
