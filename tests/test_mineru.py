import base64
import json
from pathlib import Path
from typing import Any

import httpx
from typer.testing import CliRunner

from paper_plane_x_cli import cli
from paper_plane_x_cli.mineru import MinerUClient, MinerUOutput

runner = CliRunner()


def test_mineru_client_writes_markdown_and_referenced_images(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")
    save_dir = tmp_path / "parsed"
    image_data = base64.b64encode(b"image-bytes").decode("ascii")

    def fake_post(url: str, **kwargs: Any) -> httpx.Response:
        assert url == "http://mineru/file_parse"
        assert kwargs["data"]["backend"] == "hybrid-auto-engine"
        assert kwargs["data"]["parse_method"] == "auto"
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            json={
                "results": {
                    "paper.pdf": {
                        "md_content": "# Paper\n\n![fig](images/fig.png)\n",
                        "images": {
                            "fig.png": f"data:image/png;base64,{image_data}",
                            "unused.png": f"data:image/png;base64,{image_data}",
                        },
                    }
                }
            },
            request=request,
        )

    monkeypatch.setattr("paper_plane_x_cli.mineru.httpx.post", fake_post)

    result = MinerUClient("http://mineru").parse_pdf(
        file_path=pdf_path,
        output_md_name="paper.md",
        save_dir=save_dir,
        output_dir=save_dir,
        lang_list=["ch"],
    )

    assert result.md_path == save_dir / "paper.md"
    assert (
        result.md_path.read_text(encoding="utf-8")
        == "# Paper\n\n![fig](images/fig.png)\n"
    )
    assert result.image_paths == [save_dir / "images" / "fig.png"]
    assert (save_dir / "images" / "fig.png").read_bytes() == b"image-bytes"
    assert not (save_dir / "images" / "unused.png").exists()


def test_mineru_parse_command_prints_artifact_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")
    save_dir = tmp_path / "parsed"
    captured: dict[str, Any] = {}

    class FakeMinerUClient:
        def __init__(self, base_url: str):
            captured["base_url"] = base_url

        def parse_pdf(self, **kwargs: Any) -> MinerUOutput:
            captured.update(kwargs)
            md_path = save_dir / "paper.md"
            return MinerUOutput(
                md_content="# Paper\n",
                md_path=md_path,
                image_paths=[save_dir / "images" / "fig.png"],
            )

    monkeypatch.setattr(cli, "MinerUClient", FakeMinerUClient)

    result = runner.invoke(
        cli.app,
        [
            "mineru",
            "parse",
            "--source",
            str(pdf_path),
            "--save-dir",
            str(save_dir),
            "--mineru-url",
            "http://mineru",
            "--lang-list",
            "ch,en",
        ],
    )

    assert result.exit_code == 0
    assert captured["base_url"] == "http://mineru"
    assert captured["file_path"] == pdf_path
    assert captured["output_md_name"] == "paper.md"
    assert captured["save_dir"] == save_dir
    assert captured["output_dir"] == save_dir
    assert captured["lang_list"] == ["ch", "en"]
    payload = json.loads(result.output)
    assert payload == {
        "md_path": str(save_dir / "paper.md"),
        "image_paths": [str(save_dir / "images" / "fig.png")],
    }
