from fastapi.testclient import TestClient

# from ..app import app
from api.router import router as api_router

client = TestClient(api_router)

def test_zalupa_handler():
    response = client.get("/zalupa")
    print(response.json())
    assert response.status_code == 200
    assert response.json() ==  'hello world'

