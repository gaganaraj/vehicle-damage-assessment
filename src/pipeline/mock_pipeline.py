
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MOCKS_DIR = PROJECT_ROOT / "mocks"


def list_contract_a_samples() -> list[str]:
    """Return available Contract A sample filenames."""
    return sorted(
        path.name
        for path in MOCKS_DIR.glob("contract_a_*.json")
    )


def load_contract_a_sample(filename: str) -> dict:
    """Load one sample report from the project's mocks folder."""
    available_files = list_contract_a_samples()

    if filename not in available_files:
        raise ValueError("Unknown Contract A sample filename.")

    sample_path = MOCKS_DIR / filename

    with sample_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    if not isinstance(report, dict):
        raise ValueError("The sample report must be a JSON object.")

    return report
