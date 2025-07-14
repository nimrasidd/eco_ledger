# EcoLedger App v1.8 – bug‑fix + validation
# -------------------------------------------------------------
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd, io, json
from datetime import datetime

# --- Theme ---
BRAND='#198754'; NAVY='#1B2A4E'; BG='#F4F6FA'
st.set_page_config(page_title='EcoLedger', page_icon='🌿', layout='wide')
st.markdown(f"""<style>body{{background:{BG};}} header{{background:#fff;border-bottom:1px solid #e5e5e5;}}[data-testid=collapsedControl]{{display:none}}section[data-testid=stSidebar]>div:first-child{{background:{NAVY};color:#fff;width:260px}}.stButton>button,.stDownloadButton>button{{background:{BRAND};color:#fff;border:none;border-radius:6px;padding:6px 14px;}}thead tr th:first-child,tbody th{{display:none}}</style>""",unsafe_allow_html=True)

# --- Factors ---
EF = {
    'electricity_kwh':0.43,'diesel_litre':2.68,'petrol_litre':2.31,
    'r134a_kg':1430.0,'r410a_kg':2088.0,'paper_kg':1.3,'water_m3':0.344,
    'business_air_domestic_km':0.27,'business_air_longhaul_km':0.15,'taxi_km':0.251,
    'waste_landfill_kg':1.9,'waste_incineration_kg':2.5,'employee_commute_km':0.15}
SCOPE_CATS={1:['Fuel','Refrigerants'],2:['Energy'],3:['Paper','Water','Business travel','Waste disposal','Employee commute']}
VEH={'Petrol':'petrol_litre','Diesel':'diesel_litre'}
REF={'R-134a':'r134a_kg','R-410a':'r410a_kg'}
TRV={'Domestic air':'business_air_domestic_km','Long-haul air':'business_air_longhaul_km','Taxi':'taxi_km'}
WST={'Landfill':'waste_landfill_kg','Incineration':'waste_incineration_kg'}
INT={'area':200,'occ':1000}; PREM={'Office':200,'Retail':300,'Warehouse':90}
IND=['Services','Banking','Hospitality','Manufacturing','Healthcare','Retail']

# --- Helper funcs ---
