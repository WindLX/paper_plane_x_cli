"""Context management commands for the Paper Plane X CLI."""

from __future__ import annotations

from typing import Annotated

import typer

from paper_plane_x_cli.cli.utils import (
    GLOBAL_CONTEXT_PATH,
    LOCAL_CONTEXT_PATH,
    load_context,
    normalize_project_id,
    print_json,
    save_context,
)

context_app = typer.Typer(
    no_args_is_help=True,
    help="Show or save local CLI context such as API base URL and project ID.",
)


@context_app.command("show", help="Print resolved CLI context as JSON.")
def context_show(ctx: typer.Context) -> None:
    global_ctx = load_context(GLOBAL_CONTEXT_PATH)
    local_ctx = load_context(LOCAL_CONTEXT_PATH)
    merged = {**global_ctx, **local_ctx}
    resolved = ctx.obj["ctx"]
    print_json(
        {
            "resolved": resolved,
            "global": global_ctx or None,
            "local": local_ctx or None,
            "merged": merged or None,
        }
    )


@context_app.command(
    "set",
    help=f"Save context to {LOCAL_CONTEXT_PATH} (default) or {GLOBAL_CONTEXT_PATH} (--global).",
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
            "--project-id",
            help="Project ID to save; none/null saves an explicit null value.",
        ),
    ] = None,
    global_context: Annotated[
        bool,
        typer.Option(
            "--global",
            help="Write to the global context file instead of the local file in the current directory.",
        ),
    ] = False,
) -> None:
    path = GLOBAL_CONTEXT_PATH if global_context else LOCAL_CONTEXT_PATH
    data = load_context(path)
    if set_base_url is not None:
        data["base_url"] = set_base_url.rstrip("/")
    if set_project_id is not None:
        normalized_project_id = normalize_project_id(set_project_id)
        if normalized_project_id is None:
            data.pop("project_id", None)
        else:
            data["project_id"] = normalized_project_id
    save_context(data, path)
    print_json(data)
