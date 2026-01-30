import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Setup
st.set_page_config(page_title="Sölden Navi", layout="wide")

# CSS: Entfernt alle Abstände und zentriert das iframe-Element
st.markdown("""
    <style>
    .block-container { padding: 1rem; }
    iframe { width: 100%; display: block; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

st.title("⛷️ Sölden: Pistenplan")

# 2. Hütten (Pixel-System)
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [630.0, 750.0], 
    "🏠 Gampe Thaya": [580.0, 680.0],
    "🚠 Giggijoch Tal": [200.0, 850.0]
}

start = st.sidebar.selectbox("Standort:", sorted(pisten_ziele.keys()))
ziel = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()))

# 3. Karte erstellen
# Wir lassen die Location weg und nutzen nur fit_bounds
m = folium.Map(
    crs="Simple",
    tiles=None,
    max_bounds=True,
    zoom_control=True
)

# 4. Bild-Overlay
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
# Wir spannen das Bild groß auf
bild_grenzen = [[0, 0], [1000, 1500]] # 1500 Breite, falls dein Bild eher breit ist

folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    zindex=1
).add_to(m)

# 5. DER ENTSCHEIDENDE FIX:
# Wir zwingen die Karte, genau diesen Bereich als "Sichtfeld" zu nehmen
m.fit_bounds(bild_grenzen)

# 6. Marker & Linie
pos_a, pos_b = pisten_ziele[start], pisten_ziele[ziel]
folium.Marker(pos_a, popup=start).add_to(m)
folium.Marker(pos_b, popup=ziel).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5).add_to(m)

# Klick-Hilfe
m.add_child(folium.LatLngPopup())

# 7. Anzeige
# Nutze use_container_width=True, damit Streamlit die Breite regelt
st_folium(m, use_container_width=True, height=600, key="force_center_map")
