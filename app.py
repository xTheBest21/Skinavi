import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Setup
st.set_page_config(page_title="Sölden Pistenplan-Navi", layout="wide")
st.title("⛷️ Sölden: Interaktiver Pistenplan")

# 2. Die Hütten auf dem Bild (Pixel-Koordinaten von 0 bis 1000)
# [Y = Hoch/Runter, X = Links/Rechts]
# 0,0 ist unten links | 1000,1000 ist oben rechts
pisten_ziele = {
    "🏠 Eugen's Obstlerhütte": [650, 780],  # Diese Zahlen einfach anpassen
    "🏠 Gampe Thaya": [600, 700],
    "🚠 Giggijochbahn Tal": [250, 850],
    "🚠 Gaislachkoglbahn Tal": [250, 150],
    "🏠 Falcon Restaurant": [450, 300]
}

# 3. Auswahl
st.sidebar.header("📍 Ziele auf der Karte")
start_name = st.sidebar.selectbox("Mein Standort:", sorted(pisten_ziele.keys()), key="s_pixel")
ziel_name = st.sidebar.selectbox("Ziel wählen:", sorted(pisten_ziele.keys()), key="z_pixel")

# 4. Karte im "Simple" Modus (Das Bild ist die Welt)
# Wir definieren einen festen Rahmen von 0 bis 1000
bounds = [[0, 0], [1000, 1000]]
m = folium.Map(
    location=[500, 500], 
    zoom_start=1, 
    crs=folium.crs.Simple, # WICHTIG: Nutzt Pixel statt GPS
    tiles=None,
    max_bounds=True
)

# 5. Pistenplan als Hintergrund
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
folium.raster_layers.ImageOverlay(
    url=bild_url,
    bounds=bounds,
    zindex=1
).add_to(m)

# 6. Marker setzen
pos_a = pisten_ziele[start_name]
pos_b = pisten_ziele[ziel_name]

folium.Marker(pos_a, popup=f"HIER: {start_name}", icon=folium.Icon(color='blue', icon='play')).add_to(m)
folium.Marker(pos_b, popup=f"ZIEL: {ziel_name}", icon=folium.Icon(color='red', icon='flag')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5, opacity=0.8).add_to(m)

# 7. Anzeige
st_folium(m, width="100%", height=700, key="pixel_map")
