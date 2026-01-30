import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Setup & Volle Breite erzwingen
st.set_page_config(page_title="Sölden Navi", layout="wide")

# CSS: Zentriert die Karte und entfernt graue Ränder
st.markdown("""
    <style>
    .main > div { padding: 0; }
    iframe { display: block; margin: 0 auto; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("⛷️ Sölden: Pistenplan Navigator")

# 2. Deine Hütten
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [630.0, 750.0], 
    "🏠 Gampe Thaya": [580.0, 680.0],
    "🏠 Falcon Restaurant": [420.0, 320.0],
    "🚠 Giggijoch Tal": [200.0, 850.0]
}

start = st.sidebar.selectbox("Ich bin bei:", sorted(pisten_ziele.keys()))
ziel = st.sidebar.selectbox("Ich will zu:", sorted(pisten_ziele.keys()))

# 3. Karte im "Simple" Modus (Pixel-System)
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs="Simple", 
    tiles=None,
    max_bounds=True,
    zoom_control=True
)

# 4. Bild laden & Grenzen festlegen
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
bild_grenzen = [[0, 0], [1000, 1000]]

folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    zindex=1
).add_to(m)

# 5. DER FIX: Karte auf das Bild zentrieren
m.fit_bounds(bild_grenzen)

# 6. Marker & Linie
pos_a, pos_b = pisten_ziele[start], pisten_ziele[ziel]
folium.Marker(pos_a, popup=start, icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pos_b, popup=ziel, icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5, opacity=0.8).add_to(m)

# Klick-Hilfe für die Koordinaten
m.add_child(folium.LatLngPopup())

# 7. Anzeige (Feste Breite hilft beim Zentrieren)
st_folium(m, width=1000, height=650, key="centered_map_final")
