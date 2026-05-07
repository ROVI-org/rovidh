import importlib

from click.testing import CliRunner


def system_module():
    return importlib.import_module("rovidh.system")


class JsonResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


def system_args(*extra_args):
    return [
        "--vendor-id",
        "vendor-id",
        "--vendor-key",
        "vendor-key",
        "--system-name",
        "system-name",
        "--system-jwt",
        "current-jwt",
        *extra_args,
    ]


def capture_system_side_effects(monkeypatch, response_payload):
    module = system_module()
    post_calls = []
    save_calls = []

    def fake_create_headers(rdh_config, token=True, api_key=False):
        return {
            "token": token,
            "api_key": api_key,
            "system_jwt": rdh_config.system_jwt,
            "vendor_key": rdh_config.vendor_key,
        }

    def fake_post(rdh_config, uri, data=None, headers=None):
        post_calls.append(
            {
                "uri": uri,
                "data": data,
                "headers": headers,
                "vendor_id": rdh_config.vendor_id,
                "system_name": rdh_config.system_name,
            }
        )
        return JsonResponse(response_payload)

    def fake_save_config(setting, value):
        save_calls.append((setting, value))

    monkeypatch.setattr(module, "create_headers", fake_create_headers)
    monkeypatch.setattr(module, "post", fake_post)
    monkeypatch.setattr(module, "save_config", fake_save_config)

    return post_calls, save_calls


def test_system_new_creates_jwt_and_persists_config(monkeypatch):
    post_calls, save_calls = capture_system_side_effects(monkeypatch, {"token": "new-jwt"})

    result = CliRunner().invoke(system_module().system, ["new", *system_args()])

    assert result.exit_code == 0, result.output
    assert "New system token for system-name: new-jwt" in result.output
    assert post_calls == [
        {
            "uri": "create_jwt/vendor-id/system-name",
            "data": None,
            "headers": {
                "token": False,
                "api_key": True,
                "system_jwt": "current-jwt",
                "vendor_key": "vendor-key",
            },
            "vendor_id": "vendor-id",
            "system_name": "system-name",
        }
    ]
    assert save_calls == [
        ("SYSTEM_NAME", "system-name"),
        ("VENDOR_ID", "vendor-id"),
        ("SYSTEM_JWT", "new-jwt"),
    ]


def test_system_renew_renews_jwt_and_persists_token(monkeypatch):
    post_calls, save_calls = capture_system_side_effects(monkeypatch, {"token": "renewed-jwt"})

    result = CliRunner().invoke(system_module().system, ["renew", *system_args()])

    assert result.exit_code == 0, result.output
    assert "Renewed system token for system-name: renewed-jwt" in result.output
    assert post_calls == [
        {
            "uri": "renew_jwt",
            "data": None,
            "headers": {
                "token": True,
                "api_key": True,
                "system_jwt": "current-jwt",
                "vendor_key": "vendor-key",
            },
            "vendor_id": "vendor-id",
            "system_name": "system-name",
        }
    ]
    assert save_calls == [("SYSTEM_JWT", "renewed-jwt")]


def test_system_delete_deletes_jwt_and_clears_token(monkeypatch):
    post_calls, save_calls = capture_system_side_effects(monkeypatch, {"status": "deleted"})

    result = CliRunner().invoke(system_module().system, ["delete", *system_args()])

    assert result.exit_code == 0, result.output
    assert "Deleted system system-name: deleted" in result.output
    assert post_calls == [
        {
            "uri": "delete_jwt/vendor-id/system-name",
            "data": None,
            "headers": {
                "token": True,
                "api_key": True,
                "system_jwt": "current-jwt",
                "vendor_key": "vendor-key",
            },
            "vendor_id": "vendor-id",
            "system_name": "system-name",
        }
    ]
    assert save_calls == [("SYSTEM_JWT", "")]
