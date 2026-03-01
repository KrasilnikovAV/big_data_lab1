# BBC News Classifier with CI/CD

Проект лабораторной работы по Big Data/ML Ops:
- подготовка данных и обучение классической модели классификации;
- API сервис для инференса;
- тесты;
- DVC stage;
- Docker image;
- CI/CD pipeline на GitHub Actions.

## Структура

- `src/bbc_news/` - код подготовки данных, обучения, API.
- `tests/` - unit/e2e тесты.
- `config.ini` - гиперпараметры и пути.
- `dvc.yaml` - DVC pipeline stage.
- `Dockerfile`, `docker-compose.yml` - контейнеризация.
- `.github/workflows/ci.yml` - CI pipeline (PR в `main`).
- `.github/workflows/cd.yml` - CD/functional tests.
- `scenario.json` - сценарий функционального теста контейнера.
- `dev_sec_ops.yml` - манифест DevSecOps.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### Обучение модели

```bash
python scripts/train_model.py --config config.ini
```

Артефакты сохраняются в `artifacts/`:
- `model.joblib`
- `metrics.json`
- `submission.csv`

### Запуск API

```bash
PYTHONPATH=src uvicorn bbc_news.api:app --host 0.0.0.0 --port 8000
```

Пример запроса:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"texts":["Stock market gained today","Team won championship"]}'
```

### Тесты

```bash
PYTHONPATH=src pytest --cov=src --cov-report=term-missing --cov-report=xml
```

### DVC

```bash
dvc repro
```

### Docker

```bash
docker compose up -d --build
python scripts/run_scenario.py --scenario scenario.json --base-url http://localhost:8000
docker compose down
```

## CI/CD

- CI запускается на `pull_request` в `main`.
- CI выполняет: обучение, тесты, сборку образа и push в DockerHub (если заданы secrets), подпись образа `cosign`, генерацию `dev_sec_ops.yml`.
- CD запускается вручную/по расписанию/после CI, поднимает контейнер и выполняет функциональный сценарий из `scenario.json` внутри контейнера (`docker compose exec`).

## Что подставить для отчёта

- Ссылка на GitHub репозиторий: `<YOUR_GITHUB_REPO_URL>`
- Ссылка на DockerHub image: `docker.io/<DOCKERHUB_USERNAME>/bbc-news-classifier`
