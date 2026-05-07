import json
from pathlib import Path

import pytest

imported_config = False
try:
    import tempfile
    import requests
    from rovidh.config import RDHConfig
    imported_config = True
except ImportError:
    pass

@pytest.fixture(scope="session")
def openapi_spec():
    spec_path = Path(__file__).resolve().parents[1] / "openapi.json"

    if imported_config and not spec_path.exists():
        try:
            config = RDHConfig()
            with tempfile.NamedTemporaryFile("w+", delete=False) as temp_spec_file:
                api_json = f"{config.api}/openapi.json"
                response = requests.get(api_json, verify=config.verify_ssl)
                response.raise_for_status()
                temp_spec_file.write(response.text)
                temp_spec_file.flush()
                spec_path = Path(temp_spec_file.name)
        except:
            pass

    if not spec_path.exists():
        pytest.skip(f"{spec_path} is required for OpenAPI-backed upload tests")

    with spec_path.open(encoding="utf-8") as spec_file:
        return json.load(spec_file)
