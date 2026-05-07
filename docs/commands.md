# Commands

Run top-level help:

```bash
uv run rovidh --help
```

## config

Show the resolved system configuration:

```bash
uv run rovidh config show
```

## admin

Create a vendor token:

```bash
uv run rovidh admin new
```

Delete a vendor token:

```bash
uv run rovidh admin delete
```

## system

Create a system JWT:

```bash
uv run rovidh system new
```

This command saves `SYSTEM_NAME`, `VENDOR_ID`, and `SYSTEM_JWT` into `.env`.

Renew the current system JWT:

```bash
uv run rovidh system renew
```

Delete a system JWT:

```bash
uv run rovidh system delete
```

## upload

Upload metadata JSON:

```bash
uv run rovidh upload metadata ./metadata.json
```

Upload a single file:

```bash
uv run rovidh upload file ./payload.json
```

Upload an ONNX model:

```bash
uv run rovidh upload model ./model.onnx
```

Upload a Grafana dashboard JSON file:

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

## API paths

The CLI calls these paths relative to `ROVI_API`:

| Command | API path |
| --- | --- |
| `admin new` | `POST create_token/{vendor_name}` |
| `admin delete` | `POST delete_token/{vendor_name}` |
| `system new` | `POST create_jwt/{vendor_id}/{system_name}` |
| `system renew` | `POST renew_jwt` |
| `system delete` | `POST delete_jwt/{vendor_id}/{system_name}` |
| `upload metadata` | `POST upload-metadata/` |
| `upload file` | `POST upload-file/` |
| `upload model` | `POST upload-model/` |
| `upload dashboard` | `POST upload-dashboard/` |
| `upload files` and `upload directory` | `POST upload-batch/` |
