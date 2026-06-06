"""Project-scoped commands for the Paper Plane X CLI."""

from __future__ import annotations

import typer

from paper_plane_x_cli.cli.utils import print_json, request, require_project_id

project_app = typer.Typer(
    no_args_is_help=True,
    help="Project-scoped discovery and overview commands.",
)


@project_app.command(
    "global-finder",
    help="Summarize and browse papers associated with the current project.",
)
def project_global_finder(ctx: typer.Context) -> None:
    ctx_dict = ctx.obj["ctx"]
    project_id = require_project_id(ctx_dict)
    payload = request(
        "POST",
        "/librarian/global-finder",
        ctx=ctx_dict,
        json_body={"project_id": project_id},
    )
    print_json(payload)
