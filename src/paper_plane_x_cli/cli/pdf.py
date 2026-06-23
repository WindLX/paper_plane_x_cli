"""PDF parsing commands for the Paper Plane X CLI."""

from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Annotated, Any, cast
from urllib.parse import unquote, urlparse

import typer

from paper_plane_x_cli.cli.utils import (
    fail,
    get_output_md_name,
    print_json,
    request,
)

pdf_app = typer.Typer(
    no_args_is_help=True,
    help="Parse local PDFs to Markdown through the Paper Plane X API.",
)


@pdf_app.command("parse", help="Convert a local PDF into Markdown and image files.")
def pdf_parse(
    ctx: typer.Context,
    source: Annotated[
        Path,
        typer.Option(
            "--source",
            exists=True,
            dir_okay=False,
            help="Local PDF file to parse.",
        ),
    ],
    save_dir: Annotated[
        Path,
        typer.Option(
            "--save-dir",
            help="Directory where Markdown and referenced images are written.",
        ),
    ],
    output_md_name: Annotated[
        str | None,
        typer.Option(
            "--output-md-name",
            help="Markdown filename. Defaults to the PDF stem plus .md.",
        ),
    ] = None,
) -> None:
    if source.suffix.lower() != ".pdf":
        fail(f"pdf parse expects a PDF file: {source}")

    md_name = get_output_md_name(source, output_md_name)

    with source.open("rb") as file_obj:
        data = {"output_md_name": md_name}
        files = {"pdf_file": (source.name, file_obj, "application/pdf")}
        response = request("POST", "/parse/pdf", ctx.obj["ctx"], data=data, files=files)

    response_data = cast(dict[str, Any], response)
    md_content = response_data.get("md_content")
    if not isinstance(md_content, str):
        fail("Invalid response: 'md_content' missing or not a string")

    save_dir.mkdir(parents=True, exist_ok=True)
    md_path = save_dir / md_name
    md_path.write_text(md_content, encoding="utf-8")

    image_save_dir = save_dir / "images"
    image_save_dir.mkdir(parents=True, exist_ok=True)

    _write_images(response_data.get("images", []), image_save_dir)
    _prune_unreferenced_images(md_content, image_save_dir)
    image_paths = _get_image_paths(md_content, image_save_dir)

    payload: dict[str, object] = {
        "md_path": str(md_path),
        "image_paths": [str(path) for path in image_paths],
        "parser_type": response_data.get("parser_type", ""),
    }
    print_json(payload)


def _write_images(images_raw: object, image_save_dir: Path) -> None:
    if not isinstance(images_raw, list):
        return

    for image_info in cast(list[Any], images_raw):
        if not isinstance(image_info, dict):
            continue

        name = image_info.get("name")
        b64 = image_info.get("base64")
        if not isinstance(name, str) or not isinstance(b64, str):
            continue

        try:
            img_bytes = base64.b64decode(b64)
        except ValueError:
            continue

        target_path = image_save_dir / Path(name).name
        target_path.write_bytes(img_bytes)


def _get_image_paths(md_content: str, image_dir: Path) -> list[Path]:
    if not image_dir.exists():
        return []

    referenced_names = _extract_referenced_image_names(md_content)
    image_paths: list[Path] = []
    for file_name in sorted(referenced_names):
        candidate = image_dir / file_name
        if candidate.exists() and candidate.is_file():
            image_paths.append(candidate)
    return image_paths


def _prune_unreferenced_images(md_content: str, image_dir: Path) -> None:
    if not image_dir.exists():
        return

    referenced_names = _extract_referenced_image_names(md_content)
    for candidate in image_dir.iterdir():
        if candidate.is_file() and candidate.name not in referenced_names:
            candidate.unlink(missing_ok=True)


def _extract_referenced_image_names(md_content: str) -> set[str]:
    references: set[str] = set()

    md_pattern = r"!\[[^\]]*\]\(([^)]+)\)"
    html_pattern = r"<img[^>]+src=[\"']([^\"']+)[\"'][^>]*>"

    for raw_ref in cast(list[str], re.findall(md_pattern, md_content)):
        ref = raw_ref.strip()
        if " " in ref:
            ref = ref.split(" ", 1)[0]
        ref = ref.strip("<>'\"")
        parsed_path = Path(unquote(urlparse(ref).path))
        if parsed_path.name:
            references.add(parsed_path.name)

    for raw_ref in cast(
        list[str],
        re.findall(html_pattern, md_content, flags=re.IGNORECASE),
    ):
        ref = raw_ref.strip("<>'\"")
        parsed_path = Path(unquote(urlparse(ref).path))
        if parsed_path.name:
            references.add(parsed_path.name)

    return references
