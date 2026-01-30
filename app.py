import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Konfiguration der Seite
st.set_page_config(page_title="Sölden Ski-Navi", layout="wide")
st.title("⛷️ Sölden: Pistenplan Navigator")

# 2. Erweiterte Liste der Ziele (Lifte & Hütten)
# Format: [Hoch/Runter, Links/Rechts] - Schätzwerte für dein Bild
pisten_ziele = {
    # --- LIFTE ---
    "🚠 Giggijochbahn (Zubringer)": [46.975, 11.030],
    "🚠 Gaislachkoglbahn I (Zubringer)": [46.935, 10.975],
    "🚠 Gaislachkoglbahn II": [46.928, 10.965],
    "🚠 Langeggbahn (Verbindung)": [46.955, 11.010],
    "🚠 Silberbrünnl": [46.968, 11.025],
    "🚠 Roßkirpl": [46.972, 11.035],
    "🚠 Hainbachkar": [46.965, 11.020],
    "🚠 Rotkoglbahn": [46.963, 11.040],
    "🚠 Schwarze Schneid I": [46.935, 10.940],
    "🚠 Schwarze Schneid II": [46.930, 10.930],
    "🚠 Tiefenbachbahn": [46.925, 10.920],
    "🚠 Einzeiger": [46.978, 11.045],
    
    # --- HÜTTEN & RESTAURANTS ---
    "🏠 Gampe Thaya": [46.962, 11.015],
    "🏠 Falcon (Mittelstation Gaislach)": [46.942, 10.992],
    "🏠 Ice Q (Gaislachkogl Gipfel)": [46.925, 10.960],
    "🏠 Wirtshaus Giggijoch": [46.967, 11.028],
    "🏠 Rettenbach Market / Gletschertisch": [46.938, 10.945],
    "🏠 Tiefenbach Restaurant": [46.922, 10.915],
    "🏠 Löple Alm": [46.950, 10.995],
    "🏠 Eugen's Obstlerhütte": [46.955, 11.005],
    "🏠 Rotkoglhütte": [46.960, 11.050],
    "🏠 Panorama Alm": [46.970, 11.040],
    "🏠 Bubis Schihütte": [46.945, 10.985]
}

# 3. Sidebar für die Auswahl
st.sidebar.header("📍 Wohin soll es gehen?")
start_name = st.sidebar.selectbox("Mein Standort:", sorted(pisten_ziele.keys()), key="s_final")
ziel_name = st.sidebar.selectbox("Mein Ziel:", sorted(pisten_ziele.keys()), key="z_final")

# 4. Karte fest einspannen (Zoom-Begrenzung)
bild_grenzen = [[46.90, 10.90], [47.00, 11.10]]

m = folium.Map(
    location=[46.95, 11.00], 
    zoom_start=13, 
    min_zoom=13,           # Verhindert zu weites Rauszoomen
    max_zoom=16, 
    max_bounds=True,
    min_lat=bild_grenzen[0][0],
    max_lat=bild_grenzen[1][0],
    min_lon=bild_grenzen[0][1],
    max_lon=bild_grenzen[1][1],
    tiles=None             # Keine Standard-Karte im Hintergrund
)

# 5. Den Pistenplan als Bild drüberlegen
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"

folium.raster_layers.ImageOverlay(
    image=bild_url,
    bounds=bild_grenzen,
    opacity=1.0,
    zindex=1,
    interactive=True,
    sticky_bounds=True
).add_to(m)

# 6. Marker und Verbindungslinie setzen
pos_a = pisten_ziele[start_name]
pos_b = pisten_ziele[ziel_name]

folium.Marker(pos_a, popup=f"START: {start_name}", icon=folium.Icon(color='blue', icon='play')).add_to(m)
folium.Marker(pos_b, popup=f"ZIEL: {ziel_name}", icon=folium.Icon(color='red', icon='flag')).add_to(m)
folium.PolyLine([pos_a, pos_b], color="yellow", weight=5, opacity=0.8).add_to(m)

# 7. Automatisches Zentrieren
m.fit_bounds(bild_grenzen)

# 8. Anzeige
st_folium(m, width="100%", height=700, key="main_ski_map")

st.info(f"Route von **{start_name}** nach **{ziel_name}** wird angezeigt.")
st.error("🆘 Pistenrettung Sölden: +43 5254 508")
