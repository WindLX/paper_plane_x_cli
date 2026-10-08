# Advanced Topics: Project Files

Project files live in the Paper Plane X project sandbox. Reach for these commands when the task needs to read, save, upload, or modify project files.

## Commands

| Researcher action     | CLI command                                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------------------- |
| List files            | `ppx files list --dir /`                                                                              |
| Read whole file       | `ppx files read --path /notes/idea.md`                                                                |
| Read line range       | `ppx files lines --path /draft.md --start-line 10 --end-line 20`                                      |
| Find text             | `ppx files find --path /draft.md --query "Related Work"`                                              |
| Write/overwrite file  | `ppx files write --path /notes/summary.md --content "..."`                                            |
| Upload local file     | `ppx files upload --source ./summary.md --path /notes/summary.md`                                     |
| Replace line range    | `ppx files replace-lines --path /draft.md --start-line 4 --end-line 6 --new-text "..."`               |
| Replace exact text    | `ppx files replace-text --path /draft.md --old-text "..." --new-text "..."`                           |
| Anchor patch          | `ppx files patch --path /draft.md --action insert_after --anchor-text "## Methods\n" --content "..."` |
| Delete file/empty dir | `ppx files delete --path /tmp/old.md`                                                                 |

If `--path` is omitted on `upload`, the file targets `/<source filename>`.

## Editing Rules

- Inspect before editing: use `list`, `read`, `lines`, or `find`.
- Prefer the smallest reliable edit: `replace-lines` for known line ranges, `replace-text` for unique fixed text, `patch` for anchor-based edits.
- Use `write` only for new files or intentional full-file regeneration.
- Use `upload` when a local file already exists; do not paste large local files into `write`.
- `replace-text` and `patch` support `--expected-occurrences`; use it for safety. `replace-text` also supports `--replace-all`.
- If an edit command fails because line numbers, matches, or paths changed, re-read or re-find before retrying.
- Line numbers are 1-based, and `end_line` is inclusive.
- Project files must stay inside the sandbox and use one of: `.csv`, `.json`, `.md`, `.txt`, `.yaml`, `.yml`, `.toml`.
- Single-file size limit is 10485760 bytes.

## Examples

Inspect before editing:

```bash
ppx files list --dir /
ppx files find --path /draft.md --query "Related Work"
ppx files lines --path /draft.md --start-line 20 --end-line 40
```

Small line edit:

```bash
ppx files replace-lines --path /draft.md --start-line 24 --end-line 29 --new-text "new paragraph"
```

Anchor edit:

```bash
ppx files patch --path /draft.md --action insert_after --anchor-text "## Related Work\n" --content "new content\n"
```

Whole-file write, only when intended:

```bash
ppx files write --path /notes/lit-review.md --content "# Literature Review\n..."
```

Upload a local file into the project sandbox:

```bash
ppx files upload --source ./lit-review.md --path /notes/lit-review.md
```

Delete a file or empty directory:

```bash
ppx files delete --path /tmp/old.md
```
