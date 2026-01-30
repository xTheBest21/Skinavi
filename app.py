import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Konfiguration der Seite
st.set_page_config(page_title="Sölden Ski-Navi", layout="wide")
st.title("⛷️ Sölden: Pistenplan Navigator")

# 2. Ziele definieren (Koordinaten für dein Bild)
pisten_ziele = {
    "🚠 Giggijochbahn": [46.975, 11.030],
    "🚠 Gaislachkoglbahn": [46.935, 10.975],
    "🏠 Gampe Thaya": [46.962, 11.015],
    "🏠 Falcon Restaurant": [46.942, 10.992]
}

# 3. Sidebar für die Auswahl (Eindeutige Keys verhindern Fehler)
st.sidebar.header("📍 Navigation")
start_name = st.sidebar.selectbox("Startpunkt:", sorted(pisten_ziele.keys()), key="s_final_v1")
ziel_name = st.sidebar.selectbox("Ziel:", sorted(pisten_ziele.keys()), key="z_final_v1")

# 4. Karte fest einspannen (Zoom-Begrenzung)
# Wir definieren die Grenzen deines Pistenplans
bild_grenzen = [[46.90, 10.90], [47.00, 11.10]]

m = folium.Map(
    location=[46.95, 11.00], 
    zoom_start=13, 
    min_zoom=13,           # Verhindert, dass man weiter als das Bild rauszoomt
    max_zoom=16, 
    max_bounds=True,       # Aktiviert die Grenze
    min_lat=bild_grenzen[0][0],
    max_lat=bild_grenzen[1][0],
    min_lon=bild_grenzen[0][1],
    max_lon=bild_grenzen[1][1],
    tiles=None             # Entfernt die Standard-Weltkarte im Hintergrund
)

# 5. Den Pistenplan als Bild drüberlegen
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"

folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    opacity=1.0,
    zindex=1,
    interactive=True,
    sticky_bounds=True     # Bild "klebt" an den Rändern
).add_to(m)

# 6. Marker und Verbindungslinie setzen
pos_a = pisten_ziele[start_name]
pos_b = pisten_ziele[ziel_name]

folium.Marker(pos_a, popup="START", icon=folium.Icon(color='blue', icon='play')).add_to(m)
folium.Marker(pos_b, popup="ZIEL", icon=folium.Icon(color='red', icon='flag')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5, opacity=0.7).add_to(m)

# 7. Karte auf die Grenzen zentrieren beim Start
m.fit_bounds(bild_grenzen)

# 8. Anzeige in Streamlit
st_folium(m, width="100%", height=700, key="main_ski_map")

st.info("💡 Der Zoom ist auf den Pistenplan begrenzt. Nutze die Auswahl links für die Navigation.")
