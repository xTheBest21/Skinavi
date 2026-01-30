import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Setup
st.set_page_config(page_title="Sölden Navi", layout="wide")

# CSS, um die Karte im Streamlit-Fenster zu zentrieren
st.markdown("""
    <style>
    .stFolium {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⛷️ Sölden: Pistenplan")

# 2. Hütten (Pixel-Werte)
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [630.0, 750.0], 
    "🏠 Gampe Thaya": [580.0, 680.0],
    "🚠 Giggijoch Tal": [200.0, 850.0]
}

start = st.sidebar.selectbox("Standort:", sorted(pisten_ziele.keys()))
ziel = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()))

# 3. Karte mit festem Fokus
# Wir nutzen tiles=None und eine Hintergrundfarbe
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

img = folium.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    interactive=True
).add_to(m)

# 5. DER TRICK: Karte auf das Bild zwingen
m.fit_bounds(bild_grenzen)

# 6. Marker & Linie
pos_a, pos_b = pisten_ziele[start], pisten_ziele[ziel]
folium.Marker(pos_a, popup=start, icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pos_b, popup=ziel, icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5).add_to(m)

# Klick-Popup für Koordinaten
m.add_child(folium.LatLngPopup())

# 7. Anzeige mit voller Breite
st_folium(m, width=1200, height=700, key="center_map_v3")
