"""Paper-level agent note commands for the Paper Plane X CLI."""

from __future__ import annotations

from typing import Annotated

import typer

from paper_plane_x_cli.cli.utils import print_json, request

paper_note_app = typer.Typer(
    no_args_is_help=True,
    help="Get, write, or delete paper-level agent notes.",
)


@paper_note_app.command("get", help="Read the agent note for a paper.")
def paper_note_get(
    ctx: typer.Context,
    paper_id: Annotated[str, typer.Option("--paper-id", help="Paper ID.")],
) -> None:
    path = f"/papers/{paper_id}/agent-note"
    payload = request("GET", path, ctx=ctx.obj["ctx"])
    print_json(payload)


@paper_note_app.command("write", help="Write or overwrite the agent note for a paper.")
def paper_note_write(
    ctx: typer.Context,
    paper_id: Annotated[str, typer.Option("--paper-id", help="Paper ID.")],
    content: Annotated[str, typer.Option("--content", help="Full note content.")],
) -> None:
    path = f"/papers/{paper_id}/agent-note"
    payload = request("PUT", path, ctx=ctx.obj["ctx"], json_body={"content": content})
    print_json(payload)


@paper_note_app.command("delete", help="Delete the agent note for a paper.")
def paper_note_delete(
    ctx: typer.Context,
    paper_id: Annotated[str, typer.Option("--paper-id", help="Paper ID.")],
) -> None:
    path = f"/papers/{paper_id}/agent-note"
    payload = request("DELETE", path, ctx=ctx.obj["ctx"])
    print_json(payload)
