# Development

## Set up

Install project and development dependencies:

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```

Build the docs:

```bash
uv run mkdocs build --strict
```

Serve the docs locally while editing:

```bash
uv run mkdocs serve
```

## Continuous integration

The repository has three GitHub Actions workflows:

| Workflow | Purpose |
| --- | --- |
| `CI` | Runs the test suite and a strict MkDocs build on pull requests and pushes to `main`. |
| `Publish PyPI` | Runs tests, builds distributions, and publishes to PyPI on pushes to `main`. The publish job is skipped if tests fail because it depends on the test job. |
| `Deploy Docs` | Builds MkDocs and deploys the generated site to GitHub Pages on pushes to `main`. The deploy job depends on the build job, so a MkDocs failure blocks deployment. |

## PyPI releases

Publishing uses PyPI Trusted Publishing through GitHub Actions. Configure a Trusted Publisher on PyPI for this repository, the `Publish PyPI` workflow, and the `pypi` environment before relying on automated uploads.

The workflow publishes the files generated in `dist/`. PyPI rejects duplicate versions, so update `project.version` in `pyproject.toml` before pushing a new release to `main`.

## GitHub Pages

The docs workflow builds the site from `docs/` using `mkdocs.yml`, uploads the generated `site/` directory as a Pages artifact, and deploys it to the `github-pages` environment. In the repository settings, configure GitHub Pages to use GitHub Actions as the source.
