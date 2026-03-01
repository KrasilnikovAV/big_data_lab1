from __future__ import annotations

from fastapi.testclient import TestClient

from bbc_news import api


class DummyModel:
    def predict(self, texts: list[str]) -> list[str]:
        return ["sport" for _ in texts]


def test_predict_endpoint_returns_predictions() -> None:
    with TestClient(api.app) as client:
        api.MODEL = DummyModel()
        response = client.post("/predict", json={"texts": ["one", "two"]})

    assert response.status_code == 200
    assert response.json() == {"predictions": ["sport", "sport"]}


def test_predict_endpoint_returns_503_when_model_not_loaded() -> None:
    with TestClient(api.app) as client:
        api.MODEL = None
        response = client.post("/predict", json={"texts": ["one"]})

    assert response.status_code == 503


def test_health_endpoint() -> None:
    with TestClient(api.app) as client:
        api.MODEL = DummyModel()
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
