import re

SYSTEM_NAME_PATTERN = r"^[A-Za-z0-9.-]+$"
SYSTEM_NAME_ALLOWED_CHARACTERS = "uppercase letters, lowercase letters, numbers, dashes, and dots"

_SYSTEM_NAME_RE = re.compile(SYSTEM_NAME_PATTERN)


def validate_system_name(system_name: str | None) -> str | None:
    """Validate that the system name is valid according to the ROVI Data Hub System Management API."""
    if system_name is None:
        return system_name

    if not _SYSTEM_NAME_RE.fullmatch(system_name):
        raise ValueError(f"system_name can only contain {SYSTEM_NAME_ALLOWED_CHARACTERS}")

    return system_name
