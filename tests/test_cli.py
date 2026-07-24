import json
from pathlib import Path
from typing import Any

import httpx
from typer.testing import CliRunner

from paper_plane_x_cli import cli
from paper_plane_x_cli.cli import context as context_commands

runner = CliRunner()


def set_context_paths(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    global_context_path = tmp_path / "global" / "context.json"
    local_context_path = tmp_path / "local" / "context.json"
    monkeypatch.setattr(cli, "GLOBAL_CONTEXT_PATH", global_context_path)
    monkeypatch.setattr(cli, "LOCAL_CONTEXT_PATH", local_context_path)
    return global_context_path, local_context_path


def test_context_precedence_args_env_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    global_context_path, local_context_path = set_context_paths(monkeypatch, tmp_path)
    global_context_path.parent.mkdir(parents=True)
    global_context_path.write_text(
        json.dumps(
            {
                "base_url": "http://global/api/v1",
                "project_id": "global-project",
            }
        ),
        encoding="utf-8",
    )
    local_context_path.parent.mkdir(parents=True)
    local_context_path.write_text(
        json.dumps(
            {
                "project_id": "local-project",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("PPX_BASE_URL", "http://env/api/v1")
    monkeypatch.setenv("PPX_PROJECT_ID", "env-project")

    assert cli.resolve_context(
        base_url="http://arg/api/v1",
        project_id="arg-project",
    ) == {
        "base_url": "http://arg/api/v1",
        "project_id": "arg-project",
    }


def test_context_precedence_env_local_global(
    tmp_path: Path,
    monkeypatch,
) -> None:
    global_context_path, local_context_path = set_context_paths(monkeypatch, tmp_path)
    global_context_path.parent.mkdir(parents=True)
    global_context_path.write_text(
        json.dumps(
            {
                "base_url": "http://global/api/v1",
                "project_id": "global-project",
                "custom_key": "global-value",
            }
        ),
        encoding="utf-8",
    )
    local_context_path.parent.mkdir(parents=True)
    local_context_path.write_text(
        json.dumps(
            {
                "project_id": "local-project",
                "custom_key": "local-value",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("PPX_PROJECT_ID", "env-project")
    monkeypatch.setenv("PPX_CUSTOM_KEY", "env-value")

    assert cli.resolve_context() == {
        "base_url": "http://global/api/v1",
        "project_id": "env-project",
        "custom_key": "env-value",
    }


def test_explicit_null_project_id_blocks_lower_priority_values(
    tmp_path: Path,
    monkeypatch,
) -> None:
    global_context_path, local_context_path = set_context_paths(monkeypatch, tmp_path)
    global_context_path.parent.mkdir(parents=True)
    global_context_path.write_text(
        json.dumps({"project_id": "global-project"}),
        encoding="utf-8",
    )
    local_context_path.parent.mkdir(parents=True)
    local_context_path.write_text(
        json.dumps({"project_id": None}),
        encoding="utf-8",
    )

    assert cli.resolve_context()["project_id"] is None

    for null_value in ("none", "null", "None", "NULL"):
        monkeypatch.setenv("PPX_PROJECT_ID", null_value)
        assert cli.resolve_context()["project_id"] is None
        assert cli.resolve_context(project_id=null_value)["project_id"] is None


def test_context_set_defaults_to_local_and_global_is_explicit(
    tmp_path: Path,
    monkeypatch,
) -> None:
    global_context_path, local_context_path = set_context_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(context_commands, "GLOBAL_CONTEXT_PATH", global_context_path)
    monkeypatch.setattr(context_commands, "LOCAL_CONTEXT_PATH", local_context_path)

    local_result = runner.invoke(
        cli.app,
        ["context", "set", "--project-id", "local-project"],
    )
    global_result = runner.invoke(
        cli.app,
        ["context", "set", "--global", "--project-id", "global-project"],
    )

    assert local_result.exit_code == 0
    assert global_result.exit_code == 0
    assert json.loads(local_context_path.read_text())["project_id"] == "local-project"
    assert json.loads(global_context_path.read_text())["project_id"] == "global-project"


def test_context_set_clears_project_id_with_explicit_null(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _, local_context_path = set_context_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(context_commands, "LOCAL_CONTEXT_PATH", local_context_path)
    local_context_path.parent.mkdir(parents=True)
    local_context_path.write_text(
        json.dumps({"project_id": "local-project"}),
        encoding="utf-8",
    )

    result = runner.invoke(
        cli.app,
        ["context", "set", "--project-id", "NULL"],
    )

    assert result.exit_code == 0
    assert "project_id" not in json.loads(local_context_path.read_text())


def test_cli_help_exits_successfully() -> None:
    result = runner.invoke(cli.app, ["--help"])

    assert result.exit_code == 0
    output = result.output
    assert "Usage:" in output
    assert "Paper Plane X HTTP CLI" in output
    assert "Override API base URL" in output


def test_nested_command_help_includes_descriptions() -> None:
    result = runner.invoke(cli.app, ["files", "upload", "--help"])

    output = result.output
    assert result.exit_code == 0
    assert "Upload a local file into the project sandbox" in output
    assert "Local file to upload" in output
    assert "Sandbox destination path" in output


def test_paper_markdown_help_is_registered() -> None:
    result = runner.invoke(cli.app, ["paper", "markdown", "--help"])

    assert result.exit_code == 0
    assert "Download a paper's parsed Markdown text" in result.output
    assert "Directory where the Markdown" in result.output


def test_cli_no_args_shows_help_without_traceback() -> None:
    result = runner.invoke(cli.app)

    assert result.exit_code == 2
    assert "Usage:" in result.output
    assert "Traceback" not in result.output


def test_skills_install_and_uninstall(tmp_path: Path) -> None:
    target_dir = tmp_path / "skills"

    install_result = runner.invoke(
        cli.app,
        ["skills", "install", "--target-dir", str(target_dir)],
    )

    assert install_result.exit_code == 0
    install_payload = json.loads(install_result.output)
    assert "ppx-researcher" in install_payload["installed"]
    assert (target_dir / "ppx-researcher" / "SKILL.md").exists()
    assert (target_dir / "ppx-pdf-to-markdown" / "SKILL.md").exists()
    assert "ppx paper markdown" in (
        target_dir / "ppx-researcher" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "ppx paper markdown" in (
        target_dir / "ppx-pdf-to-markdown" / "SKILL.md"
    ).read_text(encoding="utf-8")

    second_install = runner.invoke(
        cli.app,
        ["skills", "install", "--target-dir", str(target_dir)],
    )

    assert second_install.exit_code == 0
    second_payload = json.loads(second_install.output)
    assert "ppx-researcher" in second_payload["skipped"]

    uninstall_result = runner.invoke(
        cli.app,
        ["skills", "uninstall", "--target-dir", str(target_dir)],
    )

    assert uninstall_result.exit_code == 0
    uninstall_payload = json.loads(uninstall_result.output)
    assert "ppx-researcher" in uninstall_payload["removed"]
    assert not (target_dir / "ppx-researcher").exists()


def test_skills_install_defaults_to_codex_skills_dir(
    tmp_path: Path,
    monkeypatch,
) -> None:
    home_dir = tmp_path / "home"
    monkeypatch.delenv("CODEX_HOME", raising=False)
    monkeypatch.setenv("HOME", str(home_dir))

    install_result = runner.invoke(cli.app, ["skills", "install"])

    assert install_result.exit_code == 0
    payload = json.loads(install_result.output)
    target_dir = home_dir / ".codex" / "skills"
    assert payload["target_dir"] == str(target_dir)
    assert (target_dir / "ppx-researcher" / "SKILL.md").exists()
    assert (target_dir / "ppx-pdf-to-markdown" / "SKILL.md").exists()


def test_skills_install_respects_codex_home(
    tmp_path: Path,
    monkeypatch,
) -> None:
    codex_home = tmp_path / "codex-home"
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    install_result = runner.invoke(cli.app, ["skills", "install"])

    assert install_result.exit_code == 0
    payload = json.loads(install_result.output)
    target_dir = codex_home / "skills"
    assert payload["target_dir"] == str(target_dir)
    assert (target_dir / "ppx-researcher" / "SKILL.md").exists()


def test_command_group_without_subcommand_shows_help() -> None:
    result = runner.invoke(cli.app, ["context"])

    assert result.exit_code == 2
    assert "Usage:" in result.output
    assert "context" in result.output
    assert "Traceback" not in result.output


def test_librarian_search_builds_http_request(
    tmp_path: Path,
    monkeypatch,
) -> None:
    global_context_path, _ = set_context_paths(monkeypatch, tmp_path)
    global_context_path.parent.mkdir(parents=True)
    global_context_path.write_text(
        json.dumps(
            {
                "base_url": "http://server/api/v1",
                "project_id": "proj-1",
            }
        ),
        encoding="utf-8",
    )
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

    result = runner.invoke(
        cli.app,
        [
            "librarian",
            "search",
            "--query-expr",
            "(meta.title CONTAINS test)",
            "--limit",
            "5",
        ],
    )

    assert result.exit_code == 0
    assert captured["method"] == "POST"
    assert captured["url"] == "http://server/api/v1/librarian/search"
    assert captured["json"]["project_id"] == "proj-1"
    assert captured["json"]["limit"] == 5
    assert json.loads(result.output)["paper_ids"] == ["p1"]


def test_librarian_deep_dive_uses_long_default_timeout(
    monkeypatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        captured.update({"method": method, "url": url, **kwargs})
        return httpx.Response(
            200,
            json={
                "paper_id": "p1",
                "question": "q",
                "answer": {"is_answered": False, "answer": {}},
            },
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)

    result = runner.invoke(
        cli.app,
        [
            "librarian",
            "deep-dive",
            "--paper-id",
            "p1",
            "--question",
            "q",
        ],
    )

    assert result.exit_code == 0
    assert captured["timeout"] == 600


def test_librarian_deep_dive_timeout_explains_outer_timeout(
    monkeypatch,
) -> None:
    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    monkeypatch.setattr(cli.httpx, "request", fake_request)

    result = runner.invoke(
        cli.app,
        [
            "librarian",
            "deep-dive",
            "--paper-id",
            "p1",
            "--question",
            "q",
            "--timeout",
            "5",
        ],
    )

    assert result.exit_code == 1
    assert "timed out after 5s" in result.output
    assert "outer tool execution timeout" in result.output


def test_files_upload_builds_multipart_request(
    tmp_path: Path,
    monkeypatch,
) -> None:
    global_context_path, _ = set_context_paths(monkeypatch, tmp_path)
    global_context_path.parent.mkdir(parents=True)
    global_context_path.write_text(
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

    result = runner.invoke(
        cli.app,
        [
            "files",
            "upload",
            "--source",
            str(source_path),
            "--path",
            "/notes/local.md",
        ],
    )

    assert result.exit_code == 0
    assert captured["method"] == "POST"
    assert captured["url"] == "http://server/api/v1/projects/proj-1/files/upload"
    assert captured["data"]["file_path"] == "/notes/local.md"
    assert captured["uploaded_name"] == "local.md"
    assert captured["uploaded_content"] == b"# Local\n"
    assert json.loads(result.output)["file_path"] == "/notes/local.md"


def test_cli_reports_http_error(
    monkeypatch,
) -> None:
    def fake_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
        request = httpx.Request(method, url)
        return httpx.Response(
            422,
            json={"detail": {"code": "invalid_field"}},
            request=request,
        )

    monkeypatch.setattr(cli.httpx, "request", fake_request)

    result = runner.invoke(
        cli.app,
        [
            "--project-id",
            "proj-1",
            "librarian",
            "search",
            "--query-expr",
            "(bad CONTAINS x)",
        ],
    )

    assert result.exit_code == 1
    assert "invalid_field" in result.output
