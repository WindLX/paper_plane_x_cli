import base64
import json
from pathlib import Path
from typing import Any

import httpx
from typer.testing import CliRunner

from paper_plane_x_cli import cli

runner = CliRunner()


def test_pdf_parse_builds_multipart_request_and_writes_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")
    save_dir = tmp_path / "parsed"
    image_data = base64.b64encode(b"image-bytes").decode("ascii")
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        captured.update({"method": method, "url": url, **kwargs})
        uploaded_name, uploaded_file, uploaded_mime = kwargs["files"]["pdf_file"]
        captured["pdf_file"] = {
            "name": uploaded_name,
            "content": uploaded_file.read(),
            "mime": uploaded_mime,
        }
        request = httpx.Request(method, url)
        return httpx.Response(
            200,
            json={
                "md_content": "# Paper\n\n![fig](images/fig.png)\n",
                "images": [
                    {
                        "name": "images/fig.png",
                        "mime_type": "image/png",
                        "base64": image_data,
                    },
                    {
                        "name": "images/unused.png",
                        "mime_type": "image/png",
                        "base64": image_data,
                    },
                ],
                "parser_type": "local_mineru",
            },
            request=request,
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)

    result = runner.invoke(
        cli.app,
        [
            "pdf",
            "parse",
            "--source",
            str(pdf_path),
            "--save-dir",
            str(save_dir),
        ],
    )

    assert result.exit_code == 0
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/api/v1/parse/pdf")
    assert captured["data"]["output_md_name"] == "paper.md"
    assert captured["pdf_file"]["name"] == "paper.pdf"
    assert captured["pdf_file"]["content"] == b"%PDF-1.4"

    assert save_dir.exists()
    md_path = save_dir / "paper.md"
    assert md_path.read_text(encoding="utf-8") == "# Paper\n\n![fig](images/fig.png)\n"

    images_dir = save_dir / "images"
    assert (images_dir / "fig.png").read_bytes() == b"image-bytes"
    assert not (images_dir / "unused.png").exists()

    payload = json.loads(result.output)
    assert payload == {
        "md_path": str(md_path),
        "image_paths": [str(images_dir / "fig.png")],
        "parser_type": "local_mineru",
    }


def test_pdf_parse_rejects_non_pdf_source(tmp_path: Path) -> None:
    source_path = tmp_path / "paper.txt"
    source_path.write_text("not a pdf", encoding="utf-8")
    save_dir = tmp_path / "parsed"

    result = runner.invoke(
        cli.app,
        [
            "pdf",
            "parse",
            "--source",
            str(source_path),
            "--save-dir",
            str(save_dir),
        ],
    )

    assert result.exit_code != 0
    assert "pdf" in result.output.lower()
