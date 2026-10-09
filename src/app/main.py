
import streamlit as st

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
    "Prototype UI: damage detection, repair estimates, and policy analysis "
    "will be connected after the team modules are integrated."
)

st.header("1. Vehicle Information")

col1, col2 = st.columns(2)

with col1:
    make = st.text_input("Vehicle make", placeholder="e.g., Maruti Suzuki")
    model = st.text_input("Vehicle model", placeholder="e.g., Swift")
    year = st.number_input(
        "Manufacturing year",
        min_value=1980,
        max_value=2026,
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
    help="Use clear photos showing the damaged areas from different angles.",
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
                    use_container_width=True,
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
        st.write("Vehicle:", make, model, year)
        st.write("Fuel type:", fuel_type)
        st.write("Photos uploaded:", len(uploaded_files))
        st.info(
            "This is a UI test only. No damage detection, cost calculation, "
            "or policy analysis has run yet."
        )
