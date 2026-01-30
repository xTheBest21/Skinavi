import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Einfaches Setup
st.set_page_config(page_title="Sölden Navi", layout="wide")
st.title("⛷️ Sölden Pistenplan")

# 2. Auswahlmenü
ziele = {
    "Giggijoch": [46.97, 11.02],
    "Gaislachkogl": [46.93, 10.97]
}
start = st.sidebar.selectbox("Start:", list(ziele.keys()), key="s1")
ziel = st.sidebar.selectbox("Ziel:", list(ziele.keys()), key="z1")

# 3. Die Karte (Ganz simpel ohne CRS-Zusätze)
m = folium.Map(location=[46.95, 11.00], zoom_start=13)

# 4. Das Bild (Pistenplan)
# Wir nutzen die stabilste Methode für das Bild
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=[[46.90, 10.90], [47.00, 11.10]],
    opacity=1.0
).add_to(m)

# 5. Marker
folium.Marker(ziele[start], popup="START").add_to(m)
folium.Marker(ziele[ziel], popup="ZIEL", icon=folium.Icon(color='red')).add_to(m)

# 6. Anzeige
st_folium(m, width="100%", height=600, key="map_v99")
# 2. Deine Ziele (Diese Zahlen musst du jetzt schieben)
# Die erste Zahl schiebt den Marker HOCH/RUNTER
# Die zweite Zahl schiebt den Marker LINKS/RECHTS
pisten_ziele = {
    "🚠 Giggijochbahn": [46.975, 11.030], # Probier diese Werte
    "🚠 Gaislachkoglbahn": [46.935, 10.975],
    "🏠 Gampe Thaya": [46.962, 11.015],
    "🏠 Falcon Restaurant": [46.942, 10.992]
}
