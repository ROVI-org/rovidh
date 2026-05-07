import requests
import io
from requests_toolbelt.multipart.encoder import MultipartEncoder
from .config import RDHConfig


def create_headers(rdh_config: RDHConfig, token: bool = True, api_key: bool = False) -> dict:
    headers = { "Content-Type": "application/json" }
    if token:
        headers["Authorization"] = f"Bearer {rdh_config.system_jwt}"
    if api_key:
        headers["access-token"] = rdh_config.vendor_key
    return headers


def get(rdh_config: RDHConfig, uri: str, headers: dict = {}):
    response = requests.get(f"{rdh_config.api}/{uri}", headers=headers, verify=rdh_config.verify_ssl, timeout=rdh_config.timeout)
    response.raise_for_status()
    return response


def post(rdh_config: RDHConfig, uri: str, data: dict | MultipartEncoder | io.BytesIO = None, headers: dict = {}):
    response = requests.post(f"{rdh_config.api}/{uri}", data=data, headers=headers, verify=rdh_config.verify_ssl, timeout=rdh_config.timeout)
    response.raise_for_status()
    return response
