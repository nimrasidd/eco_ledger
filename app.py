import streamlit as st
import pandas as pd
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ------------------- Auth & Session -------------------

def login():
    st.title("Eco Ledger Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        st.session_state["authenticated"] = True
        st.experimental_rerun()

# ------------------- Company Profile -------------------

def company_profile():
    st.title("Company Profile")
    with st.form("profile_form"):
        name = st.text_input("Company Name")
        industry = st.selectbox("Industry", ["Manufacturing", "Services", "Retail", "Energy"])
        size = st.radio("Company Size", ["Small", "Medium", "Large", "Enterprise"])
        country = st.selectbox("Country", ["UAE", "Saudi Arabia", "Qatar", "Kuwait", "Bahrain", "Oman"])
        city = st.text_input("City")
        area = st.text_input("Area")
        year = st.selectbox("Reporting Year", list(range(2015, 2026)))
        submitted = st.form_submit_button("Save Profile")
        if submitted:
            st.session_state["company"] = {
                "name": name, "industry": industry, "size": size,
                "country": country, "city": city, "area": area, "year": year
            }
            st.success("Profile Saved")

# ------------------- Data Input -------------------

def input_scope(scope):
    st.title(f"Scope {scope} Emissions Input")
    tab1, tab2, tab3 = st.tabs(["Manual Entry", "Upload File", "Estimation Wizard"])

    with tab1:
        st.subheader("Manual Data Entry")
        df = st.data_editor(pd.DataFrame({
            "Activity Type": ["Diesel"],
            "Unit": ["liters"],
            "Quantity": [0],
            "Emission Factor": [2.68],
        }), num_rows="dynamic")
        if st.button(f"Calculate Scope {scope}"):
            df["CO2e"] = df["Quantity"] * df["Emission Factor"]
            st.session_state[f"scope{scope}_data"] = df
            st.success("Calculated Successfully")

    with tab2:
        uploaded = st.file_uploader("Upload Excel/CSV")
        if uploaded:
            data = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
            st.session_state[f"scope{scope}_data"] = data
            st.dataframe(data)

    with tab3:
        st.markdown("Coming soon: Select benchmarks for estimation")

# ------------------- Dashboard -------------------

def dashboard():
    st.title("GHG Emission Dashboard")
    all_data = []
    for scope in [1, 2, 3]:
        data = st.session_state.get(f"scope{scope}_data")
        if data is not None:
            data["Scope"] = f"Scope {scope}"
            all_data.append(data)

    if all_data:
        combined = pd.concat(all_data)
        total = combined.groupby("Scope")["CO2e"].sum().reset_index()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Total Emissions by Scope")
            st.dataframe(total)
        with col2:
            fig = px.pie(total, names="Scope", values="CO2e", title="Scope Contribution")
            st.plotly_chart(fig)

        line = combined.groupby(["Activity Type"])["CO2e"].sum().reset_index()
        fig2 = px.bar(line, x="Activity Type", y="CO2e", title="Emissions by Activity")
        st.plotly_chart(fig2)
    else:
        st.info("Please input data for at least one scope")

# ------------------- Report Generator -------------------

def generate_report():
    st.title("Download Report")
    if st.button("Generate PDF"):
        c = canvas.Canvas("GHG_Report.pdf", pagesize=A4)
        c.drawString(100, 800, f"Company: {st.session_state['company']['name']}")
        c.drawString(100, 780, f"Reporting Year: {st.session_state['company']['year']}")
        c.drawString(100, 760, "GHG Emissions Summary")
        y = 740
        for scope in [1, 2, 3]:
            df = st.session_state.get(f"scope{scope}_data")
            if df is not None:
                total = df["CO2e"].sum()
                c.drawString(100, y, f"Scope {scope}: {total:.2f} tonnes CO2e")
                y -= 20
        c.save()
        with open("GHG_Report.pdf", "rb") as f:
            st.download_button("Download Report", f, file_name="GHG_Report.pdf")

# ------------------- Routing -------------------

def main():
    if "authenticated" not in st.session_state:
        login()
        return

    menu = [
        "Dashboard",
        "Company Profile",
        "Scope 1",
        "Scope 2",
        "Scope 3",
        "Generate Report"
    ]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Dashboard":
        dashboard()
    elif choice == "Company Profile":
        company_profile()
    elif choice == "Scope 1":
        input_scope(1)
    elif choice == "Scope 2":
        input_scope(2)
    elif choice == "Scope 3":
        input_scope(3)
    elif choice == "Generate Report":
        generate_report()

if __name__ == "__main__":
    main()
