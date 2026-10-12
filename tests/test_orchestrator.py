
import pytest

from src.pipeline.orchestrator import run_claim
from src.pipeline.mock_pipeline import list_contract_a_samples


def sample_vehicle():
    return {
        "make": "Maruti Suzuki",
        "model": "Swift",
        "year": 2021,
        "fuel": "Petrol",
    }


def test_run_claim_returns_validated_mock_report():
    samples = list_contract_a_samples()
    assert samples, "Contract A sample files must exist for this test."

    result = run_claim(
        photos=[b"mock-photo"],
        description="Test damage",
        vehicle=sample_vehicle(),
        sample_filename=samples[0],
    )

    assert result["status"] == "mock"
    assert result["report"]["claim_id"]
    assert result["pipeline_stages"]["role_2_cost_engine"] == "not_connected"
    assert (
        result["pipeline_stages"]["role_3_policy_and_claim_writer"]
        == "not_connected"
    )


def test_run_claim_rejects_no_photos():
    with pytest.raises(ValueError, match="at least one"):
        run_claim(
            photos=[],
            description="Test damage",
            vehicle=sample_vehicle(),
            sample_filename="contract_a_001_dev_01.json",
        )


def test_run_claim_rejects_more_than_five_photos():
    with pytest.raises(ValueError, match="no more than five"):
        run_claim(
            photos=[b"photo"] * 6,
            description="Test damage",
            vehicle=sample_vehicle(),
            sample_filename="contract_a_001_dev_01.json",
        )


def test_run_claim_requires_a_sample_for_mock_mode():
    with pytest.raises(NotImplementedError, match="not connected yet"):
        run_claim(
            photos=[b"mock-photo"],
            description="Test damage",
            vehicle=sample_vehicle(),
        )
