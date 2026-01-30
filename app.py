import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Setup: Seite auf maximale Breite
st.set_page_config(page_title="Sölden Navi", layout="wide")

# CSS: Zentriert den Karten-Container im Browser
st.markdown("""
    <style>
    iframe { display: block; margin-left: auto; margin-right: auto; }
    .main > div { padding: 0px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⛷️ Sölden: Pistenplan Navigator")

# 2. Deine Hütten (Pixel-System: 0 bis 1000)
# Eugen's Obstlerhütte ist hier ein Beispielwert
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [650, 750], 
    "🏠 Gampe Thaya": [550, 680],
    "🚠 Giggijoch Tal": [200, 850],
    "🚠 Gaislachkogl Tal": [200, 250]
}

start = st.sidebar.selectbox("Standort:", sorted(pisten_ziele.keys()))
ziel = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()))

# 3. Karte erstellen
# Wir nutzen crs="Simple" für Pixel-Navigation
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs="Simple",
    tiles=None,
    max_bounds=True
)

# 4. Bild-Overlay
# Wir spannen das Bild von 0 bis 1000 auf
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
bild_grenzen = [[0, 0], [1000, 1000]]

folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    zindex=1
).add_to(m)

# 5. DER FIX: Karte zwingen, das Bild komplett auszufüllen
m.fit_bounds(bild_grenzen)

# 6. Marker & Linie
pos_a, pos_b = pisten_ziele[start], pisten_ziele[ziel]
folium.Marker(pos_a, popup=start, icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pos_b, popup=ziel, icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5).add_to(m)

# Klick-Popup für Koordinaten
m.add_child(folium.LatLngPopup())

# 7. Anzeige (Breite angepasst für bessere Zentrierung)
st_folium(m, width=1000, height=600, key="centered_final")
