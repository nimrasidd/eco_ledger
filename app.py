
# EcoLedger App v1.7.2 – full code (~330 lines)
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd, io, json
from datetime import datetime

# === Theme ===
BRAND = "#198754"; NAVY = "#1B2A4E"; BG = "#F4F6FA"
st.set_page_config(page_title="EcoLedger", page_icon="🌿", layout="wide")
st.markdown(f"""<style>
body{{background:{BG};}}
header{{background:#fff;border-bottom:1px solid #e5e5e5;}}
[data-testid=collapsedControl]{{display:none}}
section[data-testid=stSidebar]>div:first-child{{background:{NAVY};color:#fff;width:260px}}
.stButton>button,.stDownloadButton>button{{background:{BRAND};color:#fff;border:none;border-radius:6px;padding:6px 14px;}}
thead tr th:first-child,tbody th{{display:none}}
</style>""", unsafe_allow_html=True)

# === Factors ===
EF = {
    "electricity_kwh": 0.43, "diesel_litre": 2.68, "petrol_litre": 2.31,
    "r134a_kg": 1430.0, "r410a_kg": 2088.0,
    "paper_kg": 1.3, "water_m3": 0.344,
    "business_air_domestic_km": 0.27, "business_air_longhaul_km": 0.15, "taxi_km": 0.251,
    "waste_landfill_kg": 1.9, "waste_incineration_kg": 2.5,
    "employee_commute_km": 0.15,
}
SCOPE_CATS = {1:["Fuel","Refrigerants"], 2:["Energy"], 3:["Paper","Water","Business travel","Waste disposal","Employee commute"]}
VEH = {"Petrol":"petrol_litre", "Diesel":"diesel_litre"}
REF = {"R-134a":"r134a_kg", "R-410a":"r410a_kg"}
TRV = {"Domestic air":"business_air_domestic_km", "Long-haul air":"business_air_longhaul_km", "Taxi":"taxi_km"}
WST = {"Landfill":"waste_landfill_kg", "Incineration":"waste_incineration_kg"}
INT = {"area":200, "occ":1000}
PREM = {"Office":200, "Retail":300, "Warehouse":90}
IND = ["Services","Banking","Hospitality","Manufacturing","Healthcare","Retail"]

# === Helpers ===
def add_row(r: pd.DataFrame):
    st.session_state.df = pd.concat([st.session_state.df, r], ignore_index=True)

def enrich(df):
    d=df.copy(); d["ef"]=d.activity_code.map(EF); d["kgCO2e"]=d.quantity*d.ef; d["tCO2e"]=d.kgCO2e/1e3; return d

def export(side=False):
    res=enrich(st.session_state.df); buf=io.BytesIO(); res.to_csv(buf,index=False)
    meta={"company":st.session_state.co,"industry":st.session_state.ind,"year":st.session_state.yr}
    js=json.dumps({**meta,"generated":datetime.utcnow().isoformat(), "activities":res.to_dict("records")}, indent=2)
    st.download_button("CSV",buf.getvalue(),"results.csv",key=("csv_side" if side else "csv_main"))
    st.download_button("JSON",js,"report.json",key=("json_side" if side else "json_main"))

# === Session defaults ===
for k,v in {"df":pd.DataFrame(),"co":"ACME","ind":IND[0],"yr":2025,"scope":2}.items(): st.session_state.setdefault(k,v)

# === Sidebar ===
with st.sidebar:
    st.title("🌿 EcoLedger")
    page=option_menu("Dashboards",["Data Input","Results"],icons=["pencil-fill","bar-chart-fill"],default_index=0,
        styles={"container":{"background":NAVY},"icon":{"color":"#fff"},"nav-link":{"color":"#cfd3ec"},"nav-link-selected":{"background":"#25345d","color":"#fff"}})
    st.markdown("---")
    if not st.session_state.df.empty: export(side=True)

