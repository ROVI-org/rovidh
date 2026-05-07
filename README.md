# ROVI Data Hub Vendor CLI

Command-line client for vendor and system operations against the ROVI Data Hub API.

The CLI lets you:
- manage vendor API tokens (admin operations),
- create/renew/delete system JWTs,
- upload metadata, files, ONNX models, and Grafana dashboards to ingestion endpoints,
- inspect active configuration loaded from environment files.

## Requirements

- Python 3.11+
- `uv` (recommended) or another Python environment manager
- network access to the ROVI Data Hub API

## Install

### Option 1: with `uv` (recommended)

```bash
uv sync
```

Run commands with:

```bash
uv run rovidh --help
```

### Option 2: with `pip`

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
rovidh --help
```

## Configuration

The app uses environment-based configuration and looks for values in this order (if present):
- `config/.env.default`
- `.env.default`
- `config.env`
- `.env`

You can also pass values directly via CLI options.

### Common variables

| Variable | Required For | Description |
|---|---|---|
| `ROVI_API` | all commands | Base API endpoint (default: `https://rovidatahub.ornl.gov/api`) |
| `VERIFY_SSL` | all commands | SSL verification toggle (`true`/`false`) |
| `ADMIN_KEY` | `admin` commands | Admin access token |
| `VENDOR_NAME` | `admin` commands | Vendor name for token operations |
| `VENDOR_ID` | `system` commands | Vendor identifier |
| `VENDOR_KEY` | `system` commands | Vendor key used as `access-token` header |
| `SYSTEM_NAME` | `system` commands | System name |
| `SYSTEM_JWT` | `system` + `upload` commands | System JWT bearer token |

Example `.env`:

```dotenv
ROVI_API=https://rovidatahub.ornl.gov/api
VERIFY_SSL=true

ADMIN_KEY=...
VENDOR_NAME=example-vendor

VENDOR_ID=...
VENDOR_KEY=...
SYSTEM_NAME=test-system
SYSTEM_JWT=...
```

## Command Groups

Top-level help:

```bash
uv run rovidh --help
```

### `config`

Show active resolved config:

```bash
uv run rovidh config show
```

### `admin`

Create vendor token:

```bash
uv run rovidh admin new
```

Delete vendor token:

```bash
uv run rovidh admin delete
```

### `system`

Create system JWT (also saves `SYSTEM_NAME`, `VENDOR_ID`, and `SYSTEM_JWT` into `.env`):

```bash
uv run rovidh system new
```

Renew current system JWT (updates `SYSTEM_JWT` in `.env`):

```bash
uv run rovidh system renew
```

Delete system JWT:

```bash
uv run rovidh system delete
```

### `upload`

Upload metadata JSON file:

```bash
uv run rovidh upload metadata ./metadata.json
```

Upload single data file:

```bash
uv run rovidh upload file ./payload.json
```

Upload ONNX model:

```bash
uv run rovidh upload model ./model.onnx
```

Upload Grafana dashboard JSON:

```bash
uv run rovidh upload dashboard ./dashboard.json
```

Upload multiple files:

```bash
uv run rovidh upload files ./a.json ./b.json ./c.json
```

Upload all files in a directory:

```bash
uv run rovidh upload directory ./batch
```

## API Endpoints Used

The CLI calls these API paths relative to `ROVI_API`:

- `POST create_token/{vendor_name}`
- `POST delete_token/{vendor_name}`
- `POST create_jwt/{vendor_id}/{system_name}`
- `POST renew_jwt`
- `POST delete_jwt/{vendor_id}/{system_name}`
- `POST upload-metadata/`
- `POST upload-file/`
- `POST upload-model/`
- `POST upload-dashboard/`
- `POST upload-batch/`

## Development

Install editable dependencies and run commands through `uv`:

```bash
uv sync
uv run rovidh --help
```

Run tests:

```bash
uv run pytest
```

Upload tests read `openapi.json` from the repository root when it is present.
That file is local-only and is not required to be committed; OpenAPI-backed
tests skip with a clear message if the file is absent.

## Security Notes

- Do not commit `.env` with live credentials.
- Rotate `ADMIN_KEY`, vendor keys, and JWTs regularly.
- Keep `VERIFY_SSL=true` except in controlled local testing.
