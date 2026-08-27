"""Paper resource commands for the Paper Plane X CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, cast

import typer

from paper_plane_x_cli.cli.utils import (
    download_file,
    fail,
    print_json,
    request,
    request_bytes,
)

paper_app = typer.Typer(
    no_args_is_help=True,
    help="Access Paper Plane X paper resources.",
)


@paper_app.command("upload", help="Upload a local PDF to Paper Plane X.")
def paper_upload(
    ctx: typer.Context,
    source: Annotated[
        Path,
        typer.Option(
            "--source",
            exists=True,
            dir_okay=False,
            help="Local PDF file to upload.",
        ),
    ],
    title: Annotated[
        str | None,
        typer.Option("--title", help="Verified paper title, if available."),
    ] = None,
    authors: Annotated[
        list[str] | None,
        typer.Option(
            "--author",
            help="Verified author name. Repeat for multiple authors.",
        ),
    ] = None,
    year: Annotated[
        int | None,
        typer.Option("--year", min=1, help="Verified publication year."),
    ] = None,
    publication: Annotated[
        str | None,
        typer.Option("--publication", help="Verified journal or conference."),
    ] = None,
    doi: Annotated[
        str | None,
        typer.Option("--doi", help="Verified DOI."),
    ] = None,
) -> None:
    if source.suffix.lower() != ".pdf":
        fail(f"paper upload expects a PDF file: {source}")

    context = cast(dict[str, str | None], ctx.obj["ctx"])
    data: dict[str, str] = {}
    if title is not None:
        data["title"] = title
    if authors:
        data["authors"] = ", ".join(authors)
    if year is not None:
        data["year"] = str(year)
    if publication is not None:
        data["publication"] = publication
    if doi is not None:
        data["doi"] = doi

    with source.open("rb") as file_obj:
        response = request(
            "POST",
            "/papers",
            context,
            data=data,
            files={"pdf_file": (source.name, file_obj, "application/pdf")},
        )

    if not isinstance(response, dict):
        fail("Invalid response: expected a JSON object", status_code=1)
    payload = cast(dict[str, object], response)
    project_id = context.get("project_id")
    if project_id is not None:
        paper_id = payload.get("paper_id")
        if not isinstance(paper_id, str) or not paper_id:
            fail(
                "Upload succeeded but the response did not contain a valid paper_id; "
                "the project was not linked.",
                status_code=1,
            )
        request(
            "POST",
            f"/projects/{project_id}/papers/{paper_id}",
            context,
        )

    payload["project_id"] = project_id
    payload["next_action"] = (
        "paper_ready"
        if payload.get("status") == "COMPLETED"
        else "wait_for_data_process"
    )
    print_json(payload)


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


@paper_app.command("pdf", help="Download a paper's original PDF file.")
def paper_pdf(
    ctx: typer.Context,
    paper_id: Annotated[str, typer.Option("--paper-id", help="Paper ID.")],
    save_dir: Annotated[
        Path,
        typer.Option(
            "--save-dir",
            help="Directory where the PDF file is written.",
        ),
    ],
    output_pdf_name: Annotated[
        str | None,
        typer.Option(
            "--output-pdf-name",
            help="PDF filename. Defaults to <paper-id>.pdf.",
        ),
    ] = None,
) -> None:
    pdf_name = output_pdf_name or f"{paper_id}.pdf"
    name_path = Path(pdf_name)
    if name_path.name != pdf_name or name_path.suffix.lower() != ".pdf":
        fail("--output-pdf-name must be a single .pdf filename")

    pdf_path = save_dir / pdf_name
    bytes_written = download_file(
        f"/papers/{paper_id}/pdf?download=true",
        ctx.obj["ctx"],
        pdf_path,
    )

    print_json(
        {
            "paper_id": paper_id,
            "pdf_path": str(pdf_path),
            "bytes_written": bytes_written,
        }
    )
