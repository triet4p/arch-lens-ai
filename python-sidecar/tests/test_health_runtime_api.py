from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.api.v1.endpoints import health as health_endpoints


def test_runtime_health_endpoint_exposes_runtime_paths():
    app = FastAPI()
    app.include_router(health_endpoints.router)
    client = TestClient(app)

    response = client.get('/health/runtime')

    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'alive'
    assert 'database_url' in payload
    assert 'workspace_storage_dir' in payload
