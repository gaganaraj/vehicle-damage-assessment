
import io
import json
from xml.sax.saxutils import escape

import streamlit as st

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from src.pipeline.contract_a_validator import validate_contract_a
from src.pipeline.mock_pipeline import (
    list_contract_a_samples,
    load_contract_a_sample,
)
from src.pipeline.orchestrator import run_claim


# --------------------------------------------------
# PDF GENERATOR
# --------------------------------------------------

def generate_claim_pdf(report):
    """Generate a prototype PDF from a Contract A sample report."""
    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    story = []
    vehicle = report.get("vehicle", {})
    damages = report.get("damages", [])

    story.append(
        Paragraph("VEHICLE DAMAGE ASSESSMENT REPORT", styles["Title"])
    )
    story.append(Spacer(1, 5 * mm))
    story.append(
        Paragraph(
            "<b>PROTOTYPE REPORT — SAMPLE DATA ONLY</b>",
            styles["Heading2"],
        )
    )
    story.append(Spacer(1, 4 * mm))

    details = [
        ["Claim ID", escape(str(report.get("claim_id", "—")))],
        [
            "Vehicle",
            escape(
                f"{vehicle.get('make', '—')} "
                f"{vehicle.get('model', '—')}"
            ),
        ],
        ["Manufacturing Year", escape(str(vehicle.get("year", "—")))],
        ["Fuel Type", escape(str(vehicle.get("fuel", "—")))],
        [
            "Incident Description",
            escape(str(report.get("user_description", "—"))),
        ],
    ]

    details_table = Table(details, colWidths=[45 * mm, 115 * mm])
    details_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(details_table)
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph("Damage Details", styles["Heading1"]))
    story.append(Spacer(1, 3 * mm))

    damage_rows = [
        ["Part", "Damage Type", "Severity", "Confidence", "Photo"]
    ]

    for damage in damages:
        confidence = damage.get("confidence")
        if (
            isinstance(confidence, (int, float))
            and not isinstance(confidence, bool)
        ):
            confidence_text = f"{confidence:.0%}"
        else:
            confidence_text = "—"

        image_index = damage.get("image_index")
        if (
            isinstance(image_index, int)
            and not isinstance(image_index, bool)
            and image_index >= 0
        ):
            photo_text = str(image_index + 1)
        else:
            photo_text = "—"

        damage_rows.append(
            [
                escape(
                    str(damage.get("part", "—"))
                    .replace("_", " ")
                    .title()
                ),
                escape(
                    str(damage.get("damage_type", "—"))
                    .replace("_", " ")
                    .title()
                ),
                escape(str(damage.get("severity", "—")).title()),
                confidence_text,
                photo_text,
            ]
        )

    if len(damage_rows) == 1:
        damage_rows.append(["No damage entries", "—", "—", "—", "—"])

    damage_table = Table(
        damage_rows,
        colWidths=[38 * mm, 38 * mm, 25 * mm, 27 * mm, 18 * mm],
        repeatRows=1,
    )
    damage_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(damage_table)
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Damage Notes", styles["Heading1"]))

    if damages:
        for index, damage in enumerate(damages, start=1):
            part = (
                str(damage.get("part", "Unknown part"))
                .replace("_", " ")
                .title()
            )
            notes = str(damage.get("notes", "No notes provided"))

            story.append(
                Paragraph(
                    f"<b>{index}. {escape(part)}</b>: {escape(notes)}",
                    styles["BodyText"],
                )
            )
            story.append(Spacer(1, 2 * mm))
    else:
        story.append(
            Paragraph("No damage entries are recorded.", styles["BodyText"])
        )

    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Technical Metadata", styles["Heading1"]))

    model_used = escape(str(report.get("model_used", "—")))
    prompt_strategy = escape(str(report.get("prompt_strategy", "—")))

    story.append(
        Paragraph(
            f"Model used: {model_used}<br/>"
            f"Prompt strategy: {prompt_strategy}",
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 6 * mm))
    story.append(
        Paragraph(
            "<b>Important:</b> This report uses saved sample data. "
            "It is not a live AI assessment. Repair costs, insurance "
            "coverage, and claim approval have not been assessed.",
            styles["BodyText"],
        )
    )

    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

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
    "Prototype mode: saved sample reports are used for testing. "
    "Live photo analysis, repair estimates, and policy analysis "
    "are not connected yet."
)


# --------------------------------------------------
# 1. VEHICLE INFORMATION
# --------------------------------------------------

st.header("1. Vehicle Information")

col1, col2 = st.columns(2)

with col1:
    make = st.text_input(
        "Vehicle make",
        placeholder="e.g., Maruti Suzuki",
    )
    model = st.text_input(
        "Vehicle model",
        placeholder="e.g., Swift",
    )
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


# --------------------------------------------------
# 2. UPLOAD VEHICLE PHOTOS
# --------------------------------------------------

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


# --------------------------------------------------
# 3. ASSESSMENT INPUT VALIDATION
# --------------------------------------------------

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
        st.session_state["assessment_inputs"] = {
            "make": make.strip(),
            "model": model.strip(),
            "year": int(year),
            "fuel": fuel_type.lower(),
            "description": claim_description.strip(),
            "photo_count": len(uploaded_files),
        }
        st.success("Input validation passed!")
        st.write("Vehicle:", make, model, int(year))
        st.write("Fuel type:", fuel_type)
        st.write("Photos uploaded:", len(uploaded_files))
        st.info(
            "Inputs are valid. To run the mock pipeline, select a saved "
            "Contract A sample in Section 4. Uploaded photos are not "
            "analysed by an AI model in this prototype."
        )


