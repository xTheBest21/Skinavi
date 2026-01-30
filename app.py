import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Seite einrichten
st.set_page_config(page_title="Sölden Navi", layout="wide")

# CSS: Erzwingt, dass der Karten-Container zentriert wird
st.markdown("""
    <style>
    .stFolium {
        margin: 0 auto;
        display: flex;
        justify-content: center;
    }
    iframe {
        border-radius: 10px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⛷️ Sölden: Pistenplan Navigator")

# 2. Deine Hütten (Pixel-System)
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [630.0, 750.0], 
    "🏠 Gampe Thaya": [580.0, 680.0],
    "🚠 Giggijoch Tal": [200.0, 850.0]
}

start = st.sidebar.selectbox("Standort:", sorted(pisten_ziele.keys()))
ziel = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()))

# 3. Die Karte (Feste Grenzen)
# Wir setzen die Hintergrundfarbe auf Weiß, damit der graue Rand verschwindet
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs="Simple",
    tiles=None,
    max_bounds=True,
    control_scale=False,
    zoom_control=True
)

# 4. Bild-Overlay
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
bild_grenzen = [[0, 0], [1000, 1000]]

folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    zindex=1
).add_to(m)

# 5. DER FIX: Die Karte auf das Bild zuschneiden
m.fit_bounds(bild_grenzen)

# 6. Marker & Linie
pos_a, pos_b = pisten_ziele[start], pisten_ziele[ziel]
folium.Marker(pos_a, popup=start, icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pos_b, popup=ziel, icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5, opacity=0.8).add_to(m)

# Klick-Hilfe
m.add_child(folium.LatLngPopup())

# 7. Anzeige (Breite auf 100% aber mit max-width)
st_folium(m, width=1000, height=600, key="final_centered_map")
