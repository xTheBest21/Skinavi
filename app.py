import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Seite einrichten
st.set_page_config(page_title="Sölden Profi-Navi", layout="wide")
st.title("⛷️ Sölden: Panorama-Navigator")

# 2. Die Ziele aus deinem Pistenplan (Eich-Koordinaten)
# Diese Werte [Hoch/Runter, Links/Rechts] schieben wir später passend
pisten_ziele = {
    "🏠 HÜTTE: Gampe Thaya": [635, 465],
    "🏠 HÜTTE: Falcon": [715, 310],
    "🚠 LIFT: 12 BEUB Giggijoch": [830, 215],
    "🚠 LIFT: 1 DUB Gaislachkogl I": [290, 160],
    "🚠 LIFT: 5 3SB Wasserkar": [340, 435],
    "⛷️ GIPFEL: Gaislachkogl (3058m)": [240, 95]
}

# 3. Auswahl in der Sidebar
st.sidebar.header("📍 Wohin soll es gehen?")
# Wir nutzen neue Keys, damit Streamlit nicht zurück in den Test-Modus springt
start_sel = st.sidebar.selectbox("Mein Standort:", sorted(pisten_ziele.keys()), key="final_start_v1")
ziel_sel = st.sidebar.selectbox("Mein Ziel:", sorted(pisten_ziele.keys()), key="final_ziel_v1")

# 4. Karte als flaches System für das Bild
bild_grenzen = [[0, 0], [1000, 1000]]
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs=folium.crs.Simple, 
    tiles=None,
    max_bounds=True
)

# 5. Dein Pistenplan als Hintergrund
# Nutze dein Bild aus dem Repository xTheBest21
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"

folium.raster_layers.ImageOverlay(
    url=bild_url,
    bounds=bild_grenzen,
    zindex=1
).add_to(m)

# 6. Marker setzen
pos_a = pisten_ziele[start_sel]
pos_b = pisten_ziele[ziel_sel]

folium.Marker(pos_a, popup=f"START: {start_sel}", icon=folium.Icon(color='blue', icon='play')).add_to(m)
folium.Marker(pos_b, popup=f"ZIEL: {ziel_sel}", icon=folium.Icon(color='red', icon='flag')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5).add_to(m)

# 7. App-Anzeige
st_folium(m, width="100%", height=700, key="soelden_panorama_map")

# Info aus deinem Plan
st.info("💡 Tipp: Nutze die gelbe Linie zur Orientierung zwischen den Liften und Hütten.")
st.error("🆘 Pistenrettung Sölden: +43 5254 508")
