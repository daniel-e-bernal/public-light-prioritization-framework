from pathlib import Path

from src.prioritization_framework.pipeline import run_pipeline


def main() -> None:
    repository_root = Path(__file__).resolve().parent
    data_file_path = repository_root / "data" / "intake_data.csv"
    config_path = repository_root / "config" / "expected_columns.json"
    output_file_path = repository_root / "results" / "prioritized_items.csv"

    run_pipeline(data_file_path, config_path, output_file_path)
    print(f"Prioritized items written to: {output_file_path}")


if __name__ == "__main__":
    main()
