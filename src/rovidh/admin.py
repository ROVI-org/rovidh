import click
from .config import RDHAdminConfig
from .api import *
from pydanclick import from_pydantic

@click.group(name="admin")
def admin():
    """CLI for the ROVI Data Hub Admin Management"""

def admin_headers(key: str) -> dict:
    return {
        "Content-Type": "application/json",
        "access-token": key
    }


@admin.command("new")
@from_pydantic("rdh_config", RDHAdminConfig)
def new(rdh_config: RDHAdminConfig):
    token = post(rdh_config, f"create_token/{rdh_config.vendor_name}", headers=admin_headers(rdh_config.admin_key)).json().get("token")
    click.echo(f"New vendor token for {rdh_config.vendor_name}: {token}")


@admin.command("delete")
@from_pydantic("rdh_config", RDHAdminConfig)
def delete(rdh_config: RDHAdminConfig):
    status = post(rdh_config, f"delete_token/{rdh_config.vendor_name}", headers=admin_headers(rdh_config.admin_key)).json().get("status")
    click.echo(f"Deleted vendor token for {rdh_config.vendor_name}: {status}")
