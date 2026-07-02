import json
from pathlib import Path
from typing import Any

import httpx
from typer.testing import CliRunner

from paper_plane_x_cli import cli

runner = CliRunner()


def test_paper_markdown_downloads_to_default_filename(
    tmp_path: Path,
    monkeypatch,
) -> None:
    captured: dict[str, Any] = {}
    markdown = "# Parsed paper\n\n完整正文".encode()

    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        captured.update({"method": method, "url": url, **kwargs})
        return httpx.Response(
            200,
            content=markdown,
            headers={"content-type": "text/markdown; charset=utf-8"},
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)
    save_dir = tmp_path / "exports" / "papers"

    result = runner.invoke(
        cli.app,
        [
            "--base-url",
            "http://server/api/v1",
            "paper",
            "markdown",
            "--paper-id",
            "pap-1",
            "--save-dir",
            str(save_dir),
        ],
    )

    assert result.exit_code == 0
    assert captured["method"] == "GET"
    assert captured["url"] == "http://server/api/v1/papers/pap-1/markdown"
    assert (save_dir / "pap-1.md").read_bytes() == markdown
    payload = json.loads(result.output)
    assert payload == {
        "paper_id": "pap-1",
        "md_path": str(save_dir / "pap-1.md"),
        "bytes_written": len(markdown),
    }


def test_paper_markdown_supports_custom_filename(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"# Custom\n",
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)
    save_dir = tmp_path / "exports"

    result = runner.invoke(
        cli.app,
        [
            "paper",
            "markdown",
            "--paper-id",
            "pap-2",
            "--save-dir",
            str(save_dir),
            "--output-md-name",
            "full-paper.md",
        ],
    )

    assert result.exit_code == 0
    assert (save_dir / "full-paper.md").read_bytes() == b"# Custom\n"


def test_paper_markdown_http_error_does_not_create_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        return httpx.Response(
            409,
            json={"detail": "Paper pap-empty has no parsed markdown content"},
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)
    save_dir = tmp_path / "exports"

    result = runner.invoke(
        cli.app,
        [
            "paper",
            "markdown",
            "--paper-id",
            "pap-empty",
            "--save-dir",
            str(save_dir),
        ],
    )

    assert result.exit_code == 1
    assert "no parsed markdown content" in result.output
    assert not save_dir.exists()


def test_paper_markdown_rejects_path_as_output_filename(tmp_path: Path) -> None:
    save_dir = tmp_path / "exports"

    result = runner.invoke(
        cli.app,
        [
            "paper",
            "markdown",
            "--paper-id",
            "pap-3",
            "--save-dir",
            str(save_dir),
            "--output-md-name",
            "../escape.md",
        ],
    )

    assert result.exit_code == 2
    assert "single .md filename" in result.output
    assert not save_dir.exists()
