import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Absolut sauberes Setup
st.set_page_config(page_title="Sölden Navi Profi", layout="wide")
st.title("⛷️ Sölden Pistenplan-Navigator")

# 2. Deine Ziele (Eich-Koordinaten für dein Bild)
# Format: [HOCH/RUNTER, LINKS/RECHTS]
pisten_ziele = {
    "🏠 HÜTTE: Gampe Thaya": [635, 465],
    "🏠 HÜTTE: Falcon": [715, 310],
    "🚠 LIFT: Giggijochbahn": [830, 215],
    "🚠 LIFT: Gaislachkoglbahn": [290, 160],
    "🚠 LIFT: Wasserkar": [340, 435],
    "⛷️ BIG 3: Gaislachkogl (3058m)": [240, 95]
}

# 3. Sidebar mit absolut eindeutigen Namen (verhindert DuplicateElementId)
st.sidebar.header("📍 Einstellungen")
start_sel = st.sidebar.selectbox("Wo bist du?", sorted(pisten_ziele.keys()), key="box_start_final")
ziel_sel = st.sidebar.selectbox("Wohin willst du?", sorted(pisten_ziele.keys()), key="box_ziel_final")

# 4. Karte als flaches Bild-System
bild_grenzen = [[0, 0], [1000, 1000]]
soelden_map = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs="Simple", # Einfache Schreibweise um Attribut-Fehler zu vermeiden
    tiles=None,
    min_zoom=0,
    max_zoom=4,
    max_bounds=True
)

# 5. Pistenplan einbinden (xTheBest21)
bild_url = "https://raw.githubusercontent.com/xTheBest21/Skinavi/main/soelden_pistenplan.jpg"

folium.raster_layers.ImageOverlay(
    url=bild_url,
    bounds=bild_grenzen,
    zindex=1,
    interactive=True
).add_to(soelden_map)

# 6. Marker setzen
pos_a = pisten_ziele[start_sel]
pos_b = pisten_ziele[ziel_sel]

folium.Marker(pos_a, popup="START", icon=folium.Icon(color='blue', icon='play')).add_to(soelden_map)
folium.Marker(pos_b, popup="ZIEL", icon=folium.Icon(color='red', icon='flag')).add_to(soelden_map)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5).add_to(soelden_map)

# 7. Anzeige
st_folium(soelden_map, width="100%", height=700, key="map_widget_final")

st.error("🆘 Pistenrettung Sölden: +43 5254 508")
