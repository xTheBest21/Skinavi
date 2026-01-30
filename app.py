import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import requests
import json
import os
import math

# 1. Konfiguration
st.set_page_config(page_title="SkiNavi Sölden", page_icon="⛷️", layout="wide")
st.title("⛷️ Sölden: Original Pistenplan-Navigator")

DATA_FILE = "soelden_data.json"

# Hilfsfunktion für Distanz (Luftlinie)
def berechne_distanz(pos1, pos2):
    lat1, lon1 = pos1
    lat2, lon2 = pos2
    radius = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# 2. Daten laden (Pisten & Hütten)
@st.cache_data
def load_ski_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    else:
        url = "http://overpass-api.de/api/interpreter"
        query = """[out:json];(
          node["amenity"~"restaurant|bar|cafe"](46.93, 10.95, 47.00, 11.05);
          node["tourism"~"alpine_hut"](46.93, 10.95, 47.00, 11.05);
          way["aerialway"](46.93, 10.95, 47.00, 11.05);
        );out geom;"""
        r = requests.get(url, params={'data': query})
        data = r.json()
        with open(DATA_FILE, "w") as f: json.dump(data, f)
        return data

data = load_ski_data()

# 3. Ziele aufbereiten (34 Lifte, diverse Hütten)
huetten = {}
lifte = {}
for element in data.get('elements', []):
    t = element.get('tags', {})
    name = t.get('name')
    if name:
        if 'aerialway' in t:
            lifte[f"🚠 LIFT: {name}"] = [element['geometry'][0]['lat'], element['geometry'][0]['lon']]
        else:
            huetten[f"🏠 HÜTTE: {name}"] = [element.get('lat'), element.get('lon')]

alle_ziele = {**huetten, **lifte}

# 4. Standort & Ziel Wahl (In der Sidebar für mehr Platz)
st.sidebar.header("📍 Navigation")
start_name = st.sidebar.selectbox("Dein Standort (Start):", sorted(alle_ziele.keys()))
ziel_name = st.sidebar.selectbox("Dein Ziel:", sorted(alle_ziele.keys()))

my_pos = alle_ziele[start_name]
ziel_pos = alle_ziele[ziel_name]

# --- 5. Handy-optimierte Karte ---
# Wir nutzen 'use_container_width=True' und setzen eine feste Höhe, die auf Handys gut aussieht
map_height = 600 # Eine gute Höhe für die meisten Smartphones

# Karten-Objekt mit Start-Zoom für das Panorama
m = folium.Map(
    location=[46.9655, 11.0088], 
    zoom_start=13, 
    tiles=None,
    zoom_control=True, # Wichtig für die Bedienung mit dem Daumen
    scrollWheelZoom=True
)

# Das Bild (Pistenplan) hinzufügen
image_url = "https://raw.githubusercontent.com/xTheBest21/skinavi/main/soelden_pistenplan.jpg"
bild_grenzen = [[46.920, 10.930], [47.010, 11.060]]

folium.raster_layers.ImageOverlay(
    image=image_url,
    bounds=bild_grenzen,
    opacity=1.0,
    interactive=True, # Erlaubt das Klicken auf Markierungen auf dem Bild
    cross_origin=True,
    zindex=1
).add_to(m)

# Marker für Start und Ziel
folium.Marker(my_pos, popup=f"START: {start_name}", icon=folium.Icon(color='blue', icon='play')).add_to(m)
folium.Marker(ziel_pos, popup=f"ZIEL: {ziel_name}", icon=folium.Icon(color='red', icon='flag')).add_to(m)

# Gelbe Linie (Richtungshilfe)
folium.PolyLine([my_pos, ziel_pos], color="yellow", weight=5, opacity=0.8).add_to(m)

# Die Karte in Streamlit anzeigen (optimiert für mobile Container)
st_folium(m, width=None, height=map_height, use_container_width=True)

# Info-Box
distanz = berechne_distanz(my_pos, ziel_pos)
st.info(f"Distanz zwischen {start_name} und {ziel_name}: ca. {distanz:.2f} km")
st.error("🆘 Notruf Pistenrettung: +43 5254 508")

