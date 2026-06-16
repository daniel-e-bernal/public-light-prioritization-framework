import csv
import tempfile
import unittest
from pathlib import Path

from src.prioritization_framework.pipeline import run_pipeline


class PipelineTests(unittest.TestCase):
    def test_run_pipeline_reorders_and_adds_priority_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_file = root / "intake.csv"
            config_file = root / "expected_columns.json"
            output_file = root / "output.csv"

            data_file.write_text(
                "location,asset_id,priority_score,issue_type,extra\n"
                "Main St / 4th St,A-100,92,Outage,ignore\n"
                "Pine St / 6th St,A-101,63,Flicker,ignore\n"
                "Oak St / 2nd St,A-102,28,Inspection,ignore\n",
                encoding="utf-8",
            )
            config_file.write_text(
                '{"expected_columns": ["asset_id", "location", "issue_type", "priority_score"]}',
                encoding="utf-8",
            )

            run_pipeline(data_file, config_file, output_file)

            with output_file.open("r", encoding="utf-8", newline="") as output:
                rows = list(csv.DictReader(output))

        self.assertEqual(
            ["asset_id", "location", "issue_type", "priority_score", "priority_action"],
            list(rows[0].keys()),
        )
        self.assertEqual("A-100", rows[0]["asset_id"])
        self.assertEqual("Main St / 4th St", rows[0]["location"])
        self.assertEqual("Outage", rows[0]["issue_type"])
        self.assertEqual("92", rows[0]["priority_score"])
        self.assertEqual("Immediate Action", rows[0]["priority_action"])
        self.assertEqual("Planned Action", rows[1]["priority_action"])
        self.assertEqual("Monitor", rows[2]["priority_action"])

    def test_run_pipeline_uses_review_for_invalid_priority_score(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_file = root / "intake.csv"
            config_file = root / "expected_columns.json"
            output_file = root / "output.csv"

            data_file.write_text(
                "asset_id,location,issue_type,priority_score\n"
                "A-200,Maple St / 7th St,Unknown,n/a\n",
                encoding="utf-8",
            )
            config_file.write_text(
                '{"expected_columns": ["asset_id", "location", "issue_type", "priority_score"]}',
                encoding="utf-8",
            )

            run_pipeline(data_file, config_file, output_file)
            with output_file.open("r", encoding="utf-8", newline="") as output:
                rows = list(csv.DictReader(output))

        self.assertEqual("Review", rows[0]["priority_action"])

    def test_run_pipeline_raises_for_missing_or_invalid_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_file = root / "intake.csv"
            output_file = root / "output.csv"
            missing_config_file = root / "missing_expected_columns.json"
            invalid_config_file = root / "invalid_expected_columns.json"
            empty_config_file = root / "empty_expected_columns.json"

            data_file.write_text(
                "asset_id,location,issue_type,priority_score\nA-100,Main St / 4th St,Outage,92\n",
                encoding="utf-8",
            )
            invalid_config_file.write_text("{not_json", encoding="utf-8")
            empty_config_file.write_text('{"expected_columns": []}', encoding="utf-8")

            with self.assertRaisesRegex(FileNotFoundError, "Expected-column config file not found"):
                run_pipeline(data_file, missing_config_file, output_file)

            with self.assertRaisesRegex(ValueError, "not valid JSON"):
                run_pipeline(data_file, invalid_config_file, output_file)

            with self.assertRaisesRegex(ValueError, "No expected columns configured"):
                run_pipeline(data_file, empty_config_file, output_file)

    def test_run_pipeline_raises_for_missing_data_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            missing_data_file = root / "missing_intake.csv"
            config_file = root / "expected_columns.json"
            output_file = root / "output.csv"

            config_file.write_text(
                '{"expected_columns": ["asset_id", "location", "issue_type", "priority_score"]}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(FileNotFoundError, "Intake data file not found"):
                run_pipeline(missing_data_file, config_file, output_file)


if __name__ == "__main__":
    unittest.main()
