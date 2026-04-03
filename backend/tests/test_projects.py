from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_projects_list_endpoint() -> None:
    response = client.get('/api/v1/projects')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
