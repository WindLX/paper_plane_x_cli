"""Context management commands for the Paper Plane X CLI."""

from __future__ import annotations

from typing import Annotated

import typer

from paper_plane_x_cli.cli.utils import (
    GLOBAL_CONTEXT_PATH,
    LOCAL_CONTEXT_PATH,
    load_context,
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
    set_mineru_url: Annotated[
        str | None,
        typer.Option(
            "--mineru-url",
            help="MinerU HTTP base URL to save. Defaults to http://127.0.1:8888.",
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
    data = load_context(path)
    if set_base_url is not None:
        data["base_url"] = set_base_url.rstrip("/")
    if set_project_id is not None:
        data["project_id"] = set_project_id
    if set_mineru_url is not None:
        data["mineru_url"] = set_mineru_url.rstrip("/")
    save_context(data, path)
    print_json(data)
