import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Setup
st.set_page_config(page_title="Sölden Navi", layout="wide")
st.title("⛷️ Sölden Pistenplan")

# 2. Ziele einmessen (Koordinaten 0-1000 auf deinem Bild)
# Format: [HOCH/RUNTER, LINKS/RECHTS]
pisten_ziele = {
    "🚠 Giggijochbahn (Tal)": [200, 800],
    "🚠 Gaislachkoglbahn (Tal)": [200, 300],
    "🏠 Gampe Thaya": [550, 600],
    "🏠 Falcon Restaurant": [400, 350],
    "⛷️ Gaislachkogl Gipfel": [750, 150]
}

# 3. Auswahl
st.sidebar.header("Navigation")
start = st.sidebar.selectbox("Startpunkt:", sorted(pisten_ziele.keys()), key="s1")
ziel = st.sidebar.selectbox("Zielpunkt:", sorted(pisten_ziele.keys()), key="z1")

# 4. Karte im "Bild-Modus" (Verhindert CRS-Fehler)
# Wir definieren einen festen Rahmen von 0 bis 1000
bounds = [[0, 0], [1000, 1000]]
m = folium.Map(
    location=[500, 500], 
    zoom_start=1, 
    crs=folium.crs.Simple, 
    tiles=None,
    max_bounds=True
)

# 5. Bild-Overlay (Dein Bild von GitHub)
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"

folium.raster_layers.ImageOverlay(
    url=bild_url,
    bounds=bounds,
    interactive=True
).add_to(m)

# 6. Marker setzen
folium.Marker(pisten_ziele[start], popup="START", icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pisten_ziele[ziel], popup="ZIEL", icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine([pisten_ziele[start], pisten_ziele[ziel]], color="yellow", weight=5).add_to(m)

# 7. Anzeige
st_folium(m, width="100%", height=700, key="soelden_final_map")
