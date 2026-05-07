# ROVI Data Hub Vendor CLI

`rovidh` is a Python command-line client for ROVI Data Hub vendor, system, and upload operations. It wraps the API calls needed to manage vendor tokens, create and renew system JWTs, upload supported payloads, and inspect the active runtime configuration.

## What it does

- Manage vendor API tokens with admin credentials.
- Create, renew, and delete system JWTs.
- Upload metadata JSON, regular files, ONNX models, Grafana dashboard JSON, and batches of files.
- Load configuration from local environment files and command-line options.

## Requirements

- Python 3.11 or newer.
- `uv` for the recommended development workflow.
- Network access to the ROVI Data Hub API.
- API credentials for the command group you are using.

## Quick start

Install dependencies:

```bash
uv sync
```

Check the CLI:

```bash
uv run rovidh --help
```

Create a `.env` file with the variables needed for your workflow, then run a command:

```bash
uv run rovidh config show
```

See the installation, configuration, and commands pages for the full workflow.
