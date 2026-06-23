---
name: ppx-pdf-to-markdown
description: Convert local PDF files to Markdown with the Paper Plane X CLI before close reading, summarizing, extracting, citing, or uploading. Use for scanned PDFs, research papers, formulas, tables, figures, or requests to create Markdown assets from PDFs.
---

# PDF To Markdown

Use this skill when a task depends on the contents of a local PDF. Convert the PDF to Markdown first, then use the generated Markdown as the evidence source for reading, extraction, summarization, citation, comparison, or downstream upload.

## Workflow

1. Confirm the input is a local `.pdf`.
2. Convert the PDF:

```bash
ppx pdf parse --source ./paper.pdf --save-dir ./paper-pdf
```

3. Read the returned `md_path`.
4. Preserve any referenced images from `image_paths` when moving or uploading the Markdown.
5. If the result should become a Paper Plane X project asset, use the researcher/project-file workflow to upload or write it.

## Command

```bash
ppx pdf parse \
  --source ./paper.pdf \
  --save-dir ./paper-pdf
```

Important options:

- `--source`: local PDF file path.
- `--save-dir`: local directory where Markdown and `images/` are written.
- `--output-md-name`: Markdown filename. Defaults to the PDF stem plus `.md`.

The command prints JSON:

```json
{
  "md_path": "./paper-pdf/paper.md",
  "image_paths": ["./paper-pdf/images/fig1.png"],
  "parser_type": "local_mineru"
}
```

## Reading Rules

- Base claims on the generated Markdown, not guessed PDF contents or filenames.
- If conversion fails, report the CLI error and retry only when there is a clear adjustment: wrong base URL, smaller file, or timeout.
- If Markdown contains figure links, keep the `images/` directory together with the Markdown when the target workflow needs figures.
