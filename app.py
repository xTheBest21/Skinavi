import streamlit as st
import folium
from streamlit_folium import st_folium

# Grund-Setup
st.set_page_config(page_title="SkiNavi Sölden", layout="wide")
st.title("⛷️ Sölden Pistenplan")

# Ziele (Wir nutzen hier einfache Zahlen für die Position auf dem Bild)
ziele = {
    "🏠 Gampe Thaya": [46.96, 11.00],
    "🚠 Giggijochbahn": [46.97, 11.02],
    "🚠 Gaislachkoglbahn": [46.93, 10.97]
}

# Sidebar Auswahl
st.sidebar.header("Navigation")
s = st.sidebar.selectbox("Start:", sorted(ziele.keys()), key="start_point")
z = st.sidebar.selectbox("Ziel:", sorted(ziele.keys()), key="target_point")

# Die Karte (Wir verzichten auf crs.Simple, um Fehler zu vermeiden)
m = folium.Map(location=[46.95, 11.00], zoom_start=13, tiles=None)

# Das Bild (Pistenplan) - Wir nutzen die einfachste Methode
bild_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
folium.ImageOverlay(
    image=bild_url,
    bounds=[[46.90, 10.90], [47.00, 11.10]],
    opacity=1.0
).add_to(m)

# Marker setzen
folium.Marker(ziele[s], popup="START", icon=folium.Icon(color='blue')).add_to(m)
folium.Marker(ziele[z], popup="ZIEL", icon=folium.Icon(color='red')).add_to(m)

# Karte in der App anzeigen
st_folium(m, width="100%", height=600, key="soelden_map")
