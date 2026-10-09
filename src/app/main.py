
import streamlit as st

from src.pipeline.contract_a_validator import validate_contract_a
from src.pipeline.mock_pipeline import (
    list_contract_a_samples,
    load_contract_a_sample,
)

st.set_page_config(
    page_title="Vehicle Damage Assessment",
    page_icon="🚗",
    layout="wide",
)

st.title("🚗 Vehicle Damage Assessment")
st.caption(
    "Multimodal Vehicle Damage Assessment and Insurance Claim Generator"
)

st.info(
    "Prototype mode: the sample reports below are pre-existing test data. "
    "Live AI detection, repair estimates, and policy analysis are not "
    "connected yet."
)

st.header("1. Vehicle Information")

col1, col2 = st.columns(2)

with col1:
    make = st.text_input("Vehicle make", placeholder="e.g., Maruti Suzuki")
    model = st.text_input("Vehicle model", placeholder="e.g., Swift")
    year = st.number_input(
        "Manufacturing year",
        min_value=1980,
        max_value=2100,
        value=2022,
        step=1,
    )

with col2:
    fuel_type = st.selectbox(
        "Fuel type",
        ["Petrol", "Diesel", "CNG", "Electric", "Hybrid", "Other"],
    )
    claim_description = st.text_area(
        "Describe the damage",
        placeholder="Explain what happened and which parts appear damaged.",
    )

st.header("2. Upload Vehicle Photos")

uploaded_files = st.file_uploader(
    "Upload 1–5 vehicle photos",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    help="Use clear photos showing damaged areas from different angles.",
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.error("Please upload no more than 5 photos.")
    else:
        st.success(f"{len(uploaded_files)} photo(s) uploaded.")

        columns = st.columns(min(len(uploaded_files), 3))

        for index, uploaded_file in enumerate(uploaded_files):
            with columns[index % len(columns)]:
                st.image(
                    uploaded_file,
                    caption=f"Photo {index + 1}",
                    width="stretch",
                )

st.divider()
st.header("3. Assessment")

if st.button("Prepare Assessment", type="primary"):
    if not make.strip() or not model.strip():
        st.error("Please enter the vehicle make and model.")
    elif not uploaded_files:
        st.error("Please upload at least one vehicle photo.")
    elif len(uploaded_files) > 5:
        st.error("Please upload no more than 5 photos.")
    else:
        st.success("Input validation passed!")
        st.write("Vehicle:", make, model, int(year))
        st.write("Fuel type:", fuel_type)
        st.write("Photos uploaded:", len(uploaded_files))
        st.info(
            "Your inputs are valid. The uploaded photos have not been "
            "analysed by an AI model yet."
        )

st.divider()
st.header("4. Contract A — Sample Report Viewer")

st.caption(
    "Use this section to test the team's report schema and UI. "
    "Selecting a sample does not analyse your uploaded photos."
)

sample_files = list_contract_a_samples()

if not sample_files:
    st.warning("No Contract A sample reports were found in the mocks folder.")
else:
    selected_sample = st.selectbox(
        "Choose a sample report",
        sample_files,
    )

    if st.button("Load Sample Report"):
        try:
            report = load_contract_a_sample(selected_sample)
            errors = validate_contract_a(report)

            if errors:
                st.error("This sample does not pass Contract A validation.")
                for error in errors:
                    st.write(f"- {error}")
            else:
                st.session_state["contract_a_sample_report"] = report
                st.session_state["contract_a_sample_filename"] = selected_sample

        except (ValueError, OSError, RuntimeError) as error:
            st.error(f"Could not load the sample report: {error}")

    report = st.session_state.get("contract_a_sample_report")

    if report:
        st.subheader("Sample Report Results")
        st.caption(
            "Demo data only — these results came from a saved JSON file."
        )

        st.write("**Sample file:**", st.session_state.get(
            "contract_a_sample_filename", ""
        ))
        st.write("**Claim ID:**", report.get("claim_id", "Not provided"))

        vehicle = report.get("vehicle", {})

        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Make", vehicle.get("make", "—"))
        v2.metric("Model", vehicle.get("model", "—"))
        v3.metric("Year", vehicle.get("year", "—"))
        v4.metric("Fuel", vehicle.get("fuel", "—"))

        st.subheader("Detected Damage Entries")
        damages = report.get("damages", [])

        if damages:
            display_damages = []

            for damage in damages:
                display_damages.append(
                    {
                        "Part": damage.get("part", "—"),
                        "Damage Type": damage.get("damage_type", "—"),
                        "Severity": damage.get("severity", "—"),
                        "Confidence": (
                            f"{damage.get('confidence', 0):.0%}"
                            if isinstance(damage.get("confidence"), (int, float))
                            else "—"
                        ),
                        "Photo Number": (
                            damage["image_index"] + 1
                            if isinstance(damage.get("image_index"), int)
                            else "—"
                        ),
                        "Notes": damage.get("notes", ""),
                    }
                )

            st.dataframe(
                display_damages,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No damage entries are recorded in this sample.")

        quality_flags = report.get("image_quality_flags", [])
        st.subheader("Image Quality")
        if quality_flags:
            for flag in quality_flags:
                st.warning(str(flag))
        else:
            st.success("No image quality flags are recorded in this sample.")

        with st.expander("Technical Metadata"):
            st.write("**Model used:**", report.get("model_used", "—"))
            st.write(
                "**Prompt strategy:**",
                report.get("prompt_strategy", "—"),
            )

        with st.expander("View Complete Contract A JSON"):
            st.json(report)
