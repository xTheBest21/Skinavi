import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Grund-Setup
st.set_page_config(page_title="Sölden Pisten-Navi", layout="wide")
st.title("⛷️ Sölden: Interaktiver Pistenplan")

# 2. HÜTTEN-LISTE (Pixel-Werte von 0 bis 1000)
# [Y = Hoch/Runter, X = Links/Rechts]
# Ändere diese Zahlen, um die Hütten auf dem Bild zu verschieben!
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [630, 750], # Beispielwert: weit oben, eher rechts
    "🏠 Gampe Thaya": [580, 680],
    "🏠 Falcon Restaurant": [420, 320],
    "🏠 Ice Q (Gipfel)": [780, 180],
    "🚠 Giggijochbahn Tal": [200, 850],
    "🚠 Gaislachkoglbahn Tal": [200, 250]
}

# 3. Auswahlmenü
st.sidebar.header("📍 Navigation")
start = st.sidebar.selectbox("Mein Standort:", sorted(pisten_ziele.keys()), key="s_px")
ziel = st.sidebar.selectbox("Ziel wählen:", sorted(pisten_ziele.keys()), key="z_px")

# 4. Karte im Bild-Modus (Pixel-System)
# Wir definieren den Rahmen fest von 0 bis 1000
bounds = [[0, 0], [1000, 1000]]
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs="Simple", # Nutzt Pixel statt GPS-Koordinaten
    tiles=None,
    max_bounds=True
)

# 5. Pistenplan als Hintergrundbild
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"

folium.raster_layers.ImageOverlay(
    url=bild_url,
    bounds=bounds,
    interactive=True
).add_to(m)

# 6. Marker & Route einzeichnen
pos_a = pisten_ziele[start
