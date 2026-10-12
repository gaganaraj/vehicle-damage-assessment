# Multimodal Vehicle Damage Assessment and Insurance Claim Generator

A Python-based prototype for vehicle damage assessment and insurance claim report generation. The project is designed to integrate vehicle image analysis, repair cost estimation, insurance policy checks, and claim report generation.

## Project Overview

The system aims to help streamline the vehicle insurance claim process by combining damage assessment with structured claim reporting.

**Current implementation:** Streamlit UI, Contract A sample report validation, mock orchestration, and JSON/PDF report generation.

**Important:** The current prototype uses saved sample data. Uploaded vehicle photos are not analysed by an AI model, and repair cost estimation, insurance policy analysis, and claim approval are not yet connected.

## Features

- Vehicle information form
- Upload 1–5 vehicle photos
- Contract A sample report viewer
- JSON schema validation
- Mock pipeline orchestration
- Structured damage report display
- JSON report download
- PDF assessment report generation
- Automated tests using pytest

## Technology Stack

- Python 3.11
- Streamlit
- JSON Schema
- ReportLab
- Pytest

## Project Structure

```text
vehicle-damage-assessment/
├── docs/
│   └── role1/
├── mocks/
├── schemas/
│   └── contract_a.schema.json
├── src/
│   ├── app/
│   │   └── main.py
│   └── pipeline/
│       ├── contract_a_validator.py
│       ├── mock_pipeline.py
│       └── orchestrator.py
├── tests/
│   ├── test_contract_a_validator.py
│   └── test_orchestrator.py
├── requirements.txt
└── README.md
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/gaganaraj/vehicle-damage-assessment.git
cd vehicle-damage-assessment
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run src/app/main.py
```

Open the local URL displayed in the terminal, usually:

`http://localhost:8501`

## Running Tests

Run the test suite with:

```bash
python -m pytest -v
```

The current verified test result is **6 passed**.

## Current Pipeline Status

| Component | Status |
|---|---|
| Streamlit user interface | Implemented |
| Contract A sample validation | Implemented |
| Mock orchestration | Implemented |
| JSON report download | Implemented |
| PDF report generation | Implemented |
| Real vehicle photo analysis | Not connected |
| Repair cost estimation | Not connected |
| Insurance policy analysis | Not connected |
| Final claim decision | Not connected |

## Disclaimer

This repository contains a project prototype. Sample reports are used for testing the current workflow. The generated reports are not live AI assessments, repair quotations, insurance coverage determinations, or claim approvals.

## Repository

GitHub: https://github.com/gaganaraj/vehicle-damage-assessment