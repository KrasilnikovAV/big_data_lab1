from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.pipeline import Pipeline

from .predict import load_model, predict_texts

MODEL: Pipeline | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global MODEL
    model_path = os.getenv("MODEL_PATH", "artifacts/model.joblib")
    try:
        MODEL = load_model(model_path)
    except FileNotFoundError:
        MODEL = None
    yield


app = FastAPI(title="BBC News Classifier API", version="1.0.0", lifespan=lifespan)


class PredictRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1)


class PredictResponse(BaseModel):
    predictions: list[str]

@app.get("/health")
def health() -> dict[str, str]:
    if MODEL is None:
        return {"status": "model_not_loaded"}
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    predictions = predict_texts(MODEL, payload.texts)
    return PredictResponse(predictions=predictions)
