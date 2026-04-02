from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from .predict import DEFAULT_PREDICTION_SERVICE, PredictionModel, load_model

MODEL: PredictionModel | None = None


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
    encoding: Literal["plain", "base64"] = "plain"

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, texts: list[str]) -> list[str]:
        if any(str(text).strip() == "" for text in texts):
            raise ValueError("Texts must not contain blank values.")
        return texts


class PredictResponse(BaseModel):
    predictions: list[str]


@app.get("/health")
def health() -> dict[str, str]:
    return DEFAULT_PREDICTION_SERVICE.health_status(MODEL)


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    try:
        predictions = DEFAULT_PREDICTION_SERVICE.predict(
            MODEL,
            payload.texts,
            encoding=payload.encoding,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return PredictResponse(predictions=predictions)
