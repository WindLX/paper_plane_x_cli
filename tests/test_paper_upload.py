import json
from pathlib import Path
from typing import Any

import httpx
from typer.testing import CliRunner

from paper_plane_x_cli import cli

runner = CliRunner()


def _set_context_paths(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cli, "GLOBAL_CONTEXT_PATH", tmp_path / "global.json")
    monkeypatch.setattr(cli, "LOCAL_CONTEXT_PATH", tmp_path / "local.json")


def test_paper_upload_builds_multipart_request(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _set_context_paths(monkeypatch, tmp_path)
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-1.4 upload")
    captured: list[dict[str, Any]] = []

    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        if url.endswith("/papers"):
            name, file_obj, mime = kwargs["files"]["pdf_file"]
            captured.append(
                {
                    "method": method,
                    "url": url,
                    "data": kwargs["data"],
                    "name": name,
                    "content": file_obj.read(),
                    "mime": mime,
                }
            )
        else:
            captured.append({"method": method, "url": url})
        return httpx.Response(
            202 if url.endswith("/papers") else 201,
            json=(
                {
                    "paper_id": "paper-1",
                    "task_id": "task-1",
                    "status": "QUEUED",
                    "resource_type": "paper",
                    "resource_id": "paper-1",
                    "message": "Data-process task queued",
                }
                if url.endswith("/papers")
                else {"project_id": "project-1", "paper_id": "paper-1"}
            ),
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)

    result = runner.invoke(
        cli.app,
        [
            "--project-id",
            "project-1",
            "paper",
            "upload",
            "--source",
            str(source),
            "--author",
            "Alice",
            "--author",
            "Bob",
            "--year",
            "2025",
            "--doi",
            "10.1000/example",
        ],
    )

    assert result.exit_code == 0
    assert captured == [
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/api/v1/papers",
            "data": {
                "authors": "Alice, Bob",
                "year": "2025",
                "doi": "10.1000/example",
            },
            "name": "paper.pdf",
            "content": b"%PDF-1.4 upload",
            "mime": "application/pdf",
        },
        {
            "method": "POST",
            "url": ("http://127.0.0.1:8000/api/v1/projects/project-1/papers/paper-1"),
        },
    ]
    payload = json.loads(result.output)
    assert payload["paper_id"] == "paper-1"
    assert payload["project_id"] == "project-1"
    assert payload["next_action"] == "wait_for_data_process"


def test_paper_upload_allows_explicitly_unscoped_upload(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _set_context_paths(monkeypatch, tmp_path)
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-1.4 upload")
    captured_data: dict[str, str] = {}

    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        captured_data.update(kwargs["data"])
        return httpx.Response(
            202,
            json={
                "paper_id": "paper-1",
                "task_id": "task-1",
                "status": "COMPLETED",
            },
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)
    monkeypatch.setenv("PPX_PROJECT_ID", "none")

    result = runner.invoke(
        cli.app,
        ["paper", "upload", "--source", str(source)],
    )

    assert result.exit_code == 0
    assert captured_data == {}
    payload = json.loads(result.output)
    assert payload["project_id"] is None
    assert payload["next_action"] == "paper_ready"


def test_paper_upload_rejects_non_pdf(tmp_path: Path, monkeypatch) -> None:
    _set_context_paths(monkeypatch, tmp_path)
    source = tmp_path / "paper.txt"
    source.write_text("not a pdf", encoding="utf-8")

    result = runner.invoke(
        cli.app,
        ["paper", "upload", "--source", str(source)],
    )

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "expects a PDF" in result.stderr
