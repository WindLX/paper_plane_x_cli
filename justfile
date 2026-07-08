set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

default:
    @just --list

setup:
    uv sync

run *args:
    uv run ppx {{args}}

test *args:
    uv run pytest {{args}}

lint:
    uv run ruff check src tests

lint-fix:
    uv run ruff check src tests --fix

format:
    uv run ruff format src tests

format-check:
    uv run ruff format --check src tests

typecheck:
    uv run pyright

build:
    uv build

pre-commit:
    just lint
    just format-check
    just typecheck
    just test
