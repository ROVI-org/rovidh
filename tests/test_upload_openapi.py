import importlib
from pathlib import Path

import pytest
from click.testing import CliRunner


SINGLE_UPLOAD_COMMANDS = [
    ("metadata", "/upload-metadata/", "metadata.json", "application/json"),
    ("file", "/upload-file/", "payload.json", "application/json"),
    ("model", "/upload-model/", "model.onnx", "application/octet-stream"),
    ("dashboard", "/upload-dashboard/", "dashboard.json", "application/json"),
]


def upload_module():
    return importlib.import_module("rovidh.upload")


def fake_file_sizes(monkeypatch, sizes: dict[Path, int]):
    original_stat = Path.stat

    class StatProxy:
        def __init__(self, real, size):
            self._real = real
            self.st_size = size

        def __getattr__(self, name):
            return getattr(self._real, name)

    def fake_stat(self, *args, **kwargs):
        result = original_stat(self, *args, **kwargs)
        for path, size in sizes.items():
            if self == path:
                return StatProxy(result, size)
        return result

    monkeypatch.setattr(Path, "stat", fake_stat)


def upload_schema(openapi_spec, endpoint):
    path_spec = openapi_spec["paths"][endpoint]["post"]
    return path_spec["requestBody"]["content"]["multipart/form-data"]["schema"]


def resolved_upload_schema(openapi_spec, endpoint):
    schema = upload_schema(openapi_spec, endpoint)
    ref = schema.get("$ref")
    if not ref:
        return schema

    _, _, schema_name = ref.rpartition("/")
    return openapi_spec["components"]["schemas"][schema_name]


def required_field(openapi_spec, endpoint):
    schema = resolved_upload_schema(openapi_spec, endpoint)
    required = schema["required"]
    assert len(required) == 1
    return required[0]


def capture_posts(monkeypatch):
    captured = []

    def fake_post(rdh_config, endpoint, data=None, headers=None):
        data.to_string()
        captured.append(
            {
                "endpoint": endpoint,
                "fields": data.fields,
                "headers": headers,
                "jwt": rdh_config.system_jwt,
            }
        )

    monkeypatch.setattr(upload_module(), "post", fake_post)
    return captured


@pytest.mark.parametrize(
    ("endpoint", "field_name", "is_array"),
    [
        ("/upload-metadata/", "file", False),
        ("/upload-file/", "file", False),
        ("/upload-model/", "file", False),
        ("/upload-dashboard/", "file", False),
        ("/upload-batch/", "files", True),
    ],
)
def test_openapi_upload_contracts_are_multipart_binary(openapi_spec, endpoint, field_name, is_array):
    schema = resolved_upload_schema(openapi_spec, endpoint)

    assert upload_schema(openapi_spec, endpoint) == {
        "$ref": f"#/components/schemas/{schema['title']}"
    }
    assert required_field(openapi_spec, endpoint) == field_name

    field_schema = schema["properties"][field_name]
    if is_array:
        assert field_schema["type"] == "array"
        assert field_schema["items"] == {"type": "string", "format": "binary"}
    else:
        assert field_schema == {"type": "string", "format": "binary", "title": "File"}


@pytest.mark.parametrize(
    ("command", "endpoint", "filename", "expected_content_type"),
    SINGLE_UPLOAD_COMMANDS,
)
def test_single_upload_commands_post_multipart_matching_openapi(
    tmp_path,
    monkeypatch,
    openapi_spec,
    command,
    endpoint,
    filename,
    expected_content_type,
):
    file_path = tmp_path / filename
    file_path.write_bytes(b"upload-content")
    captured = capture_posts(monkeypatch)

    result = CliRunner().invoke(
        upload_module().upload,
        [command, "--system-jwt", "test-jwt", str(file_path)],
    )

    assert result.exit_code == 0, result.output
    assert len(captured) == 1
    post_call = captured[0]
    field_name, field_value = post_call["fields"][0]

    assert post_call["endpoint"] == endpoint.lstrip("/")
    assert post_call["jwt"] == "test-jwt"
    assert post_call["headers"]["Authorization"] == "Bearer test-jwt"
    assert post_call["headers"]["Content-Type"].startswith("multipart/form-data; boundary=")
    assert field_name == required_field(openapi_spec, endpoint)
    assert field_value[0] == filename
    assert field_value[2] == expected_content_type


