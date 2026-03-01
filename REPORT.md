# Отчёт по лабораторной работе: CI/CD для ML модели

## 1. Цель

Получить навыки построения CI/CD pipeline для ML модели с контролем метрик и качества кода.

## 2. Выполненные шаги

1. Подготовлен репозиторий и структура проекта (`src/`, `tests/`, `scripts/`, `.github/workflows/`).
2. Проведена подготовка данных для датасета BBC News в модуле `src/bbc_news/data.py`.
3. Реализована модель текстовой классификации (TF-IDF + `LinearSVC`/`LogisticRegression`) в `src/bbc_news/model.py`.
4. Ноутбук конвертирован в Python-скрипты; обучение вынесено в `python -m bbc_news.train`.
5. Реализован API сервис (FastAPI) с endpoint `/predict`.
6. Код покрыт тестами (`pytest`, `pytest-cov`).
7. Добавлен DVC pipeline (`dvc.yaml`).
8. Подготовлены конфигурационные файлы:
   - `config.ini`
   - `Dockerfile`, `docker-compose.yml`
   - `requirements.txt`
   - `dev_sec_ops.yml`
   - `scenario.json`
9. Создан CI pipeline `.github/workflows/ci.yml`:
   - запуск по PR в `main`;
   - тесты + coverage;
   - сборка и push Docker image;
   - подпись образа `cosign`.
10. Создан CD pipeline `.github/workflows/cd.yml`:
    - запуск по требованию/расписанию/после CI;
    - запуск контейнера;
    - функциональное тестирование по `scenario.json` внутри контейнера (`docker compose exec`).

## 3. Артефакты и результаты

- Метрики модели (`artifacts/metrics.json`):
  - Accuracy: `0.9765`
  - F1 macro: `0.9756`
  - F1 weighted: `0.9765`
- Предсказания на тесте: `artifacts/submission.csv`
- Функциональные тесты контейнера: `scripts/run_scenario.py` + `scenario.json`
