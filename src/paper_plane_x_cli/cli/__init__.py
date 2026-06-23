"""Paper Plane X HTTP CLI for external agent tools."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import httpx as httpx
import typer

from paper_plane_x_cli.cli.context import context_app
from paper_plane_x_cli.cli.files import files_app
from paper_plane_x_cli.cli.librarian import librarian_app
from paper_plane_x_cli.cli.paper_note import paper_note_app
from paper_plane_x_cli.cli.pdf import pdf_app
from paper_plane_x_cli.cli.project import project_app
from paper_plane_x_cli.cli.skills import skills_app
from paper_plane_x_cli.cli.utils import DEFAULT_BASE_URL, load_context

GLOBAL_CONTEXT_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
GLOBAL_CONTEXT_PATH = GLOBAL_CONTEXT_DIR / "paper-plane-x" / "context.json"
LOCAL_CONTEXT_PATH = Path.cwd() / ".paper-plane-x" / "context.json"


def resolve_context(
    base_url: str | None = None,
    project_id: str | None = None,
) -> dict[str, str | None]:
    global_ctx = load_context(GLOBAL_CONTEXT_PATH)
    local_ctx = load_context(LOCAL_CONTEXT_PATH)
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


app.add_typer(context_app, name="context")
app.add_typer(project_app, name="project")
app.add_typer(pdf_app, name="pdf")
app.add_typer(librarian_app, name="librarian")
app.add_typer(files_app, name="files")
app.add_typer(paper_note_app, name="paper-note")
app.add_typer(skills_app, name="skills")


if __name__ == "__main__":
    app()
