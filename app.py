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
st.title("⛷️ Sölden: Profi-Navigator")

DATA_FILE = "soelden_final.json"

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

# 3. Ziele trennen
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

# 4. Standort-Wahl (Sidebar)
st.sidebar.header("📍 Standort")
modus = st.sidebar.radio("Quelle:", ["Manuell auswählen", "GPS nutzen"])

my_pos = None
start_name_display = "Dein Standort"

if modus == "GPS nutzen":
    gps = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", key="gps_v7")
    if gps: 
        my_pos = [gps['lat'], gps['lon']]
    else: 
        st.info("Warte auf GPS... Nutze 'Manuell' falls du drinnen bist.")
else:
    # Kombinierte Liste für Startpunkt
    start_optionen = sorted(huetten_dict.keys()) + sorted(lifte_dict.keys())
    start_name_display = st.selectbox("Wo bist du gerade?", start_optionen)
    my_pos = alle_ziele[start_name_display]

# 5. Ziel & Karte
if my_pos:
    # Nach Distanz sortieren
    sortiert = sorted(alle_ziele.items(), key=lambda x: berechne_distanz(my_pos, x[1]))
    ziel_namen = [f"{n} ({berechne_distanz(my_pos, c):.1f} km)" for n, c in sortiert]
    
    auswahl_ziel = st.selectbox("Wohin möchtest du?", ziel_namen)
    reiner_ziel_name = auswahl_ziel.split(" (")[0]
    ziel_coords = alle_ziele[reiner_ziel_name]

    # Karte
    m = folium.Map(location=my_pos, zoom_start=15)
    folium.Marker(my_pos, popup="START", icon=folium.Icon(color='blue', icon='person', prefix='fa')).add_to(m)
    
    # Farbe: Lift=orange, Hütte=red
    farbe = 'orange' if 'LIFT' in reiner_ziel_name else 'red'
    folium.Marker(ziel_coords, popup=reiner_ziel_name, icon=folium.Icon(color=farbe, icon='star')).add_to(m)
    
    folium.PolyLine([my_pos, ziel_coords], color="green", weight=4, dash_array='5, 5').add_to(m)
    st_folium(m, width="100%", height=500)

    # Checkliste
    st.markdown("---")
    st.subheader("📋 Etappen-Plan")
    st.checkbox(f"Abfahrt von {start_name_display}")
    st.checkbox(f"Ziel {reiner_ziel_name} ansteuern")
