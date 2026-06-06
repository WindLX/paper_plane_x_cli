"""Project sandbox file commands for the Paper Plane X CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from paper_plane_x_cli.cli.utils import print_json, request, require_project_id

files_app = typer.Typer(
    no_args_is_help=True,
    help="Read, write, upload, patch, and delete project sandbox files.",
)


@files_app.command("list", help="List files and directories in the project sandbox.")
def files_list(
    ctx: typer.Context,
    dir: Annotated[str, typer.Option("--dir", help="Sandbox directory to list.")] = "/",
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = request("GET", prefix, ctx=ctx_dict, params={"dir_path": dir})
    print_json(payload)


@files_app.command("read", help="Read a project sandbox text file.")
def files_read(
    ctx: typer.Context,
    path: Annotated[
        str,
        typer.Option("--path", help="Sandbox file path, e.g. /notes/idea.md."),
    ],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = request(
        "GET", f"{prefix}/content", ctx=ctx_dict, params={"file_path": path}
    )
    print_json(payload)


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
    project_id = require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = request(
        "GET",
        f"{prefix}/lines",
        ctx=ctx_dict,
        params={
            "file_path": path,
            "start_line": start_line,
            "end_line": end_line,
        },
    )
    print_json(payload)


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
    project_id = require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = request(
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
    print_json(payload)


@files_app.command("write", help="Write or overwrite a project sandbox text file.")
def files_write(
    ctx: typer.Context,
    path: Annotated[str, typer.Option("--path", help="Sandbox destination path.")],
    content: Annotated[
        str, typer.Option("--content", help="Full text content to write.")
    ],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = request(
        "PUT",
        f"{prefix}/content",
        ctx=ctx_dict,
        json_body={"file_path": path, "content": content},
    )
    print_json(payload)


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
    project_id = require_project_id(ctx_dict)
    target_path = path or f"/{source.name}"
    prefix = f"/projects/{project_id}/files"
    with source.open("rb") as file_obj:
        payload = request(
            "POST",
            f"{prefix}/upload",
            ctx=ctx_dict,
            data={"file_path": target_path},
            files={"file": (source.name, file_obj)},
        )
    print_json(payload)


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
    project_id = require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = request(
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
    print_json(payload)


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
    project_id = require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = request(
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
    print_json(payload)


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
    project_id = require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = request(
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
    print_json(payload)


@files_app.command("delete", help="Delete a project sandbox file or empty directory.")
def files_delete(
    ctx: typer.Context,
    path: Annotated[str, typer.Option("--path", help="Sandbox path to delete.")],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = require_project_id(ctx_dict)
    prefix = f"/projects/{project_id}/files"
    payload = request(
        "DELETE", f"{prefix}/content", ctx=ctx_dict, params={"file_path": path}
    )
    print_json(payload)
