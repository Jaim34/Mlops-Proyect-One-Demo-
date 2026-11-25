"""Fetch U.S. Treasury Debt to the Penny observations."""

import argparse
import csv
import json
from urllib.parse import urlencode
from urllib.request import urlopen


API_URL = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
    "v2/accounting/od/debt_to_penny"
)
FIELDS = ("record_date", "tot_pub_debt_out_amt")


def fetch_records():
    params = urlencode(
        {
            "fields": ",".join(FIELDS),
            "sort": "-record_date",
            "page[size]": "1000",
        }
    )
    with urlopen(f"{API_URL}?{params}", timeout=30) as response:
        payload = json.load(response)
    records = payload.get("data")
    if not isinstance(records, list) or not records:
        raise ValueError("Treasury API returned no debt observations")
    return normalize_records(records)


def normalize_records(records):
    normalized = []
    for record in records:
        try:
            date = record["record_date"]
            amount = float(record["tot_pub_debt_out_amt"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Treasury API returned an invalid debt observation") from error
        normalized.append({"record_date": date, "tot_pub_debt_out_amt": amount})
    return normalized


def write_records(records, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(normalize_records(records))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="data/debt_to_penny_sample.csv")
    args = parser.parse_args()
    write_records(fetch_records(), args.output)
    print(f"Wrote Treasury debt observations to {args.output}")


if __name__ == "__main__":
    main()
