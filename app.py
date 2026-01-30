import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Seite einrichten
st.set_page_config(page_title="Sölden Navi", layout="wide")
st.title("⛷️ Sölden Pistenplan")

# 2. Deine Hütten (Pixel-System 0 bis 1000)
# Hier kannst du später Eugen's Obstlerhütte feinjustieren
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [630, 750], 
    "🏠 Gampe Thaya": [580, 680],
    "🚠 Giggijoch Tal": [200, 850],
    "🏠 Falcon Restaurant": [420, 320]
}

# 3. Auswahl
st.sidebar.header("Navigation")
start = st.sidebar.selectbox("Standort:", sorted(pisten_ziele.keys()), key="s1")
ziel = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()), key="z1")

# 4. Karte erstellen (Die stabilste Methode ohne crs.Simple Fehler)
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs="Simple", 
    tiles=None,
    max_bounds=True
)

# 5. Bild-Overlay (Der direkte Weg)
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"

# Wir nutzen hier die Basis-Funktion von folium, um AttributeError zu vermeiden
folium.ImageOverlay(
    image=bild_url,
    bounds=[[0, 0], [1000, 1000]],
    interactive=True
).add_to(m)

# 6. Marker & Linie
pos_a = pisten_ziele[start]
pos_b = pisten_ziele[ziel]

folium.Marker(pos_a, popup=start, icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(pos_b, popup=ziel, icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5).add_to(m)

# 7. Klick-Hilfe (Zeigt dir Koordinaten beim Klicken an!)
m.add_child(folium.LatLngPopup())

# 8. Anzeige
st_folium(m, width="100%", height=700, key="ski_map_final")
