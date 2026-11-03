from contextlib import ExitStack
import mimetypes
from pathlib import Path
from typing import Iterable

import click
from pydanclick import from_pydantic
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .config import RDHUploadConfig
from .api import create_headers, post

JSON_CONTENT_TYPE = "application/json"
BINARY_CONTENT_TYPE = "application/octet-stream"
MAX_UPLOAD_BYTES = 1 * 1024**3  # 1 GiB


def content_type_for(path: Path, default: str = BINARY_CONTENT_TYPE) -> str:
    return mimetypes.guess_type(path.name)[0] or default


def validate_extension(path: Path, extension: str) -> None:
    if path.suffix.lower() != extension:
        raise click.ClickException(f"{path} must be a {extension} file")


def validate_file_size(path: Path, max_bytes: int = MAX_UPLOAD_BYTES) -> None:
    size = path.stat().st_size
    if size > max_bytes:
        raise click.ClickException(
            f"{path} is {size:,} bytes, which exceeds the 1GB upload limit. "
            "Break the file into smaller pieces (each 1GB or less) and upload them separately."
        )


def multipart_headers(rdh_config: RDHUploadConfig, encoder: MultipartEncoder) -> dict:
    headers = create_headers(rdh_config, token=True)
    headers["Content-Type"] = encoder.content_type
    return headers


def upload_files(
    rdh_config: RDHUploadConfig,
    endpoint: str,
    paths: Iterable[Path],
    field_name: str,
    content_type: str | None = None,
) -> None:
    paths = list(paths)
    if not paths:
        raise click.ClickException("At least one file is required.")

    for path in paths:
        validate_file_size(path)

    with ExitStack() as stack:
        fields = [
            (
                field_name,
                (
                    path.name,
                    stack.enter_context(path.open("rb")),
                    content_type or content_type_for(path),
                ),
            )
            for path in paths
        ]
        encoder = MultipartEncoder(fields=fields)
        post(rdh_config, endpoint, data=encoder, headers=multipart_headers(rdh_config, encoder))


@click.group(name="upload")
def upload():
    """CLI for the ROVI Data Hub Upload"""


@upload.command("metadata")
@from_pydantic("rdh_config", RDHUploadConfig)
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def metadata(rdh_config: RDHUploadConfig, file: Path):
    upload_files(rdh_config, "upload-metadata/", [file], "file", JSON_CONTENT_TYPE)
    click.echo(f"Metadata uploaded: {file}")


@upload.command("file")
@from_pydantic("rdh_config", RDHUploadConfig)
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def file(rdh_config: RDHUploadConfig, file: Path):
    upload_files(rdh_config, "upload-file/", [file], "file")
    click.echo(f"File uploaded: {file}")


@upload.command("model")
@from_pydantic("rdh_config", RDHUploadConfig)
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def model(rdh_config: RDHUploadConfig, file: Path):
    validate_extension(file, ".onnx")
    upload_files(rdh_config, "upload-model/", [file], "file", BINARY_CONTENT_TYPE)
    click.echo(f"Model uploaded: {file}")


@upload.command("dashboard")
@from_pydantic("rdh_config", RDHUploadConfig)
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def dashboard(rdh_config: RDHUploadConfig, file: Path):
    validate_extension(file, ".json")
    upload_files(rdh_config, "upload-dashboard/", [file], "file", JSON_CONTENT_TYPE)
    click.echo(f"Dashboard uploaded: {file}")


@upload.command("files")
@from_pydantic("rdh_config", RDHUploadConfig)
@click.argument("files", type=click.Path(exists=True, dir_okay=False, path_type=Path), nargs=-1, required=True)
def files(rdh_config: RDHUploadConfig, files: tuple[Path, ...]):
    upload_files(rdh_config, "upload-batch/", files, "files")
    click.echo(f"Files uploaded: {', '.join(str(file) for file in files)}")


@upload.command("directory")
@from_pydantic("rdh_config", RDHUploadConfig)
@click.argument("dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
def directory(rdh_config: RDHUploadConfig, dir: Path):
    upload_files(rdh_config, "upload-batch/", (file for file in dir.iterdir() if file.is_file()), "files")
    click.echo(f"Files uploaded from directory: {dir}")
