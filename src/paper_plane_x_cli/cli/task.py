"""Data-process task commands for the Paper Plane X CLI."""

from __future__ import annotations

import json
import time
from typing import Annotated, NoReturn, cast

import typer

from paper_plane_x_cli.cli.utils import print_json, request

task_app = typer.Typer(
    no_args_is_help=True,
    help="Inspect and wait for Paper Plane X data-process tasks.",
)

ACTIVE_STATUSES = {"QUEUED", "RUNNING", "CANCELING"}
TERMINAL_STATUSES = {"COMPLETED", "FAILED", "CANCELED"}


def _normalize_task_payload(
    payload: object, elapsed_seconds: float
) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValueError("Invalid response: expected a JSON object")
    task = cast(dict[str, object], payload)
    status_value = task.get("status")
    if not isinstance(status_value, str) or status_value not in (
        ACTIVE_STATUSES | TERMINAL_STATUSES
    ):
        raise ValueError("Invalid response: task status is missing or unsupported")

    normalized = dict(task)
    normalized["terminal"] = status_value in TERMINAL_STATUSES
    normalized["elapsed_seconds"] = round(elapsed_seconds, 3)
    normalized["next_action"] = {
        "COMPLETED": "read_paper",
        "FAILED": "inspect_error_or_retry",
        "CANCELED": "retry_if_needed",
    }.get(status_value, "wait_for_data_process")
    return normalized


def _emit_error(message: str, exit_code: int) -> NoReturn:
    typer.echo(json.dumps({"error": message}, ensure_ascii=False), err=True)
    raise typer.Exit(exit_code)


@task_app.command("get", help="Get one data-process task as JSON.")
def task_get(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Option("--task-id", help="Task ID.")],
) -> None:
    try:
        payload = _normalize_task_payload(
            request("GET", f"/data-process/tasks/{task_id}", ctx.obj["ctx"]),
            elapsed_seconds=0.0,
        )
    except ValueError as exc:
        _emit_error(str(exc), 1)
    print_json(payload)


@task_app.command(
    "wait", help="Wait until a data-process task reaches a terminal state."
)
def task_wait(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Option("--task-id", help="Task ID.")],
    timeout: Annotated[
        float,
        typer.Option("--timeout", min=0.0, help="Maximum wait in seconds."),
    ] = 1800.0,
    interval: Annotated[
        float,
        typer.Option("--interval", min=0.1, help="Polling interval in seconds."),
    ] = 5.0,
) -> None:
    started_at = time.monotonic()

    while True:
        elapsed = time.monotonic() - started_at
        try:
            payload = _normalize_task_payload(
                request("GET", f"/data-process/tasks/{task_id}", ctx.obj["ctx"]),
                elapsed_seconds=elapsed,
            )
        except ValueError as exc:
            _emit_error(str(exc), 1)

        status_value = cast(str, payload["status"])
        if status_value in TERMINAL_STATUSES:
            print_json(payload)
            if status_value != "COMPLETED":
                _emit_error(f"Data-process task ended with status {status_value}", 4)
            return

        if elapsed >= timeout:
            print_json(payload)
            _emit_error(
                f"Timed out after {timeout:g}s while waiting for task {task_id}",
                3,
            )

        time.sleep(min(interval, max(timeout - elapsed, 0.0)))
