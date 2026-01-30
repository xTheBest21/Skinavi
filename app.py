import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Setup
st.set_page_config(page_title="Sölden Navi", layout="centered")

# CSS: Erstellt einen zentrierten Kasten für die Karte
st.markdown("""
    <style>
    .stFolium {
        margin: 0 auto;
        display: flex;
        justify-content: center;
        border: 2px solid #ccc;
    }
    .main {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⛷️ Sölden Pistenplan")

# 2. Deine Hütten (Pixel-System)
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [630.0, 750.0], 
    "🏠 Gampe Thaya": [580.0, 680.0],
    "🚠 Giggijoch Tal": [200.0, 850.0]
}

start = st.sidebar.selectbox("Standort:", sorted(pisten_ziele.keys()))
ziel = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()))

# 3. Die Karte (Festes Format)
# Wir setzen die Location genau in die Mitte (500,500)
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs="Simple",
    tiles=None,
    max_bounds=True
)

# 4. Bild-Overlay
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
bild_grenzen = [[0, 0], [1000, 1000]]

folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    zindex=1
).add_to(m)

# 5. DER FIX: Die Kamera auf das Bild zentrieren
m.fit_bounds(bild_grenzen)

# 6. Marker & Linie
pos_a, pos_b = pisten_ziele[start], pisten_ziele[ziel]
folium.Marker(pos_a, popup=start, icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pos_b, popup=ziel, icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5).add_to(m)

# Klick-Hilfe für die Koordinaten
m.add_child(folium.
