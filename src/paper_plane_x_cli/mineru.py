"""Standalone MinerU HTTP client for PDF-to-Markdown conversion."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, cast
from urllib.parse import unquote, urlparse

import httpx


class MinerUBackend(str, Enum):
    PIPELINE = "pipeline"
    VLM_AUTO = "vlm-auto-engine"
    VLM_HTTP = "vlm-http-client"
    HYBRID_AUTO = "hybrid-auto-engine"


class MinerUParseMethod(str, Enum):
    AUTO = "auto"
    TXT = "txt"
    OCR = "ocr"


@dataclass(frozen=True)
class MinerUOutput:
    md_content: str
    md_path: Path
    image_paths: list[Path]


class MinerUClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.parse_endpoint = f"{self.base_url}/file_parse"

    def parse_pdf(
        self,
        file_path: str | Path,
        output_md_name: str,
        save_dir: str | Path,
        output_dir: str | Path,
        lang_list: list[str],
        backend: MinerUBackend = MinerUBackend.HYBRID_AUTO,
        parse_method: MinerUParseMethod = MinerUParseMethod.AUTO,
        formula_enable: bool = True,
        table_enable: bool = True,
        server_url: str | None = None,
        return_md: bool = True,
        return_middle_json: bool = False,
        return_model_output: bool = False,
        return_content_list: bool = False,
        return_images: bool = True,
        response_format_zip: bool = False,
        start_page_id: int = 0,
        end_page_id: int = 99999,
        timeout: float = 300.0,
    ) -> MinerUOutput:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"PDF path is not a file: {file_path}")

        payload: dict[str, Any] = {
            "output_dir": str(output_dir),
            "backend": backend.value,
            "parse_method": parse_method.value,
            "formula_enable": _bool_text(formula_enable),
            "table_enable": _bool_text(table_enable),
            "return_md": _bool_text(return_md),
            "return_middle_json": _bool_text(return_middle_json),
            "return_model_output": _bool_text(return_model_output),
            "return_content_list": _bool_text(return_content_list),
            "return_images": _bool_text(return_images),
            "response_format_zip": _bool_text(response_format_zip),
            "start_page_id": str(start_page_id),
            "end_page_id": str(end_page_id),
            "lang_list": lang_list,
        }
        if server_url:
            payload["server_url"] = server_url

        with file_path.open("rb") as file_obj:
            files = {"files": (file_path.name, file_obj, "application/pdf")}
            response = httpx.post(
                self.parse_endpoint,
                data=payload,
                files=files,
                timeout=timeout,
            )

        if response.status_code != 200:
            raise RuntimeError(f"HTTP Error {response.status_code}: {response.text}")

        return self._parse_response(response, output_md_name, save_dir)

    def load_md(self, md_name: str, save_dir: str | Path) -> MinerUOutput:
        save_dir = Path(save_dir)
        md_path = save_dir / md_name
        if not md_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {md_path}")

        md_content = md_path.read_text(encoding="utf-8")
        image_paths = self._get_image_paths(md_content, save_dir / "images")
        return MinerUOutput(
            md_content=md_content, md_path=md_path, image_paths=image_paths
        )

    def _parse_response(
        self,
        response: httpx.Response,
        output_md_name: str,
        save_dir: str | Path,
    ) -> MinerUOutput:
        data = cast(dict[str, Any], response.json())
        results = data.get("results")

        if not results or not isinstance(results, dict):
            raise ValueError(
                "Invalid response format: 'results' field missing or invalid"
            )

        results_dict = cast(dict[str, Any], results)
        try:
            first_file_result = next(iter(results_dict.values()))
        except StopIteration:
            raise ValueError("Invalid response format: 'results' is empty") from None

        if not isinstance(first_file_result, dict):
            raise ValueError("Invalid result format: expected a dictionary")

        first_result_dict = cast(dict[str, Any], first_file_result)
        md_content = first_result_dict.get("md_content")

        if not md_content or not isinstance(md_content, str):
            raise ValueError(
                "'md_content' not found or invalid in result. Keys: "
                f"{list(first_result_dict.keys())}"
            )

        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        md_path = save_dir / output_md_name
        md_path.write_text(md_content, encoding="utf-8")

        image_save_dir = save_dir / "images"
        image_save_dir.mkdir(parents=True, exist_ok=True)
        self._decode_images(first_result_dict.get("images", {}), image_save_dir)
        self._prune_unreferenced_images(md_content, image_save_dir)
        image_paths = self._get_image_paths(md_content, image_save_dir)

        return MinerUOutput(
            md_content=md_content, md_path=md_path, image_paths=image_paths
        )

    def _decode_images(self, images_info_raw: object, image_save_dir: Path) -> None:
        if not isinstance(images_info_raw, dict):
            return

        for img_name, img_data in cast(dict[Any, Any], images_info_raw).items():
            if not isinstance(img_name, str) or not isinstance(img_data, str):
                continue
            if not img_data.startswith("data:image"):
                continue
            base64_data = img_data.split(",", 1)[1]
            img_bytes = base64.b64decode(base64_data)
            (image_save_dir / img_name).write_bytes(img_bytes)

    def _get_image_paths(self, md_content: str, image_dir: Path) -> list[Path]:
        if not image_dir.exists():
            return []

        referenced_names = self._extract_referenced_image_names(md_content)
        image_paths: list[Path] = []
        for file_name in sorted(referenced_names):
            candidate = image_dir / file_name
            if candidate.exists() and candidate.is_file():
                image_paths.append(candidate)
        return image_paths

    def _prune_unreferenced_images(self, md_content: str, image_dir: Path) -> None:
        if not image_dir.exists():
            return

        referenced_names = self._extract_referenced_image_names(md_content)
        for candidate in image_dir.iterdir():
            if candidate.is_file() and candidate.name not in referenced_names:
                candidate.unlink(missing_ok=True)

    def _extract_referenced_image_names(self, md_content: str) -> set[str]:
        references: set[str] = set()

        md_pattern = r"!\[[^\]]*\]\(([^)]+)\)"
        html_pattern = r"<img[^>]+src=[\"']([^\"']+)[\"'][^>]*>"

        for raw_ref in cast(list[str], re.findall(md_pattern, md_content)):
            ref = raw_ref.strip()
            if " " in ref:
                ref = ref.split(" ", 1)[0]
            ref = ref.strip("<>'\"")
            parsed_path = Path(unquote(urlparse(ref).path))
            if parsed_path.name:
                references.add(parsed_path.name)

        for raw_ref in cast(
            list[str],
            re.findall(html_pattern, md_content, flags=re.IGNORECASE),
        ):
            ref = raw_ref.strip("<>'\"")
            parsed_path = Path(unquote(urlparse(ref).path))
            if parsed_path.name:
                references.add(parsed_path.name)

        return references


def _bool_text(value: bool) -> str:
    return str(value).lower()
