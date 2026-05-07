# Installation

## With uv

The repository is set up for `uv`:

```bash
uv sync
uv run rovidh --help
```

Use `uv run` for commands during development so the project environment and lockfile stay consistent.

## With pip

You can also install the package into a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
rovidh --help
```

## From PyPI

After a release has been published, install the package directly:

```bash
pip install rovidh
rovidh --help
```

PyPI does not allow replacing an already published version. Bump `project.version` in `pyproject.toml` before pushing a new release to `main`.
