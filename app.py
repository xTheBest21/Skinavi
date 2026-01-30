import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Seite einrichten
st.set_page_config(page_title="Sölden Navi", layout="wide")
st.title("⛷️ Sölden: Interaktiver Pistenplan")

# 2. Deine Hütten (Pixel-System 0 bis 1000)
# [Y = Hoch/Runter, X = Links/Rechts]
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [630.0, 750.0], 
    "🏠 Gampe Thaya": [580.0, 680.0],
    "🏠 Falcon Restaurant": [420.0, 320.0],
    "🚠 Giggijoch Tal": [200.0, 850.0]
}

# 3. Auswahlmenü
st.sidebar.header("📍 Navigation")
start_name = st.sidebar.selectbox("Standort:", sorted(pisten_ziele.keys()), key="s1")
ziel_name = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()), key="z1")

# 4. Karte erstellen (Die stabilste Methode)
# Wir nutzen crs="Simple" als Text-String, das ist weniger fehleranfällig
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs="Simple", 
    tiles=None,
    max_bounds=True
)

# 5. Bild-Overlay (Der Panzer-Code ohne Unter-Pfade)
bild_url = "https://raw.githubusercontent.com/xTheBest21/Skinavi/main/soelden_pistenplan.jpg"

folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=[[0, 0], [1000, 1000]], # Das Bild spannt sich von 0 bis 1000 auf
    interactive=True
).add_to(m)
m.fit_bounds([[0, 0], [1000, 1000]])
# 6. Marker & Route
pos_a = pisten_ziele[start_name]
pos_b = pisten_ziele[ziel_name]

folium.Marker(pos_a, popup=start_name, icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pos_b, popup=ziel_name, icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5).add_to(m)

# 7. Klick-Hilfe (Zeigt dir Koordinaten beim Klicken an!)
m.add_child(folium.LatLngPopup())

# Anzeige
st_folium(m, width="100%", height=700, key="centered_ski_map")
