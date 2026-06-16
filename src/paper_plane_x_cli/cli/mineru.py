"""MinerU PDF parsing commands for the Paper Plane X CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import httpx
import typer

from paper_plane_x_cli.cli.utils import (
    DEFAULT_MINERU_URL,
    fail,
    get_output_md_name,
    print_json,
    split_csv,
)
from paper_plane_x_cli.mineru import MinerUBackend, MinerUClient, MinerUParseMethod

mineru_app = typer.Typer(
    no_args_is_help=True,
    help="Convert local PDFs to Markdown through a MinerU HTTP server.",
)


@mineru_app.command("parse", help="Convert a local PDF into Markdown and image files.")
def mineru_parse(
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
    mineru_url: Annotated[
        str | None,
        typer.Option(
            "--mineru-url",
            envvar="MINERU_BASE_URL",
            help="MinerU HTTP base URL. Can also be set with MINERU_BASE_URL. Defaults to the resolved context value.",
        ),
    ] = None,
    output_md_name: Annotated[
        str | None,
        typer.Option(
            "--output-md-name",
            help="Markdown filename. Defaults to the PDF stem plus .md.",
        ),
    ] = None,
    lang_list: Annotated[
        str,
        typer.Option(
            "--lang-list",
            help="Comma-separated MinerU language list, e.g. ch,en.",
        ),
    ] = "ch",
    backend: Annotated[
        MinerUBackend,
        typer.Option("--backend", help="MinerU parsing backend."),
    ] = MinerUBackend.HYBRID_AUTO,
    parse_method: Annotated[
        MinerUParseMethod,
        typer.Option("--parse-method", help="MinerU parse method."),
    ] = MinerUParseMethod.AUTO,
    formula_enable: Annotated[
        bool,
        typer.Option(
            "--formula/--no-formula",
            help="Enable formula recognition.",
        ),
    ] = True,
    table_enable: Annotated[
        bool,
        typer.Option("--table/--no-table", help="Enable table recognition."),
    ] = True,
    start_page_id: Annotated[
        int,
        typer.Option("--start-page-id", help="First page index to parse, 0-based."),
    ] = 0,
    end_page_id: Annotated[
        int,
        typer.Option("--end-page-id", help="Last page index to parse."),
    ] = 99999,
    timeout: Annotated[
        float,
        typer.Option("--timeout", help="HTTP timeout in seconds."),
    ] = 300.0,
) -> None:
    if source.suffix.lower() != ".pdf":
        fail(f"MinerU parse expects a PDF file: {source}")

    # Resolve mineru_url from CLI option -> context -> default
    resolved_mineru_url = (
        mineru_url or ctx.obj["ctx"].get("mineru_url") or DEFAULT_MINERU_URL
    )

    md_name = get_output_md_name(source, output_md_name)
    try:
        result = MinerUClient(resolved_mineru_url).parse_pdf(
            file_path=source,
            output_md_name=md_name,
            save_dir=save_dir,
            output_dir=save_dir,
            lang_list=split_csv(lang_list),
            backend=backend,
            parse_method=parse_method,
            formula_enable=formula_enable,
            table_enable=table_enable,
            start_page_id=start_page_id,
            end_page_id=end_page_id,
            timeout=timeout,
        )
    except (FileNotFoundError, ValueError, RuntimeError, httpx.HTTPError) as exc:
        fail(str(exc), status_code=1)

    payload: dict[str, object] = {
        "md_path": str(result.md_path),
        "image_paths": [str(path) for path in result.image_paths],
    }
    print_json(payload)
