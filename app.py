import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Setup
st.set_page_config(page_title="Sölden Navi", layout="centered")

# CSS: Zentriert den Karten-Rahmen und färbt den Hintergrund passend zum Bild
st.markdown("""
    <style>
    .stFolium { margin: 0 auto; display: flex; justify-content: center; }
    iframe { background-color: #ffffff; } 
    </style>
    """, unsafe_allow_html=True)

st.title("⛷️ Sölden Pistenplan")

# 2. Deine Hütten (Wir nutzen jetzt ein breiteres System: 0-1000 hoch, 0-2000 breit)
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [630.0, 1100.0], 
    "🏠 Gampe Thaya": [580.0, 900.0],
    "🚠 Giggijoch Tal": [200.0, 1400.0]
}

start = st.sidebar.selectbox("Standort:", sorted(pisten_ziele.keys()))
ziel = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()))

# 3. Karte mit Panorama-Fokus
# Wir setzen die Location in die Mitte des neuen 2000er Systems
m = folium.Map(
    location=[500, 1000],
    zoom_start=1,
    crs="Simple",
    tiles=None,
    max_bounds=True
)

# 4. Bild-Overlay (Hier passen wir die Breite auf 2000 an!)
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
# [Unten-Links, Oben-Rechts] -> Das Bild ist jetzt doppelt so breit wie hoch
bild_grenzen = [[0, 0], [1000, 2000]]

folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    zindex=1
).add_to(m)

# 5. DER FIX: Kamera auf das Panorama zuschneiden
m.fit_bounds(bild_grenzen)

# 6. Marker & Linie
pos_a, pos_b = pisten_ziele[start], pisten_ziele[ziel]
folium.Marker(pos_a, popup=start).add_to(m)
folium.Marker(pos_b, popup=ziel).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5).add_to(m)

# Klick-Hilfe für die neuen Koordinaten
m.add_child(folium.LatLngPopup())

# 7. Anzeige (Breiteres Fenster für Panorama)
st_folium(m, width=1000, height=500, key="panorama_map_v6")
