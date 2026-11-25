"""Prepare Treasury data and train a simple debt trend baseline."""

import argparse
from datetime import date

import pandas as pd
from sklearn.linear_model import LinearRegression


DEFAULT_DATA_PATH = "data/debt_to_penny_sample.csv"
DATE_COLUMN = "record_date"
TARGET_COLUMN = "tot_pub_debt_out_amt"


def load_training_data(input_path=DEFAULT_DATA_PATH):
    data = pd.read_csv(input_path)
    missing_columns = {DATE_COLUMN, TARGET_COLUMN} - set(data.columns)
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing_columns)}")
    data = data[[DATE_COLUMN, TARGET_COLUMN]].copy()
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN], errors="coerce")
    data[TARGET_COLUMN] = pd.to_numeric(data[TARGET_COLUMN], errors="coerce")
    data = data.dropna().sort_values(DATE_COLUMN)
    if len(data) < 2:
        raise ValueError("At least two valid debt observations are required")
    data["record_date_ordinal"] = data[DATE_COLUMN].map(date.toordinal)
    return data


def train_model(input_path=DEFAULT_DATA_PATH):
    data = load_training_data(input_path)
    model = LinearRegression()
    model.fit(data[["record_date_ordinal"]], data[TARGET_COLUMN])
    return model


def predict_debt(target_date, input_path=DEFAULT_DATA_PATH):
    model = train_model(input_path)
    ordinal = date.fromisoformat(str(target_date)).toordinal()
    prediction = model.predict(pd.DataFrame({"record_date_ordinal": [ordinal]}))[0]
    return max(0.0, float(prediction))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_DATA_PATH)
    args = parser.parse_args()
    data = load_training_data(args.input)
    model = train_model(args.input)
    score = model.score(data[["record_date_ordinal"]], data[TARGET_COLUMN])
    print(f"Trained debt trend baseline on {len(data)} observations (R²={score:.3f})")


if __name__ == "__main__":
    main()
