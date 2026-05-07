import click
from .system import system
from .upload import upload
from .config import config
from .admin import admin

@click.group()
def cli():
    """CLI for the ROVI Data Hub"""

cli.add_command(system)
cli.add_command(upload)
cli.add_command(config)
cli.add_command(admin)

if __name__ == "__main__":
    cli()
