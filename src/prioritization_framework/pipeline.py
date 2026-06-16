import csv
import json
from pathlib import Path
from typing import Dict, List


def load_expected_columns(config_path: Path) -> List[str]:
    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Expected-column config file not found: {config_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Expected-column config is not valid JSON: {config_path}") from error
    return config.get("expected_columns", [])


def _clean_row(row: Dict[str, str]) -> Dict[str, str]:
    return {str(key).strip(): str(value).strip() for key, value in row.items()}


def _priority_action_for_row(row: Dict[str, str]) -> str:
    score_value = row.get("priority_score", "")
    try:
        score = float(score_value)
    except (TypeError, ValueError):
        return "Review"

    if score >= 80:
        return "Immediate Action"
    if score >= 50:
        return "Planned Action"
    return "Monitor"


def process_rows(rows: List[Dict[str, str]], expected_columns: List[str]) -> List[Dict[str, str]]:
    processed_rows: List[Dict[str, str]] = []
    for raw_row in rows:
        cleaned_row = _clean_row(raw_row)
        normalized_row = {column: cleaned_row.get(column, "") for column in expected_columns}
        normalized_row["priority_action"] = _priority_action_for_row(normalized_row)
        processed_rows.append(normalized_row)
    return processed_rows


def read_rows(data_file_path: Path) -> List[Dict[str, str]]:
    try:
        with data_file_path.open("r", encoding="utf-8", newline="") as data_file:
            return list(csv.DictReader(data_file))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Intake data file not found: {data_file_path}") from error


def write_rows(output_file_path: Path, rows: List[Dict[str, str]], expected_columns: List[str]) -> None:
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_columns = [*expected_columns, "priority_action"]
    with output_file_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline(data_file_path: Path, config_path: Path, output_file_path: Path) -> Path:
    expected_columns = load_expected_columns(config_path)
    if not expected_columns:
        raise ValueError(f"No expected columns configured in {config_path}.")

    rows = read_rows(data_file_path)
    processed_rows = process_rows(rows, expected_columns)
    write_rows(output_file_path, processed_rows, expected_columns)
    return output_file_path
