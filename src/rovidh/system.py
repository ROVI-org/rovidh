import click
from .config import RDHSystemConfig, save_config
from .api import *
from pydanclick import from_pydantic


from rovidh.validation import validate_system_name


@click.group(name="system")
def system():
    """CLI for the ROVI Data Hub System Management"""


@system.command("new")
@from_pydantic("rdh_config", RDHSystemConfig)
def new(rdh_config: RDHSystemConfig):
    token = post(rdh_config, f"create_jwt/{rdh_config.vendor_id}/{rdh_config.system_name}", headers=create_headers(rdh_config, token=False, api_key=True)).json().get("token")
    save_config("SYSTEM_NAME", validate_system_name(rdh_config.system_name))
    save_config("VENDOR_ID", rdh_config.vendor_id)
    save_config("SYSTEM_JWT", token)
    click.echo(f"New system token for {rdh_config.system_name}: {token}")


@system.command("renew")
@from_pydantic("rdh_config", RDHSystemConfig)
def renew(rdh_config: RDHSystemConfig):
    token = post(rdh_config, f"renew_jwt", headers=create_headers(rdh_config, token=True, api_key=True)).json().get("token")
    save_config("SYSTEM_JWT", token)
    click.echo(f"Renewed system token for {rdh_config.system_name}: {token}")


@system.command("delete")
@from_pydantic("rdh_config", RDHSystemConfig)
def delete(rdh_config: RDHSystemConfig):
    status = post(rdh_config, f"delete_jwt/{rdh_config.vendor_id}/{rdh_config.system_name}", headers=create_headers(rdh_config, token=True, api_key=True)).json().get("status")
    save_config("SYSTEM_JWT", "")
    click.echo(f"Deleted system {rdh_config.system_name}: {status}")
