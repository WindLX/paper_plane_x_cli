"""Paper resource commands for the Paper Plane X CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from paper_plane_x_cli.cli.utils import fail, print_json, request_bytes

paper_app = typer.Typer(
    no_args_is_help=True,
    help="Access Paper Plane X paper resources.",
)


@paper_app.command("markdown", help="Download a paper's parsed Markdown text.")
def paper_markdown(
    ctx: typer.Context,
    paper_id: Annotated[str, typer.Option("--paper-id", help="Paper ID.")],
    save_dir: Annotated[
        Path,
        typer.Option(
            "--save-dir",
            help="Directory where the Markdown file is written.",
        ),
    ],
    output_md_name: Annotated[
        str | None,
        typer.Option(
            "--output-md-name",
            help="Markdown filename. Defaults to <paper-id>.md.",
        ),
    ] = None,
) -> None:
    md_name = output_md_name or f"{paper_id}.md"
    name_path = Path(md_name)
    if name_path.name != md_name or name_path.suffix.lower() != ".md":
        fail("--output-md-name must be a single .md filename")

    content = request_bytes(
        "GET",
        f"/papers/{paper_id}/markdown",
        ctx.obj["ctx"],
    )

    save_dir.mkdir(parents=True, exist_ok=True)
    md_path = save_dir / md_name
    md_path.write_bytes(content)

    print_json(
        {
            "paper_id": paper_id,
            "md_path": str(md_path),
            "bytes_written": len(content),
        }
    )
