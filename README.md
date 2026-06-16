# public-light-prioritization-framework

This repo intakes data generated from ArcGIS Survey123 and runs a prioritization framework.

## Architecture

- `data/`: incoming intake CSV data.
- `config/expected_columns.json`: editable expected intake columns.
- `src/prioritization_framework/`: intake, clean, reorder, and priority-action processing logic.
- `results/`: output prioritized result list.

## Run

```bash
python run_prioritization.py
```

This reads `data/intake_data.csv` and writes `results/prioritized_items.csv`.
