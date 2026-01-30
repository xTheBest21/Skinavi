import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import requests
import json
import os
import math

# 1. Setup
st.set_page_config(page_title="SkiNavi Sölden", page_icon="⛷️", layout="wide")
st.title("⛷️ Sölden: Pisten-Navigator")

DATA_FILE = "soelden_master_v9.json"

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

# 3. Kategorisierung
huetten_dict = {}
lifte_dict = {}
pisten_info = [] # Speichert Pisten für die Analyse
pisten_farben = {"easy": "blue", "intermediate": "red", "advanced": "black", "expert": "black"}

for element in data.get('elements', []):
    t = element.get('tags', {})
    name = t.get('name', 'Piste')
    if 'piste:type' in t and 'geometry' in element:
        diff = t.get('piste:difficulty', 'unknown')
        pisten_info.append({"name": name, "coords": element['geometry'], "diff": diff})
    elif name:
        if 'aerialway' in t and 'geometry' in element:
            lifte_dict[f"🚠 LIFT: {name}"] = [element['geometry'][0]['lat'], element['geometry'][0]['lon']]
        elif (t.get('amenity') in ['restaurant', 'bar', 'cafe'] or t.get('tourism') == 'alpine_hut'):
            if 'lat' in element and 'lon' in element:
                huetten_dict[f"🏠 HÜTTE: {name}"] = [element['lat'], element['lon']]

alle_ziele = {**huetten_dict, **lifte_dict}

# 4. Sidebar & Standort
st.sidebar.header("📍 Einstellungen")
modus = st.sidebar.radio("Standort-Quelle:", ["Manuell auswählen", "GPS nutzen"], key="nav_mode")

my_pos = None
if modus == "GPS nutzen":
    gps = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", key="gps_v9")
    if gps: my_pos = [gps['lat'], gps['lon']]
    else: st.info("Suche GPS...")
else:
    start_opt = sorted(huetten_dict.keys()) + sorted(lifte_dict.keys())
    start_name = st.selectbox("Startpunkt:", start_opt, key="start_box")
    my_pos = alle_ziele[start_name]

# 5. Routing-Analyse & Karte
if my_pos:
    sortiert = sorted(alle_ziele.items(), key=lambda x: berechne_distanz(my_pos, x[1]))
    auswahl_ziel = st.selectbox("Ziel:", [f"{n} ({berechne_distanz(my_pos, c):.1f} km)" for n, c in sortiert])
    reiner_ziel_name = auswahl_ziel.split(" (")[0]
    ziel_coords = alle_ziele[reiner_ziel_name]

    m = folium.Map(location=my_pos, zoom_start=15)
    
    # Pisten einzeichnen
    pisten_auf_dem_weg = set()
    for p in pisten_info:
        pts = [(pt['lat'], pt['lon']) for pt in p['coords']]
        color = pisten_farben.get(p['diff'], "gray")
        folium.PolyLine(pts, color=color, weight=3, opacity=0.7, tooltip=p['name']).add_to(m)
        
        # Check ob Piste grob in der Nähe der Luftlinie liegt
        p_mid = pts[len(pts)//2]
        if berechne_distanz(my_pos, p_mid) < 1.0: # Pisten im 1km Umkreis
            pisten_auf_dem_weg.add(p['diff'])

    folium.Marker(my_pos, popup="START", icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker(ziel_coords, popup="ZIEL", icon=folium.Icon(color='red')).add_to(m)
    folium.PolyLine([my_pos, ziel_coords], color="green", weight=2, dash_array='5, 5').add_to(m)
    
    st_folium(m, width="100%", height=500)

    # 6. Pisten-Anweisung (DEINE LOGIK)
    st.subheader("🚠 Wegbeschreibung")
    st.write(f"Die grüne Linie zeigt die Richtung. Nutze folgende Pisten:")
    
    if "easy" in pisten_auf_dem_weg:
        st.success("🔵 Blaue Pisten (leicht) sind in deiner Nähe verfügbar.")
    if "intermediate" in pisten_auf_dem_weg:
        st.warning("🔴 Achtung: Du musst rote Pisten (mittelschwer) nutzen.")
    if "advanced" in pisten_auf_dem_weg:
        st.error("⚫ Warnung: Schwarze Pisten (schwer) liegen auf dem Weg!")
    
    st.info("💡 **Tipp:** Orientiere dich an den farbigen Linien auf der Karte, die in Richtung der grünen Markierung verlaufen.")
