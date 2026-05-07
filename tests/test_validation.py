import pytest
from pydantic import ValidationError

from rovidh.config import RDHSystemConfig
from rovidh.validation import validate_system_name


@pytest.mark.parametrize(
    "system_name",
    [
        "system",
        "SYSTEM",
        "System-Name.1",
        "123.abc-XYZ",
    ],
)
def test_validate_system_name_accepts_openapi_characters(system_name):
    assert validate_system_name(system_name) == system_name


@pytest.mark.parametrize(
    "system_name",
    [
        "",
        "system_name",
        "system name",
        "system/name",
        "system@name",
    ],
)
def test_validate_system_name_rejects_non_openapi_characters(system_name):
    with pytest.raises(ValueError, match="system_name can only contain"):
        validate_system_name(system_name)


def test_system_config_validates_system_name():
    with pytest.raises(ValidationError, match="system_name can only contain"):
        RDHSystemConfig(
            api="https://example.test/api",
            vendor_id="vendor",
            vendor_key="vendor-key",
            system_name="system_name",
        )
