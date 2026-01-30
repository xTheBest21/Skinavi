import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Sölden Profi-Navi", layout="wide")
st.title("⛷️ Sölden: Pistenplan Navigator")

# --- 2. PRÄZISE KOORDINATEN (HIER ANPASSEN) ---
# Erste Zahl: HOCH/RUNTER | Zweite Zahl: LINKS/RECHTS
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [46.9550, 11.0050],
    "🚠 Giggijochbahn": [46.9750, 11.0300],
    "🏠 Gampe Thaya": [46.9620, 11.0150],
    "🏠 Falcon Restaurant": [46.9420, 10.9920],
    "🚠 Gaislachkoglbahn I": [46.9350, 10.9750]
}

# --- 3. NAVIGATION ---
st.sidebar.header("📍 Standort wählen")
start_name = st.sidebar.selectbox("Ich bin hier:", sorted(pisten_ziele.keys()), key="s_v1")
ziel_name = st.sidebar.selectbox("Ich will hierhin:", sorted(pisten_ziele.keys()), key="z_v1")

# --- 4. KARTE & BILD ---
bild_grenzen = [[46.90, 10.90], [47.00, 11.10]]
m = folium.Map(
    location=[46.95, 11.00], 
    zoom_start=14, 
    min_zoom=13, 
    max_bounds=True,
    tiles=None # Keine störende Weltkarte im Hintergrund
)

bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    opacity=1.0,
    zindex=1,
    sticky_bounds=True # Verhindert das "Herauszoomen" über das Bild
).add_to(m)

# --- 5. MARKER SETZEN ---
pos_a = pisten_ziele[start_name]
pos_b = pisten_ziele[ziel_name]

folium.Marker(pos_a, popup=f"START: {start_name}", icon=folium.Icon(color='blue', icon='play')).add_to(m)
folium.Marker(pos_b, popup=f"ZIEL: {ziel_name}", icon=folium.Icon(color='red', icon='flag')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5, opacity=0.8).add_to(m)

m.fit_bounds(bild_grenzen)
st_folium(m, width="100%", height=700, key="ski_map_final")
