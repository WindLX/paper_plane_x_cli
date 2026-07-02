"""Librarian search and deep-dive commands for the Paper Plane X CLI."""

from __future__ import annotations

from typing import Annotated

import typer

from paper_plane_x_cli.cli.utils import print_json, request, split_csv

librarian_app = typer.Typer(
    no_args_is_help=True,
    help="Search, compare, and deep-dive papers through the Librarian API.",
)


@librarian_app.command(
    "search",
    help="Search project papers with the Librarian query expression DSL.",
)
def librarian_search(
    ctx: typer.Context,
    query_expr: Annotated[
        str,
        typer.Option(
            "--query-expr", help='DSL query, e.g. "(meta.title CONTAINS transformer)".'
        ),
    ],
    limit: Annotated[
        int, typer.Option("--limit", help="Maximum number of papers.")
    ] = 20,
    offset: Annotated[int, typer.Option("--offset", help="Pagination offset.")] = 0,
) -> None:
    ctx_dict = ctx.obj["ctx"]
    payload = request(
        "POST",
        "/librarian/search",
        ctx=ctx_dict,
        json_body={
            "project_id": ctx_dict.get("project_id"),
            "query_expr": query_expr,
            "limit": limit,
            "offset": offset,
        },
    )
    print_json(payload)


@librarian_app.command(
    "matrix",
    help="Fetch structured field paths for one or more papers.",
)
def librarian_matrix(
    ctx: typer.Context,
    paper_ids: Annotated[
        str,
        typer.Option("--paper-ids", help="Comma-separated paper IDs, e.g. p1,p2."),
    ],
    field_paths: Annotated[
        str,
        typer.Option(
            "--field-paths",
            help="Comma-separated field paths, e.g. meta.title,quick_scan.verdict.",
        ),
    ],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    payload = request(
        "POST",
        "/librarian/matrix",
        ctx=ctx_dict,
        json_body={
            "paper_ids": split_csv(paper_ids),
            "field_paths": split_csv(field_paths),
        },
    )
    print_json(payload)


@librarian_app.command(
    "deep-dive",
    help="Ask a focused question about a single paper.",
)
def librarian_deep_dive(
    ctx: typer.Context,
    paper_id: Annotated[str, typer.Option("--paper-id", help="Paper ID to inspect.")],
    question: Annotated[
        str,
        typer.Option("--question", help="Focused question for the Deep Diver agent."),
    ],
) -> None:
    ctx_dict = ctx.obj["ctx"]
    payload = request(
        "POST",
        "/librarian/deep-dive",
        ctx=ctx_dict,
        json_body={"paper_id": paper_id, "question": question},
        timeout=240,
    )
    print_json(payload)
