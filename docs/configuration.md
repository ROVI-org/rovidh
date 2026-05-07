# Configuration

The CLI reads settings from environment variables, environment files, and command-line options. Environment files are discovered from the current working directory in this order:

1. `config/.env.default`
2. `.env.default`
3. `config.env`
4. `.env`

Values can also be passed directly as CLI options generated from the configuration models.

## Common settings

| Variable | Required for | Description |
| --- | --- | --- |
| `ROVI_API` | All commands | Base API endpoint. Defaults to `https://rovidatahub.ornl.gov/api`. |
| `VERIFY_SSL` | All commands | SSL verification toggle, such as `true` or `false`. |
| `TIMEOUT` | All commands | Request timeout in seconds. Defaults to `30`. |
| `ADMIN_KEY` | `admin` commands | Admin access token. |
| `VENDOR_NAME` | `admin` commands | Vendor name for token operations. |
| `VENDOR_ID` | `system` commands | Vendor identifier. |
| `VENDOR_KEY` | `system` commands | Vendor key sent as the `access-token` header. |
| `SYSTEM_NAME` | `system` commands | System name. |
| `SYSTEM_JWT` | `system` and `upload` commands | System JWT bearer token. |

Example `.env`:

```dotenv
ROVI_API=https://rovidatahub.ornl.gov/api
VERIFY_SSL=true
TIMEOUT=30

ADMIN_KEY=...
VENDOR_NAME=example-vendor

VENDOR_ID=...
VENDOR_KEY=...
SYSTEM_NAME=test-system
SYSTEM_JWT=...
```

Do not commit `.env` files containing live credentials.
