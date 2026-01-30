import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import requests
import json
import os
import math

# 1. Seite einrichten
st.set_page_config(page_title="SkiNavi Sölden", page_icon="⛷️", layout="wide")
st.title("⛷️ Sölden: Pisten, Hütten & Lifte")

DATA_FILE = "soelden_total.json"

# Hilfsfunktion für Entfernung
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
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = """[out:json];(
          way["piste:type"](46.93, 10.95, 47.00, 11.05);
          node["amenity"~"restaurant|bar|cafe"](46.93, 10.95, 47.00, 11.05);
          node["tourism"~"alpine_hut"](46.93, 10.95, 47.00, 11.05);
          way["aerialway"](46.93, 10.95, 47.00, 11.05);
        );out geom;"""
        response = requests.get(overpass_url, params={'data': query})
        data = response.json()
        with open(DATA_FILE, "w") as f: json.dump(data, f)
        return data

data = load_ski_data()

# 3. Ziele sammeln
gefundene_ziele = {}
for element in data.get('elements', []):
    t = element.get('tags', {})
    name = t.get('name')
    if name and 'aerialway' in t and 'geometry' in element:
        gefundene_ziele[f"🚠 {name}"] = [element['geometry'][0]['lat'], element['geometry'][0]['lon']]
    elif name and (t.get('amenity') in ['restaurant', 'bar', 'cafe'] or t.get('tourism') == 'alpine_hut'):
        if 'lat' in element and 'lon' in element:
            gefundene_ziele[f"🏠 {name}"] = [element['lat'], element['lon']]

# 4. Standort & Auswahl
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", 
    key="gps_final_v5"
)

if location:
    my_pos = [location['lat'], location['lon']]
    sortierte_liste = sorted(gefundene_ziele.items(), key=lambda x: berechne_distanz(my_pos, x[1]))
    ziel_namen = [f"{n} ({berechne_distanz(my_
