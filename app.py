import streamlit as st
import folium
from streamlit_folium import st_folium

# Einfaches Setup
st.set_page_config(page_title="Sölden Navi", layout="wide")
st.title("⛷️ Sölden Pistenplan")

# Ziele mit einfachen Koordinaten
pisten_ziele = {
    "🏠 HÜTTE: Gampe Thaya": [46.96, 11.00],
    "🏠 HÜTTE: Falcon": [46.94, 10.98],
    "🚠 LIFT: Giggijochbahn": [46.97, 11.02],
    "🚠 LIFT: Gaislachkoglbahn": [46.93, 10.97]
}

# Sidebar Auswahl
st.sidebar.header("Navigation")
start = st.sidebar.selectbox("Startpunkt:", sorted(pisten_ziele.keys()), key="s1")
ziel = st.sidebar.selectbox("Zielpunkt:", sorted(pisten_ziele.keys()), key="z1")

# Karte erstellen
m = folium.Map(location=[46.95, 11.00], zoom_start=13)

# Bild einfügen (Dein Pistenplan)
bild_url = "https://raw.githubusercontent.com/xTheBest21/Skinavi/main/soelden_pistenplan.jpg"
folium.ImageOverlay(
    image=bild_url,
    bounds=[[46.90, 10.90], [47.00, 11.10]],
    opacity=1.0
).add_to(m)

# Marker setzen
folium.Marker(pisten_ziele[start], popup="START", icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pisten_ziele[ziel], popup="ZIEL", icon=folium.Icon(color='red')).add_to(m)

# Karte anzeigen
st_folium(m, width="100%", height=600, key="map_final")
