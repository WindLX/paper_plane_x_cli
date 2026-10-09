import json
from pathlib import Path
from typing import Any

import httpx
from typer.testing import CliRunner

from paper_plane_x_cli import cli

runner = CliRunner()

# A minimal PNG-shaped payload that carries non-UTF-8 bytes in the body: a
# text-mode read or any decode step would corrupt or reject it, so an exact
# byte comparison fails the moment the upload stops streaming the raw file.
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
    b"\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDAT\x78\x9c\x63\x00\x01\x00\x00\x05\x00\x01"
    b"\x0d\x0a\x2d\xb4"
    b"\x00\x00\x00\x00IEND\xaeB\x60\x82"
)

# An SVG whose payload would break naive text handling: a UTF-8 BOM plus a
# non-ASCII glyph, so an exact byte comparison also catches re-encoding.
SVG_BYTES = (
    b'\xef\xbb\xbf<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2 2">'
    + ('<text y="2">\u56fe</text></svg>').encode("utf-8")
)


def _set_context_paths(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cli, "GLOBAL_CONTEXT_PATH", tmp_path / "global.json")
    monkeypatch.setattr(cli, "LOCAL_CONTEXT_PATH", tmp_path / "local.json")


def _capture_upload(
    monkeypatch, tmp_path: Path, source: Path, sandbox_path: str
) -> dict[str, Any]:
    """Run `files upload` while recording the real multipart request httpx builds."""
    _set_context_paths(monkeypatch, tmp_path)
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        # Rebuild the request with httpx's own multipart encoder so the
        # assertions below run against the exact bytes sent on the wire. The
        # encoder consumes the file object, so snapshot its bytes first.
        name, file_obj = kwargs["files"]["file"]
        raw_content = file_obj.read()
        rebuilt_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in {"timeout", "files"}
        }
        rebuilt_kwargs["files"] = {"file": (name, raw_content)}
        built = httpx.Request(method, url, **rebuilt_kwargs)
        built.read()
        captured.update(
            {
                "method": method,
                "url": url,
                "data": kwargs["data"],
                "name": name,
                "content": raw_content,
                "body": built.content,
                "content_type": built.headers["content-type"],
            }
        )
        return httpx.Response(
            201,
            json={
                "file_path": sandbox_path,
                "bytes_written": len(source.read_bytes()),
                "is_dir": False,
            },
            request=built,
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)

    result = runner.invoke(
        cli.app,
        [
            "--project-id",
            "project-1",
            "files",
            "upload",
            "--source",
            str(source),
            "--path",
            sandbox_path,
        ],
    )
    assert result.exit_code == 0, result.output
    return {"output": result.output, "captured": captured}


def test_files_upload_sends_raw_image_bytes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "figure.png"
    source.write_bytes(PNG_BYTES)

    run = _capture_upload(monkeypatch, tmp_path, source, "/images/figure.png")
    captured = run["captured"]

    assert captured["method"] == "POST"
    assert (
        captured["url"]
        == "http://127.0.0.1:8000/api/v1/projects/project-1/files/upload"
    )
    assert captured["data"] == {"file_path": "/images/figure.png"}
    assert captured["name"] == "figure.png"
    # The file object is streamed as raw bytes, never decoded or rewritten.
    assert captured["content"] == PNG_BYTES
    # The multipart body carries the identical byte sequence, so any decode or
    # text-mode round trip in the upload path would change these bytes.
    assert PNG_BYTES in captured["body"]
    assert captured["content_type"].startswith("multipart/form-data; boundary=")

    payload = json.loads(run["output"])
    assert payload["file_path"] == "/images/figure.png"
    assert payload["bytes_written"] == len(PNG_BYTES)


def test_files_upload_preserves_svg_bytes_without_reencoding(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "diagram.svg"
    source.write_bytes(SVG_BYTES)

    run = _capture_upload(monkeypatch, tmp_path, source, "/images/diagram.svg")
    captured = run["captured"]

    assert captured["name"] == "diagram.svg"
    assert captured["content"] == SVG_BYTES
    assert SVG_BYTES in captured["body"]

    payload = json.loads(run["output"])
    assert payload["bytes_written"] == len(SVG_BYTES)
