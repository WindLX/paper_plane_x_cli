"""Install and uninstall bundled Paper Plane X agent skills."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Annotated

import typer

from paper_plane_x_cli.cli.utils import fail, print_json

skills_app = typer.Typer(
    no_args_is_help=True,
    help="Install or uninstall bundled ppx-* agent skills.",
)


def _default_codex_skills_dir() -> Path:
    return Path(os.environ.get("CODEX_HOME", "~/.codex")) / "skills"


def _resolve_target_dir(target_dir: Path | None) -> Path:
    return (target_dir or _default_codex_skills_dir()).expanduser()


def _bundled_skills_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "skills"
        if candidate.exists() and any(candidate.glob("ppx-*/SKILL.md")):
            return candidate
    fail("Could not locate bundled skills directory.", status_code=1)


def _bundled_skill_dirs() -> list[Path]:
    skills_dir = _bundled_skills_dir()
    return sorted(
        candidate
        for candidate in skills_dir.iterdir()
        if candidate.is_dir()
        and candidate.name.startswith("ppx-")
        and (candidate / "SKILL.md").is_file()
    )


def _skill_names() -> set[str]:
    return {skill_dir.name for skill_dir in _bundled_skill_dirs()}


@skills_app.command("list", help="List bundled ppx-* skills.")
def skills_list() -> None:
    print_json({"skills": sorted(_skill_names())})


@skills_app.command(
    "install", help="Install bundled ppx-* skills into a target directory."
)
def skills_install(
    target_dir: Annotated[
        Path | None,
        typer.Option(
            "--target-dir",
            help="Directory that should contain skill folders. Defaults to ${CODEX_HOME:-~/.codex}/skills.",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing ppx-* skill directories."),
    ] = False,
) -> None:
    target_dir = _resolve_target_dir(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    skipped: list[str] = []

    for source_dir in _bundled_skill_dirs():
        destination = target_dir / source_dir.name
        if destination.exists():
            if not force:
                skipped.append(source_dir.name)
                continue
            shutil.rmtree(destination)
        shutil.copytree(source_dir, destination)
        installed.append(source_dir.name)

    print_json(
        {
            "target_dir": str(target_dir),
            "installed": installed,
            "skipped": skipped,
        }
    )


@skills_app.command(
    "uninstall", help="Remove bundled ppx-* skills from a target directory."
)
def skills_uninstall(
    target_dir: Annotated[
        Path | None,
        typer.Option(
            "--target-dir",
            help="Directory that contains installed skill folders. Defaults to ${CODEX_HOME:-~/.codex}/skills.",
        ),
    ] = None,
) -> None:
    target_dir = _resolve_target_dir(target_dir)
    if not target_dir.exists():
        print_json({"target_dir": str(target_dir), "removed": [], "missing": []})
        return

    removed: list[str] = []
    missing: list[str] = []
    for skill_name in sorted(_skill_names()):
        destination = target_dir / skill_name
        if not destination.exists():
            missing.append(skill_name)
            continue
        if not destination.is_dir() or not (destination / "SKILL.md").is_file():
            fail(f"Refusing to remove non-skill path: {destination}", status_code=1)
        shutil.rmtree(destination)
        removed.append(skill_name)

    print_json(
        {
            "target_dir": str(target_dir),
            "removed": removed,
            "missing": missing,
        }
    )
