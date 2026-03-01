from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable

import joblib
from sklearn.pipeline import Pipeline

from .data import normalize_payload_texts


@lru_cache(maxsize=1)
def load_model(model_path: str | Path) -> Pipeline:
    return joblib.load(model_path)


def predict_texts(model: Pipeline, texts: Iterable[str]) -> list[str]:
    normalized_texts = normalize_payload_texts(texts)
    predictions = model.predict(normalized_texts)
    if hasattr(predictions, "tolist"):
        predictions = predictions.tolist()
    return [str(label) for label in predictions]
