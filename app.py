import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Einfaches Setup
st.set_page_config(page_title="Sölden Navi", layout="wide")
st.title("⛷️ Sölden Pistenplan")

# 2. Deine Ziele (Dictionary sauber definiert)
pisten_ziele = {
    "🚠 Giggijochbahn": [46.975, 11.030],
    "🚠 Gaislachkoglbahn": [46.935, 10.975],
    "🏠 Gampe Thaya": [46.962, 11.015],
    "🏠 Falcon Restaurant": [46.942, 10.992]
}

# 3. Auswahlmenü
st.sidebar.header("Navigation")
start_name = st.sidebar.selectbox("Startpunkt:", sorted(pisten_ziele.keys()), key="s1")
ziel_name = st.sidebar.selectbox("Zielpunkt:", sorted(pisten_ziele.keys()), key="z1")

# 4. Die Karte (Standard-Modus ohne fehleranfällige CRS-Befehle)
m = folium.Map(location=[46.95, 11.00], zoom_start=13)
bild_grenzen = [[46.90, 10.90], [47.00, 11.10]]

m = folium.Map(
    location=[46.95, 11.00], 
    zoom_start=13, 
    min_zoom=12,           # Verhindert zu weites Herauszoomen
    max_zoom=16,           # Verhindert Verpixelung beim Reinzoomen
    max_bounds=True,       # Aktiviert die Begrenzung
    min_lat=bild_grenzen[0][0],
    max_lat=bild_grenzen[1][0],
    min_lon=bild_grenzen[0][1],
    max_lon=bild_grenzen[1][1]
# 5. Dein Pistenplan als Bild
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
# Wir nutzen die stabilste Schreibweise für das Overlay
folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=[[46.90, 10.90], [47.00, 11.10]],
    opacity=1.0
).add_to(m)
folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    opacity=1.0,
    zindex=1
).add_to(m)
# 6. Marker setzen
pos_a = pisten_ziele[start_name]
pos_b = pisten_ziele[ziel_name]

folium.Marker(pos_a, popup="START", icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pos_b, popup="ZIEL", icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5).add_to(m)

# 7. Anzeige
st_folium(m, width="100%", height=600, key="main_map")
