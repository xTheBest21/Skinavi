import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Sölden Navi", layout="wide")
st.title("⛷️ Sölden Pistenplan")

# Einfache Ziele
pisten_ziele = {
    "🏠 HÜTTE: Gampe Thaya": [46.96, 11.00],
    "🚠 LIFT: Giggijochbahn": [46.97, 11.02]
}

# Auswahl
start = st.sidebar.selectbox("Start:", sorted(pisten_ziele.keys()), key="s_new")
ziel = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()), key="z_new")

# Karte
m = folium.Map(location=[46.95, 11.00], zoom_start=12)

# Bild einfügen
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
folium.ImageOverlay(
    image=bild_url,
    bounds=[[46.90, 10.90], [47.00, 11.10]],
    opacity=1.0
).add_to(m)

st_folium(m, width="100%", height=600, key="map_unique")
