"""Paper Plane X HTTP CLI for external agent tools."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Annotated, Any, NoReturn, cast

import httpx
import typer

DEFAULT_BASE_URL = "http://127.0.0.1:8000/api/v1"
GLOBAL_CONTEXT_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
GLOBAL_CONTEXT_PATH = GLOBAL_CONTEXT_DIR / "paper-plane-x" / "context.json"
LOCAL_CONTEXT_PATH = Path.cwd() / ".paper-plane-x" / "context.json"
QueryParamValue = str | int | bool


def _fail(message: str, *, status_code: int = 2) -> NoReturn:
    typer.echo(json.dumps({"error": message}, ensure_ascii=False), err=True)
    raise typer.Exit(status_code)


def _load_context(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        data_obj: object = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"Invalid context file JSON: {path}: {exc}")
    if not isinstance(data_obj, dict):
        _fail(f"Invalid context file shape: {path}")
    data = cast(dict[str, object], data_obj)
    return {key: str(value) for key, value in data.items() if value is not None}


def _save_context(data: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def resolve_context(
    base_url: str | None = None,
    project_id: str | None = None,
) -> dict[str, str | None]:
    global_ctx = _load_context(GLOBAL_CONTEXT_PATH)
    local_ctx = _load_context(LOCAL_CONTEXT_PATH)
    merged = {**global_ctx, **local_ctx}
    resolved_base_url = (
        base_url
        or os.environ.get("PPX_BASE_URL")
        or merged.get("base_url")
        or DEFAULT_BASE_URL
    )
    resolved_project_id = (
        project_id or os.environ.get("PPX_PROJECT_ID") or merged.get("project_id")
    )
    return {
        "base_url": resolved_base_url.rstrip("/"),
        "project_id": resolved_project_id,
    }


def _print_json(payload: object, *, stream: Any | None = None) -> None:
    stream = stream or sys.stdout
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=stream)


def _split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _require_project_id(ctx: dict[str, str | None]) -> str:
    project_id = ctx.get("project_id")
    if not project_id:
        _fail("project_id is required. Run: ppx context set --project-id <id>")
    return project_id


def _request(
    method: str,
    path: str,
    ctx: dict[str, str | None],
    json_body: object | None = None,
    params: dict[str, QueryParamValue | None] | None = None,
    data: dict[str, str] | None = None,
    files: dict[str, Any] | None = None,
) -> object:
    base_url = ctx["base_url"]
    url = f"{base_url}{path}"
    cleaned_params = (
        {key: value for key, value in params.items() if value is not None}
        if params
        else None
    )
    try:
        response = httpx.request(
            method,
            url,
            json=json_body,
            params=cleaned_params,
            data=data,
            files=files,
            timeout=60.0,
        )
    except httpx.HTTPError as exc:
        _fail(f"HTTP request failed: {exc}", status_code=1)

    if response.status_code >= 400:
        try:
            detail = response.json()
        except json.JSONDecodeError:
            detail = response.text
        _fail(
            json.dumps(
                {"status_code": response.status_code, "error": detail},
                ensure_ascii=False,
            ),
            status_code=1,
        )

    if not response.content:
        return {}
    return response.json()


app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help=(
        "Paper Plane X HTTP CLI. All commands call a running Paper Plane X "
        "FastAPI server and print JSON for external agents."
    ),
)


@app.callback()
def callback(
    ctx: typer.Context,
    base_url: Annotated[
        str | None,
        typer.Option(
            "--base-url",
            help="Override API base URL, e.g. http://127.0.0.1:8000/api/v1.",
        ),
    ] = None,
    project_id: Annotated[
        str | None,
        typer.Option("--project-id", help="Override current Paper Plane X project ID."),
    ] = None,
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["ctx"] = resolve_context(base_url=base_url, project_id=project_id)


context_app = typer.Typer(
    no_args_is_help=True,
    help="Show or save local CLI context such as API base URL and project ID.",
)
app.add_typer(context_app, name="context")


@context_app.command("show", help="Print resolved CLI context as JSON.")
def context_show(ctx: typer.Context) -> None:
    global_ctx = _load_context(GLOBAL_CONTEXT_PATH)
    local_ctx = _load_context(LOCAL_CONTEXT_PATH)
    merged = {**global_ctx, **local_ctx}
    resolved = ctx.obj["ctx"]
    _print_json(
        {
            "resolved": resolved,
            "global": global_ctx or None,
            "local": local_ctx or None,
            "merged": merged or None,
        }
    )


@context_app.command(
    "set",
    help=f"Save context to {GLOBAL_CONTEXT_PATH} (default) or {LOCAL_CONTEXT_PATH} (--local).",
)
def context_set(
    set_base_url: Annotated[
        str | None,
        typer.Option(
            "--base-url",
            help="API base URL to save, e.g. http://127.0.0.1:8000/api/v1.",
        ),
    ] = None,
    set_project_id: Annotated[
        str | None,
        typer.Option(
            "--project-id", help="Project ID to save for project-scoped commands."
        ),
    ] = None,
    local: Annotated[
        bool,
        typer.Option(
            "--local",
            help="Write to the local context file in the current directory instead of the global one.",
        ),
    ] = False,
) -> None:
    path = LOCAL_CONTEXT_PATH if local else GLOBAL_CONTEXT_PATH
    data = _load_context(path)
    if set_base_url is not None:
        data["base_url"] = set_base_url.rstrip("/")
    if set_project_id is not None:
        data["project_id"] = set_project_id
    _save_context(data, path)
    _print_json(data)


project_app = typer.Typer(
    no_args_is_help=True,
    help="Project-scoped discovery and overview commands.",
)
app.add_typer(project_app, name="project")


@project_app.command(
    "global-finder",
    help="Summarize and browse papers associated with the current project.",
)
def project_global_finder(ctx: typer.Context) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    payload = _request(
        "POST",
        "/librarian/global-finder",
        ctx=ctx_dict,
        json_body={"project_id": project_id},
    )
    _print_json(payload)


librarian_app = typer.Typer(
    no_args_is_help=True,
    help="Search, compare, and deep-dive papers through the Librarian API.",
)
app.add_typer(librarian_app, name="librarian")


@librarian_app.command(
    "search",
    help="Search project papers with the Librarian query expression DSL.",
)
def librarian_search(
    ctx: typer.Context,
    query_expr: Annotated[
        str,
        typer.Option(
            "--query-expr",
            help='DSL query, e.g. "(meta.title CONTAINS transformer)".',
        ),
    ],
    limit: Annotated[
        int, typer.Option("--limit", help="Maximum number of papers.")
    ] = 20,
    offset: Annotated[int, typer.Option("--offset", help="Pagination offset.")] = 0,
) -> None:
    ctx_dict = ctx.obj["ctx"]
    payload = _request(
        "POST",
        "/librarian/search",
        ctx=ctx_dict,
        json_body={
            "project_id": ctx_dict.get("project_id"),
            "query_expr": query_expr,
            "limit": limit,
            "offset": offset,
        },
    )
    _print_json(payload)


@librarian_app.command(
    "matrix",
    help="Fetch structured field paths for one or more papers.",
)
def librarian_matrix(
    ctx: typer.Context,
    paper_ids: Annotated[
        str,
        typer.Option("--paper-ids", help="Comma-separated paper IDs, e.g. p1,p2."),
    ],
    field_paths: Annotated[
        str,
        typer.Option(
            "--field-paths",
            help="Comma-separated field paths, e.g. meta.title,quick_scan.verdict.",
        ),
    ],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    payload = _request(
        "POST",
        "/librarian/matrix",
        ctx=ctx_dict,
        json_body={
            "paper_ids": _split_csv(paper_ids),
            "field_paths": _split_csv(field_paths),
        },
    )
    _print_json(payload)


@librarian_app.command(
    "deep-dive",
    help="Ask a focused question about a single paper.",
)
def librarian_deep_dive(
    ctx: typer.Context,
    paper_id: Annotated[str, typer.Option("--paper-id", help="Paper ID to inspect.")],
    question: Annotated[
        str,
        typer.Option("--question", help="Focused question for the Deep Diver agent."),
    ],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    payload = _request(
        "POST",
        "/librarian/deep-dive",
        ctx=ctx_dict,
        json_body={"paper_id": paper_id, "question": question},
    )
    _print_json(payload)


files_app = typer.Typer(
    no_args_is_help=True,
    help="Read, write, upload, patch, and delete project sandbox files.",
)
app.add_typer(files_app, name="files")


@files_app.command("list", help="List files and directories in the project sandbox.")
def files_list(
    ctx: typer.Context,
    dir: Annotated[str, typer.Option("--dir", help="Sandbox directory to list.")] = "/",
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = _request("GET", prefix, ctx=ctx_dict, params={"dir_path": dir})
    _print_json(payload)


@files_app.command("read", help="Read a project sandbox text file.")
def files_read(
    ctx: typer.Context,
    path: Annotated[
        str,
        typer.Option("--path", help="Sandbox file path, e.g. /notes/idea.md."),
    ],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = _request(
        "GET", f"{prefix}/content", ctx=ctx_dict, params={"file_path": path}
    )
    _print_json(payload)


@files_app.command("lines", help="Read a 1-based inclusive line range from a file.")
def files_lines(
    ctx: typer.Context,
    path: Annotated[str, typer.Option("--path", help="Sandbox file path.")],
    start_line: Annotated[
        int, typer.Option("--start-line", help="First line, 1-based.")
    ],
    end_line: Annotated[
        int | None,
        typer.Option(
            "--end-line", help="Last line, inclusive. Defaults to start line."
        ),
    ] = None,
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = _request(
        "GET",
        f"{prefix}/lines",
        ctx=ctx_dict,
        params={
            "file_path": path,
            "start_line": start_line,
            "end_line": end_line,
        },
    )
    _print_json(payload)


@files_app.command("find", help="Find text occurrences in a project sandbox file.")
def files_find(
    ctx: typer.Context,
    path: Annotated[str, typer.Option("--path", help="Sandbox file path.")],
    query: Annotated[str, typer.Option("--query", help="Text to search for.")],
    case_sensitive: Annotated[
        bool,
        typer.Option("--case-sensitive", help="Use case-sensitive matching."),
    ] = False,
    max_matches: Annotated[
        int,
        typer.Option("--max-matches", help="Maximum number of matches to return."),
    ] = 20,
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = _request(
        "GET",
        f"{prefix}/find",
        ctx=ctx_dict,
        params={
            "file_path": path,
            "query": query,
            "case_sensitive": case_sensitive,
            "max_matches": max_matches,
        },
    )
    _print_json(payload)


@files_app.command("write", help="Write or overwrite a project sandbox text file.")
def files_write(
    ctx: typer.Context,
    path: Annotated[str, typer.Option("--path", help="Sandbox destination path.")],
    content: Annotated[
        str, typer.Option("--content", help="Full text content to write.")
    ],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = _request(
        "PUT",
        f"{prefix}/content",
        ctx=ctx_dict,
        json_body={"file_path": path, "content": content},
    )
    _print_json(payload)


@files_app.command("upload", help="Upload a local file into the project sandbox.")
def files_upload(
    ctx: typer.Context,
    source: Annotated[
        Path,
        typer.Option(
            "--source",
            exists=True,
            dir_okay=False,
            help="Local file to upload.",
        ),
    ],
    path: Annotated[
        str | None,
        typer.Option(
            "--path",
            help="Sandbox destination path. Defaults to /<source filename>.",
        ),
    ] = None,
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    target_path = path or f"/{source.name}"
    prefix = f"/projects/{project_id}/files"
    with source.open("rb") as file_obj:
        payload = _request(
            "POST",
            f"{prefix}/upload",
            ctx=ctx_dict,
            data={"file_path": target_path},
            files={"file": (source.name, file_obj)},
        )
    _print_json(payload)


@files_app.command("replace-lines", help="Replace a 1-based inclusive line range.")
def files_replace_lines(
    ctx: typer.Context,
    path: Annotated[str, typer.Option("--path", help="Sandbox file path.")],
    start_line: Annotated[
        int, typer.Option("--start-line", help="First line to replace.")
    ],
    end_line: Annotated[int, typer.Option("--end-line", help="Last line to replace.")],
    new_text: Annotated[str, typer.Option("--new-text", help="Replacement text.")],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = _request(
        "PATCH",
        f"{prefix}/lines",
        ctx=ctx_dict,
        json_body={
            "file_path": path,
            "start_line": start_line,
            "end_line": end_line,
            "new_text": new_text,
        },
    )
    _print_json(payload)


@files_app.command("replace-text", help="Replace exact text in a project sandbox file.")
def files_replace_text(
    ctx: typer.Context,
    path: Annotated[str, typer.Option("--path", help="Sandbox file path.")],
    old_text: Annotated[str, typer.Option("--old-text", help="Exact text to replace.")],
    new_text: Annotated[str, typer.Option("--new-text", help="Replacement text.")],
    replace_all: Annotated[
        bool,
        typer.Option("--replace-all", help="Replace all occurrences instead of one."),
    ] = False,
    expected_occurrences: Annotated[
        int,
        typer.Option(
            "--expected-occurrences",
            help="Required occurrence count before replacement proceeds.",
        ),
    ] = 1,
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = _request(
        "PATCH",
        f"{prefix}/text",
        ctx=ctx_dict,
        json_body={
            "file_path": path,
            "old_text": old_text,
            "new_text": new_text,
            "replace_all": replace_all,
            "expected_occurrences": expected_occurrences,
        },
    )
    _print_json(payload)


@files_app.command("patch", help="Patch a file relative to an exact anchor text.")
def files_patch(
    ctx: typer.Context,
    path: Annotated[str, typer.Option("--path", help="Sandbox file path.")],
    action: Annotated[
        str,
        typer.Option(
            "--action",
            help="Patch action: replace, insert_before, insert_after, or delete.",
        ),
    ],
    anchor_text: Annotated[
        str,
        typer.Option("--anchor-text", help="Exact anchor text to locate."),
    ],
    content: Annotated[
        str,
        typer.Option("--content", help="Content for replace/insert actions."),
    ] = "",
    expected_occurrences: Annotated[
        int,
        typer.Option(
            "--expected-occurrences",
            help="Required anchor occurrence count before patch proceeds.",
        ),
    ] = 1,
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = _request(
        "PATCH",
        f"{prefix}/patch",
        ctx=ctx_dict,
        json_body={
            "file_path": path,
            "action": action,
            "anchor_text": anchor_text,
            "content": content,
            "expected_occurrences": expected_occurrences,
        },
    )
    _print_json(payload)


@files_app.command("delete", help="Delete a project sandbox file or empty directory.")
def files_delete(
    ctx: typer.Context,
    path: Annotated[str, typer.Option("--path", help="Sandbox path to delete.")],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = _require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = _request(
        "DELETE", f"{prefix}/content", ctx=ctx_dict, params={"file_path": path}
    )
    _print_json(payload)


paper_note_app = typer.Typer(
    no_args_is_help=True,
    help="Get, write, or delete paper-level agent notes.",
)
app.add_typer(paper_note_app, name="paper-note")


@paper_note_app.command("get", help="Read the agent note for a paper.")
def paper_note_get(
    ctx: typer.Context,
    paper_id: Annotated[str, typer.Option("--paper-id", help="Paper ID.")],
) -> None:
    path = f"/papers/{paper_id}/agent-note"
    payload = _request("GET", path, ctx=ctx.obj["ctx"])
    _print_json(payload)


@paper_note_app.command("write", help="Write or overwrite the agent note for a paper.")
def paper_note_write(
    ctx: typer.Context,
    paper_id: Annotated[str, typer.Option("--paper-id", help="Paper ID.")],
    content: Annotated[str, typer.Option("--content", help="Full note content.")],
) -> None:
    path = f"/papers/{paper_id}/agent-note"
    payload = _request("PUT", path, ctx=ctx.obj["ctx"], json_body={"content": content})
    _print_json(payload)


@paper_note_app.command("delete", help="Delete the agent note for a paper.")
def paper_note_delete(
    ctx: typer.Context,
    paper_id: Annotated[str, typer.Option("--paper-id", help="Paper ID.")],
) -> None:
    path = f"/papers/{paper_id}/agent-note"
    payload = _request("DELETE", path, ctx=ctx.obj["ctx"])
    _print_json(payload)


if __name__ == "__main__":
    app()
