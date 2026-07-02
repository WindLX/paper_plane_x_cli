"""Shared utilities and helpers for the Paper Plane X CLI."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, NoReturn, cast

import httpx
import typer

DEFAULT_BASE_URL = "http://127.0.0.1:8000/api/v1"
GLOBAL_CONTEXT_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
GLOBAL_CONTEXT_PATH = GLOBAL_CONTEXT_DIR / "paper-plane-x" / "context.json"
LOCAL_CONTEXT_PATH = Path.cwd() / ".paper-plane-x" / "context.json"
QueryParamValue = str | int | bool


def fail(message: str, *, status_code: int = 2) -> NoReturn:
    typer.echo(json.dumps({"error": message}, ensure_ascii=False), err=True)
    raise typer.Exit(status_code)


def load_context(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        data_obj: object = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid context file JSON: {path}: {exc}")
    if not isinstance(data_obj, dict):
        fail(f"Invalid context file shape: {path}")
    data = cast(dict[str, object], data_obj)
    return {key: str(value) for key, value in data.items() if value is not None}


def save_context(data: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def resolve_context(
    base_url: str | None = None,
    project_id: str | None = None,
) -> dict[str, str | None]:
    global_ctx = load_context(GLOBAL_CONTEXT_PATH)
    local_ctx = load_context(LOCAL_CONTEXT_PATH)
    merged = {**global_ctx, **local_ctx}
    resolved_base_url = (
        base_url
        or os.environ.get("PPX_BASE_URL")
        or merged.get("base_url")
        or DEFAULT_BASE_URL
    )
    resolved_project_id = (
        project_id or os.environ.get("PPX_PROJECT_ID") or merged.get("project_id")
    )
    return {
        "base_url": resolved_base_url.rstrip("/"),
        "project_id": resolved_project_id,
    }


def print_json(payload: object, *, stream: Any | None = None) -> None:
    stream = stream or sys.stdout
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=stream)


def split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def get_output_md_name(source: Path, output_md_name: str | None) -> str:
    if output_md_name:
        return output_md_name
    return f"{source.stem}.md"


def require_project_id(ctx: dict[str, str | None]) -> str:
    project_id = ctx.get("project_id")
    if not project_id:
        fail("project_id is required. Run: ppx context set --project-id <id>")
    return project_id


def request(
    method: str,
    path: str,
    ctx: dict[str, str | None],
    json_body: object | None = None,
    params: dict[str, QueryParamValue | None] | None = None,
    data: dict[str, str] | None = None,
    files: dict[str, Any] | None = None,
    timeout: float = 60.0,
) -> object:
    response = _request_response(
        method,
        path,
        ctx,
        json_body=json_body,
        params=params,
        data=data,
        files=files,
        timeout=timeout,
    )

    if not response.content:
        return {}
    return response.json()


def request_bytes(
    method: str,
    path: str,
    ctx: dict[str, str | None],
    *,
    timeout: float = 60.0,
) -> bytes:
    response = _request_response(method, path, ctx, timeout=timeout)
    return response.content


def _request_response(
    method: str,
    path: str,
    ctx: dict[str, str | None],
    *,
    json_body: object | None = None,
    params: dict[str, QueryParamValue | None] | None = None,
    data: dict[str, str] | None = None,
    files: dict[str, Any] | None = None,
    timeout: float = 60.0,
) -> httpx.Response:
    base_url = ctx["base_url"]
    url = f"{base_url}{path}"
    cleaned_params = (
        {key: value for key, value in params.items() if value is not None}
        if params
        else None
    )
    try:
        response = httpx.request(
            method,
            url,
            json=json_body,
            params=cleaned_params,
            data=data,
            files=files,
            timeout=timeout,
        )
    except httpx.HTTPError as exc:
        fail(f"HTTP request failed: {exc}", status_code=1)

    if response.status_code >= 400:
        try:
            detail = response.json()
        except json.JSONDecodeError:
            detail = response.text
        fail(
            json.dumps(
                {"status_code": response.status_code, "error": detail},
                ensure_ascii=False,
            ),
            status_code=1,
        )

    return response
