import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(
    page_title="Line Restoration Portal",
    page_icon="⚡",
    layout="wide"
)

# ------------------------------
# MASTER DATA
# ------------------------------
VOLTAGES = ["132 kV", "220 kV", "400 kV"]

TOWER_TYPES = [
    "Suspension Tower",
    "Tension Tower",
    "Angle Tower",
    "Dead End Tower",
    "Special Tower"
]

STATUSES = [
    "Reported",
    "Under Removal",
    "Material Mobilized",
    "Under Erection",
    "Charging Clearance Pending",
    "Restored"
]

MATERIAL_TYPES = [
    "Tower",
    "Tension Fittings",
    "Suspension Fittings",
    "Conductor",
    "Mid Span Joint"
]

# ------------------------------
# SESSION STATE
# ------------------------------
if "events" not in st.session_state:
    st.session_state.events = []

if "materials" not in st.session_state:
    st.session_state.materials = []

# ------------------------------
# HEADER
# ------------------------------
st.title("⚡ Line Restoration Portal")
st.markdown("Tower Damage & Restoration Monitoring System")

tabs = st.tabs([
    "Dashboard",
    "Event Entry",
    "Material Entry",
    "Photos",
    "Report"
])

# ==================================================
# EVENT ENTRY
# ==================================================
with tabs[1]:

    st.subheader("Tower Damage Entry")

    col1, col2 = st.columns(2)

    with col1:
        event_name = st.text_input("Event Name")
        line_name = st.text_input("Line Name")
        voltage = st.selectbox("Voltage", VOLTAGES)
        tower_type = st.selectbox("Tower Type", TOWER_TYPES)
        tower_no = st.text_input("Tower Number")

    with col2:
        damage_date = st.date_input("Damage Date", date.today())
        district = st.text_input("District")
        gps = st.text_input("GPS Location")
        status = st.selectbox("Status", STATUSES)

    removal = st.slider(
        "Removal Progress (%)",
        0,
        100,
        0
    )

    erection = st.slider(
        "Erection Progress (%)",
        0,
        100,
        0
    )

    remarks = st.text_area("Remarks")

    if st.button("Save Event"):

        st.session_state.events.append({
            "Event Name": event_name,
            "Line Name": line_name,
            "Voltage": voltage,
            "Tower Type": tower_type,
            "Tower No": tower_no,
            "Damage Date": damage_date,
            "District": district,
            "GPS": gps,
            "Status": status,
            "Removal %": removal,
            "Erection %": erection,
            "Remarks": remarks
        })

        st.success("Event Saved Successfully")

# ==================================================
# MATERIAL ENTRY
# ==================================================
with tabs[2]:

    st.subheader("Material Requirement")

    if len(st.session_state.events) == 0:
        st.warning("Please create event first")

    else:

        event_list = [
            x["Event Name"]
            for x in st.session_state.events
        ]

        event_name = st.selectbox(
            "Select Event",
            event_list
        )

        voltage = st.selectbox(
            "Voltage",
            VOLTAGES
        )

        material_type = st.selectbox(
            "Material Type",
            MATERIAL_TYPES
        )

        description = st.text_input(
            "Description"
        )

        required_qty = st.number_input(
            "Required Qty",
            min_value=0
        )

        available_qty = st.number_input(
            "Available Qty",
            min_value=0
        )

        unit = st.text_input(
            "Unit",
            value="Nos"
        )

        if st.button("Add Material"):

            shortage = max(
                required_qty - available_qty,
                0
            )

            st.session_state.materials.append({
                "Event": event_name,
                "Voltage": voltage,
                "Type": material_type,
                "Description": description,
                "Required": required_qty,
                "Available": available_qty,
                "Shortage": shortage,
                "Unit": unit
            })

            st.success("Material Added")

# ==================================================
# DASHBOARD
# ==================================================
with tabs[0]:

    st.subheader("Dashboard Summary")

    if len(st.session_state.events):

        df = pd.DataFrame(
            st.session_state.events
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Damaged Towers",
            len(df)
        )

        c2.metric(
            "Avg Removal %",
            round(df["Removal %"].mean(), 1)
        )

        c3.metric(
            "Avg Erection %",
            round(df["Erection %"].mean(), 1)
        )

        summary = (
            df.groupby("Voltage")
            .agg({
                "Tower No": "count",
                "Removal %": "mean",
                "Erection %": "mean"
            })
            .reset_index()
        )

        summary.columns = [
            "Voltage",
            "Damaged Towers",
            "Removal %",
            "Erection %"
        ]

        fig = px.bar(
            summary,
            x="Voltage",
            y=[
                "Damaged Towers",
                "Removal %",
                "Erection %"
            ],
            barmode="group"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ==================================================
# PHOTO UPLOAD
# ==================================================
with tabs[3]:

    st.subheader("Site Photographs")

    photos = st.file_uploader(
        "Upload Photos",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if photos:

        for photo in photos:
            st.image(
                photo,
                width=300
            )

# ==================================================
# REPORT
# ==================================================
with tabs[4]:

    st.subheader("Consolidated Report")

    if len(st.session_state.events):

        df = pd.DataFrame(
            st.session_state.events
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        csv = df.to_csv(
            index=False
        )

        st.download_button(
            "Download CSV Report",
            csv,
            "Line_Restoration_Report.csv",
            "text/csv"
        )

    if len(st.session_state.materials):

        st.subheader(
            "Material Summary"
        )

        mdf = pd.DataFrame(
            st.session_state.materials
        )

        st.dataframe(
            mdf,
            use_container_width=True
        )