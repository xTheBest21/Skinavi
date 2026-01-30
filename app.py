import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Konfiguration
st.set_page_config(page_title="SkiNavi Sölden", page_icon="⛷️", layout="wide")
st.title("⛷️ Sölden: Pistenplan Navigator")

# 2. Die "Eichung" (Koordinaten auf deinem Bild)
# Da der Pistenplan ein Panorama ist, nutzen wir ein einfaches 0-1000 System.
# Diese Werte musst du einmalig kurz anpassen, damit die Punkte exakt sitzen.
targets = {
    "🏠 HÜTTE: Gampe Thaya": [650, 450],
    "🏠 HÜTTE: Falcon": [720, 320],
    "🚠 LIFT: Giggijochbahn": [850, 200],
    "🚠 LIFT: Gaislachkoglbahn": [300, 150],
    "🚠 LIFT: Wasserkar": [350, 450],
    "⛷️ BIG 3: Gaislachkogl (3058m)": [250, 100]
}

# 3. Sidebar für die Auswahl
st.sidebar.header("📍 Navigation")
start_name = st.sidebar.selectbox("Wo bist du?", sorted(targets.keys()), key="start")
ziel_name = st.sidebar.selectbox("Wo willst du hin?", sorted(targets.keys()), key="ziel")

# 4. Die Karte (Der "Bilderrahmen")
# Wir nutzen CRS.Simple, damit das Bild flach bleibt und nicht wie eine Erdkugel zoomt
bounds = [[0, 0], [1000, 1000]] # Die Größe des virtuellen Raums

m = folium.Map(
    location=[500, 500], # Startet in der Mitte des Bildes
    zoom_start=1,
    crs=folium.crs.Simple, 
    tiles=None,
    min_zoom=0,
    max_zoom=4,
    max_bounds=True
)

# 5. Dein Pistenplan als Hintergrund
# Ersetze xTheBest21 und den Repository-Namen falls nötig
image_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"

folium.raster_layers.ImageOverlay(
    url=image_url,
    bounds=bounds,
    zindex=1
).add_to(m)

# 6. Marker setzen
start_pos = targets[start_name]
ziel_pos = targets[ziel_name]

folium.Marker(start_pos, popup=f"START: {start_name}", icon=folium.Icon(color='blue', icon='play')).add_to(m)
folium.Marker(ziel_pos, popup=f"ZIEL: {ziel_name}", icon=folium.Icon(color='red', icon='flag')).add_to(m)

# Verbindungslinie (Luftlinie auf dem Plan)
folium.PolyLine([start_pos, ziel_pos], color="yellow", weight=5, opacity=0.7).add_to(m)

# 7. Anzeige in der App
st_folium(m, width="100%", height=700, use_container_width=True)

st.info("💡 **Bedienung:** Wähle links deinen Standort und dein Ziel. Die gelbe Linie zeigt dir die Richtung auf dem Pistenplan.")
