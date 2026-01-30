import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import requests
import json
import os
import math

# 1. Konfiguration (Titel & Icon wie im Plan)
st.set_page_config(page_title="SkiNavi Sölden", page_icon="⛷️", layout="wide")
st.title("⛷️ Sölden: Digitaler Pistenplan")

DATA_FILE = "soelden_master.json"

def berechne_distanz(pos1, pos2):
    lat1, lon1 = pos1
    lat2, lon2 = pos2
    radius = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# 2. Daten laden
@st.cache_data
def load_ski_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    else:
        url = "http://overpass-api.de/api/interpreter"
        query = """[out:json];(
          way["piste:type"](46.93, 10.95, 47.00, 11.05);
          node["amenity"~"restaurant|bar|cafe"](46.93, 10.95, 47.00, 11.05);
          node["tourism"~"alpine_hut"](46.93, 10.95, 47.00, 11.05);
          way["aerialway"](46.93, 10.95, 47.00, 11.05);
        );out geom;"""
        r = requests.get(url, params={'data': query})
        data = r.json()
        with open(DATA_FILE, "w") as f: json.dump(data, f)
        return data

data = load_ski_data()

# 3. Pistenfarben nach deiner Legende definieren [cite: 125, 131]
pisten_farben = {
    "easy": "#0055ff",       # Blau (leicht) [cite: 126]
    "intermediate": "#ff0000", # Rot (mittel) [cite: 127]
    "advanced": "#000000",   # Schwarz (schwer) [cite: 128]
    "expert": "#000000",
    "skiroute": "#ffaa00"    # Gelb/Orange (Skiroute) [cite: 131]
}

huetten_dict = {}
lifte_dict = {}

for element in data.get('elements', []):
    t = element.get('tags', {})
    name = t.get('name')
    if name:
        if 'aerialway' in t and 'geometry' in element:
            lifte_dict[f"🚠 LIFT: {name}"] = [element['geometry'][0]['lat'], element['geometry'][0]['lon']]
        elif (t.get('amenity') in ['restaurant', 'bar', 'cafe'] or t.get('tourism') == 'alpine_hut'):
            if 'lat' in element and 'lon' in element:
                huetten_dict[f"🏠 HÜTTE: {name}"] = [element['lat'], element['lon']]

alle_ziele = {**huetten_dict, **lifte_dict}

# 4. Standort & Sidebar
st.sidebar.header("📍 Navigation")
modus = st.sidebar.radio("Modus:", ["Manuell", "GPS"], key="nav_mode")

my_pos = None
if modus == "GPS":
    gps = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", key="gps_final")
    if gps: my_pos = [gps['lat'], gps['lon']]
    else: st.info("Suche GPS...")
else:
    start_opt = sorted(huetten_dict.keys()) + sorted(lifte_dict.keys())
    start_name = st.selectbox("Mein Standort:", start_opt)
    my_pos = alle_ziele[start_name]

# 5. Karte im "Sölden-Look"
# --- 5. Die Panorama-Karte (Pistenplan) einbauen ---
# Die Koordinaten sind so gewählt, dass das Bild über Sölden liegt
pistenplan_url = "https://raw.githubusercontent.com/DEIN_USER/DEIN_REPO/main/soelden_pistenplan.jpg"

# Die ungefähren Grenzen des Skigebiets für das Bild
bild_grenzen = [[46.920, 10.930], [47.010, 11.060]] 

m = folium.Map(location=[46.9655, 11.0088], zoom_start=13, tiles=None)

# Das Bild aus deinem PDF als Hintergrund legen
folium.Raster(
    image=pistenplan_url,
    bounds=bild_grenzen,
    opacity=1.0,
    name="Sölden Pistenplan"
).add_to(m)

# Pisten für die Interaktivität (unsichtbar darüberlegen)
for element in data.get('elements', []):
    if 'geometry' in element and 'piste:type' in element.get('tags', {}):
        pts = [(p['lat'], p['lon']) for p in element['geometry']]
        # Wir lassen die Linien fast durchsichtig, damit man den Plan sieht
        folium.PolyLine(pts, color="blue", weight=10, opacity=0.01, 
                        tooltip=element.get('tags', {}).get('name')).add_to(m)

# Marker für Start und Ziel
if my_pos:
    folium.Marker(my_pos, popup="DU", icon=folium.Icon(color='blue', icon='user', prefix='fa')).add_to(m)
    folium.Marker(ziel_coords, popup=reiner_name, icon=folium.Icon(color='red', icon='flag')).add_to(m)
    
    # Notrufnummer aus dem Plan [cite: 149]
    st.error("🆘 **Pistenrettung Sölden:** [+43 5254 508](tel:+435254508)")