# --------------------------------------------------
# 4. CONTRACT A SAMPLE VIEWER AND MOCK ORCHESTRATION
# --------------------------------------------------

st.divider()
st.header("4. Contract A — Sample Report Viewer")

st.caption(
    "Saved samples are used to test validation, orchestration, and output "
    "generation. Selecting a sample does not analyse uploaded photos."
)

sample_files = list_contract_a_samples()

if not sample_files:
    st.warning("No Contract A sample reports were found in the mocks folder.")
else:
    selected_sample = st.selectbox(
        "Choose a sample report",
        sample_files,
    )

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        load_clicked = st.button("Load Sample Report")

    with action_col2:
        run_clicked = st.button("Run Mock Orchestration", type="primary")

    if load_clicked:
        try:
            report = load_contract_a_sample(selected_sample)
            errors = validate_contract_a(report)

            if errors:
                st.error("This sample does not pass Contract A validation.")
                for error in errors:
                    st.write(f"- {error}")
            else:
                st.session_state["contract_a_sample_report"] = report
                st.session_state["contract_a_sample_filename"] = (
                    selected_sample
                )
                st.session_state.pop("orchestration_result", None)
        except (ValueError, OSError, RuntimeError) as error:
            st.error(f"Could not load the sample report: {error}")

    if run_clicked:
        assessment_inputs = st.session_state.get("assessment_inputs")

        if not assessment_inputs:
            st.error(
                "Complete Section 1 and Section 2, then click "
                "'Prepare Assessment' before running orchestration."
            )
        else:
            try:
                with st.spinner("Running mock orchestration..."):
                    photos = [
                        uploaded_file.getvalue()
                        for uploaded_file in uploaded_files
                    ]

                    result = run_claim(
                        photos=photos,
                        description=assessment_inputs["description"],
                        vehicle={
                            "make": assessment_inputs["make"],
                            "model": assessment_inputs["model"],
                            "year": assessment_inputs["year"],
                            "fuel": assessment_inputs["fuel"],
                        },
                        sample_filename=selected_sample,
                    )

                st.session_state["orchestration_result"] = result
                st.session_state["contract_a_sample_report"] = result["report"]
                st.session_state["contract_a_sample_filename"] = selected_sample

            except (ValueError, NotImplementedError, OSError, RuntimeError) as error:
                st.error(f"Mock orchestration could not run: {error}")

    result = st.session_state.get("orchestration_result")

    if result:
        st.subheader("Mock Orchestration Status")
        st.success(result["message"])
        st.write("**Status:**", result["status"])

        st.write("**Pipeline stages:**")
        for stage, status in result["pipeline_stages"].items():
            st.write(f"- **{stage}:** {status}")

        st.warning(
            "This is a mock pipeline. The selected saved report is returned "
            "after validation; the uploaded photos are not analysed."
        )

    report = st.session_state.get("contract_a_sample_report")

    if report:
        st.subheader("Sample Report Results")
        st.caption(
            "Demo data only — these results came from a saved JSON file."
        )

        st.write(
            "**Sample file:**",
            st.session_state.get("contract_a_sample_filename", ""),
        )
        st.write("**Claim ID:**", report.get("claim_id", "Not provided"))

        report_vehicle = report.get("vehicle", {})

        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Make", report_vehicle.get("make", "—"))
        v2.metric("Model", report_vehicle.get("model", "—"))
        v3.metric("Year", report_vehicle.get("year", "—"))
        v4.metric("Fuel", report_vehicle.get("fuel", "—"))

        st.subheader("Detected Damage Entries")
        damages = report.get("damages", [])

        if damages:
            display_damages = []

            for damage in damages:
                confidence = damage.get("confidence")
                if (
                    isinstance(confidence, (int, float))
                    and not isinstance(confidence, bool)
                ):
                    confidence_text = f"{confidence:.0%}"
                else:
                    confidence_text = "—"

                image_index = damage.get("image_index")
                if (
                    isinstance(image_index, int)
                    and not isinstance(image_index, bool)
                    and image_index >= 0
                ):
                    photo_number = image_index + 1
                else:
                    photo_number = "—"

                display_damages.append(
                    {
                        "Part": damage.get("part", "—"),
                        "Damage Type": damage.get("damage_type", "—"),
                        "Severity": damage.get("severity", "—"),
                        "Confidence": confidence_text,
                        "Photo Number": photo_number,
                        "Notes": damage.get("notes", ""),
                    }
                )

            st.dataframe(
                display_damages,
                width="stretch",
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

        # JSON DOWNLOAD
        json_data = json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )

        st.download_button(
            label="⬇️ Download Contract A Report (JSON)",
            data=json_data,
            file_name=st.session_state.get(
                "contract_a_sample_filename",
                "contract_a_report.json",
            ),
            mime="application/json",
            key="download_contract_a_json",
        )

        # PDF DOWNLOAD
        try:
            pdf_data = generate_claim_pdf(report)

            st.download_button(
                label="📄 Download Assessment Report (PDF)",
                data=pdf_data,
                file_name=(
                    f"{report.get('claim_id', 'claim_report')}"
                    "_assessment.pdf"
                ),
                mime="application/pdf",
                key="download_contract_a_pdf",
            )

            st.caption(
                "The PDF contains sample assessment data. "
                "It does not include repair pricing or policy decisions."
            )
        except Exception as error:
            st.error(f"Could not generate the PDF report: {error}")
