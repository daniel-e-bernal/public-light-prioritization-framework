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


if __name__ == "__main__":
    unittest.main()
