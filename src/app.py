"""FastAPI service for the FinRisk public-debt demo."""

from datetime import date

from fastapi import FastAPI, HTTPException, Query

from src.pipeline import predict_debt


app = FastAPI(title="FinRisk Public Debt Demo", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/predict")
def predict(target_date: date = Query(alias="date")):
    try:
        amount = predict_debt(target_date.isoformat())
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate a prediction from the configured data.",
        ) from error
    return {
        "date": target_date.isoformat(),
        "forecast_total_public_debt_usd": amount,
        "model": "debt-trend-baseline",
        "disclaimer": "Educational estimate only; not a financial risk assessment.",
    }
