from rovidh.config import RDHSystemConfig
from rovidh import api


class ResponseStub:
    def __init__(self):
        self.raise_for_status_called = False

    def raise_for_status(self):
        self.raise_for_status_called = True


def rdh_config():
    return RDHSystemConfig(
        api="https://example.test/api",
        verify_ssl=False,
        vendor_id="vendor",
        vendor_key="vendor-key",
        system_name="system",
        system_jwt="system-jwt",
        timeout=10,
    )


def test_create_headers_defaults_to_bearer_json_headers():
    headers = api.create_headers(rdh_config())

    assert headers == {
        "Content-Type": "application/json",
        "Authorization": "Bearer system-jwt",
    }


def test_create_headers_can_use_api_key_without_bearer():
    headers = api.create_headers(rdh_config(), token=False, api_key=True)

    assert headers == {
        "Content-Type": "application/json",
        "access-token": "vendor-key",
    }


def test_get_calls_requests_and_raises(monkeypatch):
    response = ResponseStub()
    calls = []

    def fake_get(url, headers=None, verify=None, timeout=None):
        calls.append({"url": url, "headers": headers, "verify": verify, "timeout": timeout})
        return response

    monkeypatch.setattr(api.requests, "get", fake_get)

    result = api.get(rdh_config(), "query/10", headers={"Authorization": "Bearer token"})

    assert result is response
    assert response.raise_for_status_called is True
    assert calls == [
        {
            "url": "https://example.test/api/query/10",
            "headers": {"Authorization": "Bearer token"},
            "verify": False,
            "timeout": 10,
        }
    ]


def test_post_calls_requests_with_data_and_raises(monkeypatch):
    response = ResponseStub()
    calls = []
    payload = {"key": "value"}

    def fake_post(url, data=None, headers=None, verify=None, timeout=None):
        calls.append({"url": url, "data": data, "headers": headers, "verify": verify, "timeout": timeout})
        return response

    monkeypatch.setattr(api.requests, "post", fake_post)

    result = api.post(rdh_config(), "renew_jwt", data=payload, headers={"access-token": "vendor-key"})

    assert result is response
    assert response.raise_for_status_called is True
    assert calls == [
        {
            "url": "https://example.test/api/renew_jwt",
            "data": payload,
            "headers": {"access-token": "vendor-key"},
            "verify": False,
            "timeout": 10,
        }
    ]
