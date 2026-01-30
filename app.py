import streamlit as st
import folium
from streamlit_folium import st_folium
import os

# 1. Konfiguration
st.set_page_config(page_title="SkiNavi Sölden", page_icon="⛷️", layout="wide")
st.title("⛷️ Sölden: Pistenplan Navigator")

# 2. Deine Ziele (Die "Eichung")
# Die ersten Zahlen sind HOCH/RUNTER (0-1000), die zweiten LINKS/RECHTS (0-1000)
targets = {
    "🏠 HÜTTE: Gampe Thaya": [650, 450],
    "🏠 HÜTTE: Falcon": [720, 320],
    "🚠 LIFT: Giggijochbahn": [850, 200],
    "🚠 LIFT: Gaislachkoglbahn": [300, 150],
    "🚠 LIFT: Wasserkar": [350, 450],
    "⛷️ BIG 3: Gaislachkogl (3058m)": [250, 100]
}

# 3. Sidebar Auswahl (NUR EINMAL - verhindert DuplicateElementId)
st.sidebar.header("📍 Navigation")
start_name = st.sidebar.selectbox("Wo bist du?", sorted(targets.keys()), key="start_point")
ziel_name = st.sidebar.selectbox("Wo willst du hin?", sorted(targets.keys()), key="end_point")

# 4. Karte vorbereiten (Eingespannter Bilderrahmen)
bounds = [[0, 0], [1000, 1000]]
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs=folium.CRS.Simple, # Korrekte Schreibweise für CRS
    tiles=None,
    min_zoom=0,
    max_zoom=4,
    max_bounds=True
)

# 5. Pistenplan als Hintergrund
# Ersetze xTheBest21 durch deinen Namen falls nötig
image_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"

folium.raster_layers.ImageOverlay(
    url=image_url,
    bounds=bounds,
    zindex=1
).add_to(m)

# 6. Marker setzen
start_pos = targets[start_name]
ziel_pos = targets[ziel_name]

folium.Marker(start_pos, popup=f"START: {start_name}", icon=folium.Icon(color='blue', icon='play')).add_to(m)
folium.Marker(ziel_pos, popup=f"ZIEL: {ziel_name}", icon=folium.Icon(color='red', icon='flag')).add_to(m)

folium.PolyLine([start_pos, ziel_pos], color="yellow", weight=5, opacity=0.7).add_to(m)

# 7. Anzeige
st_folium(m, width="100%", height=700, use_container_width=True)

st.info("💡 Nutze die Auswahl links, um Marker auf dem Plan zu setzen.")
