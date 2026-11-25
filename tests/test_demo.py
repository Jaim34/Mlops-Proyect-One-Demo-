import json
import unittest
from datetime import date
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src.data_ingestion import fetch_records, normalize_records
from src.pipeline import load_training_data, predict_debt


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA = ROOT / "data" / "debt_to_penny_sample.csv"


class IngestionTests(unittest.TestCase):
    def test_normalize_records_converts_amounts_and_rejects_invalid_data(self):
        records = normalize_records(
            [{"record_date": "2025-01-02", "tot_pub_debt_out_amt": "123.45"}]
        )
        self.assertEqual(records[0]["tot_pub_debt_out_amt"], 123.45)
        with self.assertRaises(ValueError):
            normalize_records([{"record_date": "2025-01-02"}])

    @patch("src.data_ingestion.urlopen")
    def test_fetch_records_requests_latest_data(self, mock_urlopen):
        mock_urlopen.return_value = BytesIO(
            json.dumps(
                {"data": [{"record_date": "2025-01-17", "tot_pub_debt_out_amt": "100"}]}
            ).encode()
        )
        self.assertEqual(fetch_records()[0]["record_date"], "2025-01-17")
        self.assertIn("sort=-record_date", mock_urlopen.call_args.args[0])


class PipelineTests(unittest.TestCase):
    def test_load_and_predict_from_sample(self):
        data = load_training_data(SAMPLE_DATA)
        self.assertEqual(len(data), 10)
        self.assertGreater(
            predict_debt(date(2026, 1, 1), SAMPLE_DATA),
            0,
        )

    def test_rejects_insufficient_valid_observations(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "debt.csv"
            path.write_text(
                "record_date,tot_pub_debt_out_amt\n2025-01-01,100\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_training_data(path)


if __name__ == "__main__":
    unittest.main()
