import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Setup
st.set_page_config(page_title="Sölden Navi", layout="wide")
st.title("⛷️ Sölden Pistenplan")

# 2. Ziele (Wir nutzen hier Standard-Koordinaten für maximale Stabilität)
pisten_ziele = {
    "🚠 Giggijochbahn": [46.97, 11.02],
    "🚠 Gaislachkoglbahn": [46.93, 10.97],
    "🏠 Gampe Thaya": [46.96, 11.00],
    "🏠 Falcon Restaurant": [46.94, 10.98]
}

# 3. Auswahl
st.sidebar.header("Navigation")
start = st.sidebar.selectbox("Start:", sorted(pisten_ziele.keys()), key="s_final")
ziel = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()), key="z_final")

# 4. Karte (Standard-Modus)
m = folium.Map(location=[46.95, 11.00], zoom_start=13)

# 5. Bild-Overlay (Dein Pistenplan von GitHub)
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
folium.ImageOverlay(image=bild_url, bounds=[[46.90, 10.90], [47.00, 11.10]], opacity=1.0).add_to(m)

# 6. Marker setzen
folium.Marker(pisten_ziele[start], popup="START", icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pisten_ziele[ziel], popup="ZIEL", icon=folium.Icon(color='red')).add_to(m)

# 7. Anzeige
st_folium(m, width="100%", height=700, key="map_v21")
