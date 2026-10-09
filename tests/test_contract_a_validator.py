
import json
from pathlib import Path

from src.pipeline.contract_a_validator import validate_contract_a


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MOCKS_DIR = PROJECT_ROOT / "mocks"


def test_sample_contract_a_reports_are_valid():
    sample_files = sorted(MOCKS_DIR.glob("contract_a_*.json"))

    assert sample_files, "No Contract A sample JSON files found in mocks/"

    for sample_file in sample_files:
        with sample_file.open("r", encoding="utf-8") as file:
            report = json.load(file)

        errors = validate_contract_a(report)

        assert not errors, (
            f"{sample_file.name} failed validation:\n"
            + "\n".join(errors)
        )


def test_vision_error_example_is_valid_json():
    error_file = MOCKS_DIR / "vision_error_example.json"

    assert error_file.exists(), "Vision error example is missing"

    with error_file.open("r", encoding="utf-8") as file:
        example = json.load(file)

    assert isinstance(example, dict)
