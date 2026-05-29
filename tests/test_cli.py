import json
from pathlib import Path
from typing import Any

import httpx

from paper_plane_x_cli import cli


def test_context_precedence_args_env_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    context_path = tmp_path / "context.json"
    context_path.write_text(
        json.dumps(
            {
                "base_url": "http://file/api/v1",
                "project_id": "file-project",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cli, "CONTEXT_PATH", context_path)
    monkeypatch.setenv("PPX_BASE_URL", "http://env/api/v1")
    monkeypatch.setenv("PPX_PROJECT_ID", "env-project")

    assert cli.resolve_context(
        base_url="http://arg/api/v1",
        project_id="arg-project",
    ) == {
        "base_url": "http://arg/api/v1",
        "project_id": "arg-project",
    }


def test_cli_help_exits_successfully(capsys) -> None:
    status = cli.run(["--help"])

    assert status == 0
    output = capsys.readouterr().out
    assert "Usage: ppx" in output
    assert "Paper Plane X HTTP CLI" in output
    assert "Override API base URL" in output


def test_nested_command_help_includes_descriptions(capsys) -> None:
    status = cli.run(["files", "upload", "--help"])

    output = capsys.readouterr().out
    assert status == 0
    assert "Upload a local file into the project sandbox" in output
    assert "Local file to upload" in output
    assert "Sandbox destination path" in output


def test_cli_no_args_shows_help_without_traceback(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli.sys, "argv", ["ppx"])

    status = cli.run()

    captured = capsys.readouterr()
    assert status == 0
    assert "Usage: ppx" in captured.out
    assert "Traceback" not in captured.err


def test_librarian_search_builds_http_request(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    context_path = tmp_path / "context.json"
    context_path.write_text(
        json.dumps(
            {
                "base_url": "http://server/api/v1",
                "project_id": "proj-1",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cli, "CONTEXT_PATH", context_path)
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        captured.update({"method": method, "url": url, **kwargs})
        request = httpx.Request(method, url)
        return httpx.Response(
            200,
            json={"paper_ids": ["p1"], "total": 1},
            request=request,
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)

    status = cli.run(
        [
            "librarian",
            "search",
            "--query-expr",
            "(meta.title CONTAINS test)",
            "--limit",
            "5",
        ]
    )

    assert status == 0
    assert captured["method"] == "POST"
    assert captured["url"] == "http://server/api/v1/librarian/search"
    assert captured["json"]["project_id"] == "proj-1"
    assert captured["json"]["limit"] == 5
    assert json.loads(capsys.readouterr().out)["paper_ids"] == ["p1"]


def test_files_upload_builds_multipart_request(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    context_path = tmp_path / "context.json"
    context_path.write_text(
        json.dumps(
            {
                "base_url": "http://server/api/v1",
                "project_id": "proj-1",
            }
        ),
        encoding="utf-8",
    )
    source_path = tmp_path / "local.md"
    source_path.write_text("# Local\n", encoding="utf-8")
    monkeypatch.setattr(cli, "CONTEXT_PATH", context_path)
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        uploaded_name, uploaded_file = kwargs["files"]["file"]
        captured.update(
            {
                "method": method,
                "url": url,
                "data": kwargs["data"],
                "uploaded_name": uploaded_name,
                "uploaded_content": uploaded_file.read(),
            }
        )
        request = httpx.Request(method, url)
        return httpx.Response(
            200,
            json={
                "file_path": "/notes/local.md",
                "bytes_written": 8,
                "is_dir": False,
            },
            request=request,
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)

    status = cli.run(
        [
            "files",
            "upload",
            "--source",
            str(source_path),
            "--path",
            "/notes/local.md",
        ]
    )

    assert status == 0
    assert captured["method"] == "POST"
    assert captured["url"] == "http://server/api/v1/projects/proj-1/files/upload"
    assert captured["data"]["file_path"] == "/notes/local.md"
    assert captured["uploaded_name"] == "local.md"
    assert captured["uploaded_content"] == b"# Local\n"
    assert json.loads(capsys.readouterr().out)["file_path"] == "/notes/local.md"


def test_cli_reports_http_error(
    monkeypatch,
    capsys,
) -> None:
    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        request = httpx.Request(method, url)
        return httpx.Response(
            422,
            json={"detail": {"code": "invalid_field"}},
            request=request,
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)

    status = cli.run(
        [
            "--project-id",
            "proj-1",
            "librarian",
            "search",
            "--query-expr",
            "(bad CONTAINS x)",
        ]
    )

    assert status == 1
    payload = json.loads(capsys.readouterr().err)
    assert "invalid_field" in payload["error"]
