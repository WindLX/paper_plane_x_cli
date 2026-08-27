"""Tests for data-process task CLI commands."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from paper_plane_x_cli.cli import app

runner = CliRunner()


def _task_payload(status: str) -> dict[str, object]:
    return {
        "task_id": "tsk-test",
        "paper_id": "pap-test",
        "status": status,
        "created_at": "2026-08-27T08:00:00",
        "started_at": None,
        "finished_at": None,
        "error": None,
        "retry_of_task_id": None,
        "extraction_trace_ids": [],
        "analysis_trace_ids": [],
        "extraction_fact_check_trace_ids": [],
        "analysis_fact_check_trace_ids": [],
    }


def test_task_get_adds_agent_fields(monkeypatch) -> None:
    monkeypatch.setattr(
        "paper_plane_x_cli.cli.task.request",
        lambda method, path, context: _task_payload("RUNNING"),
    )

    result = runner.invoke(app, ["task", "get", "--task-id", "tsk-test"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["terminal"] is False
    assert payload["next_action"] == "wait_for_data_process"
    assert payload["elapsed_seconds"] == 0.0


def test_task_wait_returns_completed(monkeypatch) -> None:
    responses = iter([_task_payload("QUEUED"), _task_payload("COMPLETED")])
    clock = iter([10.0, 10.0, 11.0])
    monkeypatch.setattr(
        "paper_plane_x_cli.cli.task.request",
        lambda method, path, context: next(responses),
    )
    monkeypatch.setattr(
        "paper_plane_x_cli.cli.task.time.monotonic", lambda: next(clock)
    )
    monkeypatch.setattr("paper_plane_x_cli.cli.task.time.sleep", lambda seconds: None)

    result = runner.invoke(
        app,
        ["task", "wait", "--task-id", "tsk-test", "--interval", "1"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "COMPLETED"
    assert payload["terminal"] is True
    assert payload["next_action"] == "read_paper"


def test_task_wait_uses_exit_four_for_terminal_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "paper_plane_x_cli.cli.task.request",
        lambda method, path, context: _task_payload("FAILED"),
    )

    result = runner.invoke(app, ["task", "wait", "--task-id", "tsk-test"])

    assert result.exit_code == 4
    assert json.loads(result.stdout)["status"] == "FAILED"
    assert "ended with status FAILED" in result.stderr


def test_task_wait_uses_exit_three_for_timeout(monkeypatch) -> None:
    clock = iter([10.0, 10.0])
    monkeypatch.setattr(
        "paper_plane_x_cli.cli.task.request",
        lambda method, path, context: _task_payload("RUNNING"),
    )
    monkeypatch.setattr(
        "paper_plane_x_cli.cli.task.time.monotonic", lambda: next(clock)
    )

    result = runner.invoke(
        app,
        ["task", "wait", "--task-id", "tsk-test", "--timeout", "0"],
    )

    assert result.exit_code == 3
    assert json.loads(result.stdout)["status"] == "RUNNING"
    assert "Timed out" in result.stderr


def test_task_rejects_unknown_status(monkeypatch) -> None:
    monkeypatch.setattr(
        "paper_plane_x_cli.cli.task.request",
        lambda method, path, context: _task_payload("UNKNOWN"),
    )

    result = runner.invoke(app, ["task", "get", "--task-id", "tsk-test"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "unsupported" in result.stderr
