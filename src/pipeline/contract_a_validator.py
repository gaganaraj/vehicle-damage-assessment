
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "contract_a.schema.json"


def load_contract_a_schema():
    """Load the team's official Contract A JSON schema."""
    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        schema = json.load(schema_file)

    Draft202012Validator.check_schema(schema)
    return schema


def validate_contract_a(report: dict) -> list[str]:
    """
    Validate a Contract A report.

    Returns an empty list when valid, or readable error messages
    when the report does not match the schema.
    """
    schema = load_contract_a_schema()

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    errors = sorted(
        validator.iter_errors(report),
        key=lambda error: list(map(str, error.absolute_path)),
    )

    messages = []

    for error in errors:
        location = ".".join(str(part) for part in error.absolute_path)
        location = location or "report"
        messages.append(f"{location}: {error.message}")

    return messages