def test_batch_upload_uses_repeated_files_field_from_openapi(tmp_path, monkeypatch, openapi_spec):
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    first.write_text("{}", encoding="utf-8")
    second.write_text("{}", encoding="utf-8")
    captured = capture_posts(monkeypatch)

    result = CliRunner().invoke(
        upload_module().upload,
        ["files", "--system-jwt", "test-jwt", str(first), str(second)],
    )

    assert result.exit_code == 0, result.output
    assert len(captured) == 1
    post_call = captured[0]
    field_name = required_field(openapi_spec, "/upload-batch/")

    assert post_call["endpoint"] == "upload-batch/"
    assert [field[0] for field in post_call["fields"]] == [field_name, field_name]
    assert [field[1][0] for field in post_call["fields"]] == ["a.json", "b.json"]
    assert all(field[1][2] == "application/json" for field in post_call["fields"])


def test_directory_upload_rejects_empty_directory_before_posting(tmp_path, monkeypatch):
    captured = capture_posts(monkeypatch)

    result = CliRunner().invoke(
        upload_module().upload,
        ["directory", "--system-jwt", "test-jwt", str(tmp_path)],
    )

    assert result.exit_code == 1
    assert "At least one file is required." in result.output
    assert captured == []


def test_model_upload_rejects_non_onnx_before_posting(tmp_path, monkeypatch):
    bad_model = tmp_path / "model.json"
    bad_model.write_text("{}", encoding="utf-8")
    captured = capture_posts(monkeypatch)

    result = CliRunner().invoke(
        upload_module().upload,
        ["model", "--system-jwt", "test-jwt", str(bad_model)],
    )

    assert result.exit_code == 1
    assert "must be a .onnx file" in result.output
    assert captured == []


def test_dashboard_upload_rejects_non_json_before_posting(tmp_path, monkeypatch):
    bad_dashboard = tmp_path / "dashboard.txt"
    bad_dashboard.write_text("{}", encoding="utf-8")
    captured = capture_posts(monkeypatch)

    result = CliRunner().invoke(
        upload_module().upload,
        ["dashboard", "--system-jwt", "test-jwt", str(bad_dashboard)],
    )

    assert result.exit_code == 1
    assert "must be a .json file" in result.output
    assert captured == []


def test_upload_rejects_file_larger_than_1gb_before_posting(tmp_path, monkeypatch):
    oversized = tmp_path / "huge.bin"
    oversized.write_bytes(b"x")
    captured = capture_posts(monkeypatch)
    fake_file_sizes(monkeypatch, {oversized: upload_module().MAX_UPLOAD_BYTES + 1})

    result = CliRunner().invoke(
        upload_module().upload,
        ["file", "--system-jwt", "test-jwt", str(oversized)],
    )

    assert result.exit_code == 1
    assert "exceeds the 1GB upload limit" in result.output
    assert "Break the file into smaller pieces" in result.output
    assert captured == []


def test_upload_allows_file_exactly_1gb(tmp_path, monkeypatch):
    boundary = tmp_path / "boundary.bin"
    boundary.write_bytes(b"x")
    captured = capture_posts(monkeypatch)
    fake_file_sizes(monkeypatch, {boundary: upload_module().MAX_UPLOAD_BYTES})

    result = CliRunner().invoke(
        upload_module().upload,
        ["file", "--system-jwt", "test-jwt", str(boundary)],
    )

    assert result.exit_code == 0, result.output
    assert len(captured) == 1


def test_batch_upload_rejects_oversized_file_before_posting(tmp_path, monkeypatch):
    small = tmp_path / "ok.json"
    large = tmp_path / "too-big.json"
    small.write_text("{}", encoding="utf-8")
    large.write_text("{}", encoding="utf-8")
    captured = capture_posts(monkeypatch)
    fake_file_sizes(monkeypatch, {large: upload_module().MAX_UPLOAD_BYTES + 1})

    result = CliRunner().invoke(
        upload_module().upload,
        ["files", "--system-jwt", "test-jwt", str(small), str(large)],
    )

    assert result.exit_code == 1
    assert "exceeds the 1GB upload limit" in result.output
    assert captured == []
