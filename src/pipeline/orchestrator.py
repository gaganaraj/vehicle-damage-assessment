
"""Role 4 orchestration layer for the vehicle damage claim project.

This version uses mock Contract A data until the real teammate modules
and their agreed interfaces are available.
"""

from typing import Any

from src.pipeline.contract_a_validator import validate_contract_a
from src.pipeline.mock_pipeline import load_contract_a_sample


def run_claim(
    photos: list[Any],
    description: str,
    vehicle: dict[str, Any],
    sample_filename: str | None = None,
) -> dict[str, Any]:
    """Prepare a claim using validated mock data.

    IMPORTANT:
    - This does not analyse uploaded photos.
    - It does not estimate repair costs.
    - It does not perform policy RAG or generate a final claim decision.
    - Real teammate modules must be integrated when their interfaces
      are available.
    """

    if not photos:
        raise ValueError("Upload at least one vehicle photo.")

    if len(photos) > 5:
        raise ValueError("Upload no more than five vehicle photos.")

    if not isinstance(description, str):
        raise ValueError("The damage description must be text.")

    if not isinstance(vehicle, dict):
        raise ValueError("Vehicle information must be provided as a dictionary.")

    required_fields = ("make", "model", "year", "fuel")

    for field in required_fields:
        if field not in vehicle or str(vehicle[field]).strip() == "":
            raise ValueError(f"Missing vehicle information: {field}")

    if not sample_filename:
        raise NotImplementedError(
            "Real photo analysis is not connected yet. "
            "Select a Contract A sample to run the mock pipeline."
        )

    report = load_contract_a_sample(sample_filename)
    validation_errors = validate_contract_a(report)

    if validation_errors:
        raise ValueError(
            "Contract A validation failed: "
            + "; ".join(validation_errors)
        )

    return {
        "status": "mock",
        "message": (
            "Validated sample report returned. "
            "Uploaded photos were not analysed."
        ),
        "report": report,
        "pipeline_stages": {
            "role_1_vision": "mock_sample_loaded_and_validated",
            "role_2_cost_engine": "not_connected",
            "role_3_policy_and_claim_writer": "not_connected",
            "role_4_orchestration": "working_with_mock_data",
        },
    }
