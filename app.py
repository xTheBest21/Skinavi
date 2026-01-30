import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Sölden Navi Tool", layout="wide")
st.title("⛷️ Sölden: Hütten-Positionierer")

# 1. Deine Hütten-Liste (Pixel-System 0-1000)
# Ändere diese Zahlen nach dem Klicken auf die Karte!
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [630, 750], 
    "🏠 Gampe Thaya": [580, 680],
    "🚠 Giggijoch Tal": [200, 850]
}

# 2. Auswahl
ziel = st.sidebar.selectbox("Suche Hütte:", sorted(pisten_ziele.keys()))

# 3. Karte im Bild-Modus
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs="Simple", 
    tiles=None,
    max_bounds=True
)

# 4. Bild laden
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
folium.raster_layers.ImageOverlay(url=bild_url, bounds=[[0, 0], [1000, 1000]]).add_to(m)

# 5. Marker
folium.Marker(pisten_ziele[ziel], popup=ziel, icon=folium.Icon(color='red')).add_to(m)

# 6. Klick-Funktion aktivieren
m.add_child(folium.LatLngPopup())

# 7. Anzeige
data = st_folium(m, width="100%", height=700)

# 8. HIER ABLESEN:
if data and data.get("last_clicked"):
    st.success(f"Geklickte Position für den Code: [{round(data['last_clicked']['lat'], 1)}, {round(data['last_clicked']['lng'], 1)}]")
    st.write("Kopiere diese Zahlen oben in deine 'pisten_ziele' Liste!")
