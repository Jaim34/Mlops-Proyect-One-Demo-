# FinRisk: U.S. Public Debt Demo

A small, educational MLOps demo using the U.S. Treasury's public **Debt to the Penny** data. It trains a linear-regression baseline to estimate total public debt for a requested date. This is a demonstration of data ingestion, training, and API serving—not a financial risk rating or advice.

## Project structure

```text
.github/workflows/ci.yml  Automated tests
data/                     Small sample dataset
models/model_config.json  Model metadata (no serialized model)
notebooks/                Clean baseline experiment
src/data_ingestion.py     Treasury API ingestion
src/pipeline.py           Data preparation and training
src/app.py                FastAPI prediction service
tests/                    Focused unit tests
Dockerfile                Container setup
requirements.txt          Python dependencies
```

## Run locally

Use Python 3.11 or newer. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.pipeline
uvicorn src.app:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for the interactive API. For example:

```bash
curl 'http://localhost:8000/predict?date=2026-01-01'
```

The API trains from `data/debt_to_penny_sample.csv` when a prediction is requested, so no model binary needs to be committed. The bundled CSV is a small synthetic fixture for offline development, not official Treasury observations. To refresh it with current public Treasury data:

```bash
python -m src.data_ingestion --output data/debt_to_penny_sample.csv
```

Ingestion requires an internet connection; the bundled sample supports offline training and serving.

## Run in Docker

```bash
docker build -t finrisk-demo .
docker run --rm -p 8000:8000 finrisk-demo
```

## Data source and limitations

The ingestion module reads the Treasury Fiscal Data API's [`debt_to_penny`](https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny) endpoint, which provides daily public debt observations. The baseline uses only the observation date to extrapolate reported total public debt; it is not suitable for financial decisions or production forecasting.
