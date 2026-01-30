import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Grundlegendes Setup
st.set_page_config(page_title="Sölden Navi", layout="wide")
st.title("⛷️ Sölden Pistenplan")

# 2. Deine Ziele (Koordinaten für den Standard-Modus)
# Wir nutzen hier GPS-ähnliche Werte, die stabil funktionieren
pisten_ziele = {
    "🏠 HÜTTE: Gampe Thaya": [46.96, 11.00],
    "🏠 HÜTTE: Falcon": [46.94, 10.98],
    "🚠 LIFT: Giggijochbahn": [46.97, 11.02],
    "🚠 LIFT: Gaislachkoglbahn": [46.93, 10.97],
    "⛷️ GIPFEL: Gaislachkogl": [46.92, 10.96]
}

# 3. Auswahl (Eindeutige Namen gegen DuplicateElementId Fehler)
st.sidebar.header("📍 Navigation")
s_node = st.sidebar.selectbox("Startpunkt:", sorted(pisten_ziele.keys()), key="start_1")
z_node = st.sidebar.selectbox("Zielpunkt:", sorted(pisten_ziele.keys()), key="ziel_1")

# 4. Karte (Standard-Modus ohne komplizierte CRS-Befehle)
# Das verhindert die Fehler aus deinen Screenshots!
m = folium.Map(location=[46.95, 11.00], zoom_start=13, tiles=None)

# 5. Bild-Overlay (Der Pistenplan)
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
# Wir spannen das Bild über einen festen Bereich auf
bild_grenzen = [[46.90, 10.90], [47.00, 11.10]]

folium.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    opacity=1.0
).add_to(m)

# 6. Marker setzen
pos_start = pisten_ziele[s_node]
pos_ziel = pisten_ziele[z_node]

folium.Marker(pos_start, popup="START", icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pos_ziel, popup="ZIEL", icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine([pos_start, pos_ziel], color="yellow", weight=5).add_to(m)

# 7. Anzeige
st_folium(m, width="100%", height=600, key="main_map")
