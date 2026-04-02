from __future__ import annotations

import base64

from fastapi.testclient import TestClient

from bbc_news import api


class DummyModel:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def predict(self, texts: list[str]) -> list[str]:
        self.calls.append(texts)
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


def test_predict_endpoint_decodes_base64_payload() -> None:
    encoded_text = base64.b64encode("team won the final".encode("utf-8")).decode("utf-8")
    model = DummyModel()

    with TestClient(api.app) as client:
        api.MODEL = model
        response = client.post(
            "/predict",
            json={"texts": [encoded_text], "encoding": "base64"},
        )

    assert response.status_code == 200
    assert response.json() == {"predictions": ["sport"]}
    assert model.calls == [["team won the final"]]


def test_predict_endpoint_returns_422_for_invalid_base64() -> None:
    with TestClient(api.app) as client:
        api.MODEL = DummyModel()
        response = client.post(
            "/predict",
            json={"texts": ["not-base64"], "encoding": "base64"},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid base64 payload."
