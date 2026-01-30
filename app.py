import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Grund-Einstellungen
st.set_page_config(page_title="SkiNavi Sölden", page_icon="⛷️", layout="wide")
st.title("⛷️ Sölden: Pistenplan Navigator")

# 2. Die Ziele (Hütten & Lifte auf deinem Bild einmessen)
# Wert 1: HOCH/RUNTER (0-1000), Wert 2: LINKS/RECHTS (0-1000)
targets = {
    "🏠 HÜTTE: Gampe Thaya": [635, 465],
    "🏠 HÜTTE: Falcon": [715, 310],
    "🚠 LIFT: Giggijochbahn": [830, 215],
    "🚠 LIFT: Gaislachkoglbahn": [290, 160],
    "🚠 LIFT: Wasserkar": [340, 435],
    "⛷️ BIG 3: Gaislachkogl (3058m)": [240, 95]
}

# 3. Sidebar (NUR EINMAL - löst den DuplicateElementId Fehler)
st.sidebar.header("📍 Navigation")
start_name = st.sidebar.selectbox("Wo bist du?", sorted(targets.keys()), key="user_start")
ziel_name = st.sidebar.selectbox("Wo willst du hin?", sorted(targets.keys()), key="user_target")

# 4. Karte als "Bilderrahmen" (lößt den CRS-Fehler)
# Wir nutzen 0 bis 1000 als festes Koordinatensystem
bounds = [[0, 0], [1000, 1000]]
m = folium.Map(
    location=[500, 500],
    zoom_start=1,
    crs=folium.crs.Simple, # Korrekte Kleinschreibung für folium
    tiles=None,
    min_zoom=0,
    max_zoom=4,
    max_bounds=True
)

# 5. Dein Pistenplan als Hintergrundbild
# WICHTIG: Ersetze xTheBest21 durch deinen GitHub Namen, falls er anders ist
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

# Richtungslinie
folium.PolyLine([start_pos, ziel_pos], color="yellow", weight=5, opacity=0.7).add_to(m)

# 7. App-Anzeige
st_folium(m, width="100%", height=700, use_container_width=True)

st.info("💡 Nutze die Auswahl in der Seitenleiste links, um deine Position auf dem Plan zu markieren.")
