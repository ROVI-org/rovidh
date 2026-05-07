from pathlib import Path
import click
from dotenv import find_dotenv, set_key
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional
from pydanclick import from_pydantic
from .validation import validate_system_name


env_files = (find_dotenv(p, usecwd=True) for p in ("config/.env.default", ".env.default", "config.env", ".env") if find_dotenv(p, raise_error_if_not_found=False, usecwd=True))


def env_field(env_name: str, field_name: str, **kwargs: Any):
    return Field(
        validation_alias=AliasChoices(env_name, field_name),
        json_schema_extra={"env": env_name},
        **kwargs,
    )


class RDHConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_files, env_file_encoding="utf-8", cli_parse_args=True, cli_ignore_unknown_args=True, extra="ignore", case_sensitive=False)
    api: str = env_field("ROVI_API", "api", default="https://rovidatahub.ornl.gov/api", description="ROVI Data Hub API Endpoint")
    verify_ssl: bool = env_field("VERIFY_SSL", "verify_ssl", default=True)
    timeout: int = env_field("TIMEOUT", "timeout", default=30)


class RDHAdminConfig(RDHConfig):
    admin_key: str = env_field("ADMIN_KEY", "admin_key")
    vendor_name: str = env_field("VENDOR_NAME", "vendor_name")


class RDHSystemConfig(RDHConfig):
    vendor_id: str = env_field("VENDOR_ID", "vendor_id")
    vendor_key: str = env_field("VENDOR_KEY", "vendor_key")
    system_name: Optional[str] = env_field("SYSTEM_NAME", "system_name", default=None)
    system_jwt: Optional[str] = env_field("SYSTEM_JWT", "system_jwt", default=None)

    @field_validator("system_name")
    @classmethod
    def validate_system_name_value(cls, value: str | None) -> str | None:
        return validate_system_name(value)


class RDHUploadConfig(RDHConfig):
    system_jwt: str = env_field("SYSTEM_JWT", "system_jwt")


def save_config(setting: str, value: str, settings_file: Path = Path(".env")):
    settings_file.touch(exist_ok=True)
    set_key(settings_file, setting, value)


@click.group(name="config")
def config():
    """CLI for the ROVI Data Hub System Management"""


@config.command("show")
@from_pydantic("rdh_config", RDHSystemConfig)
def show(rdh_config: RDHSystemConfig):
    click.echo(rdh_config.model_dump())