# === Data Input Page ===
if page=="Data Input":
    st.header("Company meta")
    st.text_input("Company",key="co")
    st.selectbox("Industry",IND,key="ind")
    st.number_input("Reporting year",step=1,key="yr")
    st.divider()

    st.selectbox("Scope",[1,2,3],key="scope"); scope=st.session_state.scope
    cat=st.selectbox("Category",SCOPE_CATS[scope])

    if scope==1 and cat=="Fuel":
        f=st.selectbox("Fuel",list(VEH)); econ=st.number_input("L/100km",0.0); km=st.number_input("km/yr",0.0); fleet=st.number_input("Fleet",1,step=1)
        if st.button("Add fleet") and all(x>0 for x in [econ,km,fleet]):
            add_row(pd.DataFrame([{"activity_code":VEH[f],"quantity":km*econ/100*fleet,"unit":"litre","scope":1,"quality":"Measured – fleet"}]))
    elif scope==1 and cat=="Refrigerants":
        r=st.selectbox("Gas",list(REF)); kg=st.number_input("kg",0.0)
        if st.button("Add gas") and kg>0:
            add_row(pd.DataFrame([{"activity_code":REF[r],"quantity":kg,"unit":"kg","scope":1,"quality":"Measured"}]))
    elif scope==2:
        if cat=="Energy":
            kwh=st.number_input("Measured kWh",0.0)
            if st.button("Add kWh") and kwh>0:
                add_row(pd.DataFrame([{"activity_code":"electricity_kwh","quantity":kwh,"unit":"kWh","scope":2,"quality":"Measured"}]))
            st.markdown("### Estimate via proxy")
            proxy=st.selectbox("Proxy",["Floor area","Occupants","Bulk kW","Premise type","Appliance list"])
            kw=None
            if proxy=="Floor area":
                area=st.number_input("m²",0.0)
                if st.button("Add area") and area>0: kw=area*INT["area"]
            elif proxy=="Occupants":
                occ=st.number_input("People",0.0)
                if st.button("Add occ") and occ>0: kw=occ*INT["occ"]
            elif proxy=="Bulk kW":
                tot=st.number_input("kW total",0.0); hrs=st.number_input("Hours",0.0)
                if st.button("Add bulk") and tot>0 and hrs>0: kw=tot*hrs
            elif proxy=="Premise type":
                p=st.selectbox("Prem",list(PREM)); area=st.number_input("Area",0.0)
                if st.button("Add premise") and area>0: kw=area*PREM[p]
            else:
                units=st.number_input("Units",0,step=1); kwu=st.number_input("kW/unit",0.0); hrs=st.number_input("Hours",0.0)
                if st.button("Add appl") and units>0 and kwu>0 and hrs>0: kw=units*kwu*hrs
            if kw: add_row(pd.DataFrame([{"activity_code":"electricity_kwh","quantity":kw,"unit":"kWh","scope":2,"quality":"Estimated – proxy"}]))
    elif scope==3:
        if cat=="Business travel":
            mode=st.selectbox("Mode",list(TRV)); km=st.number_input("km",0.0)
            if st.button("Add travel") and km>0:
                add_row(pd.DataFrame([{"activity_code":TRV[mode],"quantity":km,"unit":"km","scope":3,"quality":"Measured"}]))
        elif cat=="Waste disposal":
            route=st.selectbox("Route",list(WST)); kg=st.number_input("kg",0.0)
            if st.button("Add waste") and kg>0:
                add_row(pd.DataFrame([{"activity_code":WST[route],"quantity":kg,"unit":"kg","scope":3,"quality":"Measured"}]))
        elif cat=="Employee commute":
            emp=st.number_input("Employees",1,step=1); km_emp=st.number_input("km/emp/yr",0.0)
            if st.button("Add commute") and km_emp>0:
                add_row(pd.DataFrame([{"activity_code":"employee_commute_km","quantity":emp*km_emp,"unit":"km","scope":3,"quality":"Measured"}]))
        else:
            qty=st.number_input("Quantity",0.0)
            if st.button("Add row") and qty>0:
                code,unit=("paper_kg","kg") if cat=="Paper" else ("water_m3","m³")
                add_row(pd.DataFrame([{"activity_code":code,"quantity":qty,"unit":unit,"scope":3,"quality":"Measured"}]))

    # live data
    st.dataframe(st.session_state.df) if not st.session_state.df.empty else st.info("No rows yet.")

else:  # Results
    st.title("Results")
    if st.session_state.df.empty:
        st.info("No data")
    else:
        res=enrich(st.session_state.df); st.dataframe(res)
        summ=res.groupby(["scope","quality"],as_index=False)["tCO2e"].sum()
        if not summ.empty:
            st.bar_chart(summ.pivot(index="scope",columns="quality",values="tCO2e"))
        export(side=False)
