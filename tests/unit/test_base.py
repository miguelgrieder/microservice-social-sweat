from fastapi.testclient import TestClient


def test_healt_check_endpoint() -> None:
    from microservice_social_sweat import main

    with TestClient(app=main.app) as client:
        response = client.get("/health_check")

    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
