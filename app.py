import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import requests
import json
import os    # <--- Das repariert den NameError aus deinem Bild!
import math

# 1. Seite einrichten
st.set_page_config(page_title="SkiNavi Sölden", page_icon="⛷️", layout="wide")
st.title("⛷️ Sölden: Alle Hütten & Pisten")

DATA_FILE = "soelden_total.json"

# 2. Daten laden (Pisten + ALLE Hütten)
# 2. Daten laden (Pisten + Hütten + LIFTE)
@st.cache_data
def load_ski_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        overpass_url = "http://overpass-api.de/api/interpreter"
        # Die Query sucht jetzt nach Pisten, Gastronomie UND Liften (aerialway)
        query = """
        [out:json];
        (
          way["piste:type"](46.93, 10.95, 47.00, 11.05);
          node["amenity"~"restaurant|bar|cafe"](46.93, 10.95, 47.00, 11.05);
          node["tourism"~"alpine_hut"](46.93, 10.95, 47.00, 11.05);
          way["aerialway"](46.93, 10.95, 47.00, 11.05);
        );
        out geom;
        """
        try:
            response = requests.get(overpass_url, params={'data': query})
            data = response.json()
            with open(DATA_FILE, "w") as f:
                json.dump(data, f)
            return data
        except:
            return {"elements": []}

data = load_ski_data()

# 3. Datenbank für Ziele (Hütten & Lifte) erstellen
gefundene_ziele = {}
for element in data.get('elements', []):
    t = element.get('tags', {})
    name = t.get('name')
    
    # Falls es ein Lift (way mit aerialway) ist, nehmen wir den ersten Punkt der Geometrie
    if name and 'aerialway' in t and 'geometry' in element:
        gefundene_ziele[f"🚠 {name}"] = [element['geometry'][0]['lat'], element['geometry'][0]['lon']]
    
    # Falls es eine Hütte (node) ist
    elif name and (t.get('amenity') in ['restaurant', 'bar', 'cafe'] or t.get('tourism') == 'alpine_hut'):
        if 'lat' in element and 'lon' in element:
            gefundene_ziele[f"🏠 {name}"] = [element['lat'], element['lon']]

# 4. GPS & Sortierung (wie gehabt, aber mit Symbolen)
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", 
    key="gps_tracker_v4" 
)

if location:
    my_pos = [location['lat'], location['lon']]
    
    def dist_sort(item):
        return berechne_distanz(my_pos, item[1])
    
    sortierte_liste = sorted(gefundene_ziele.items(), key=dist_sort)
    ziel_auswahl_namen = [f"{name} ({berechne_distanz(my_pos, coords):.1f} km)" for name, coords in sortierte_liste]
    
    auswahl_komplett = st.selectbox("Wohin soll es gehen?", ziel_auswahl_namen)
    reiner_name = auswahl_komplett.split(" (")[0]
    ziel_coords = gefundene_ziele[reiner_name]
else:
    st.warning("Suche Standort...")
    reiner_name = st.selectbox("Ziel wählen:", sorted(gefundene_ziele.keys()))
    ziel_coords = gefundene_ziele[reiner_name]
# 5. Karte & Anzeige
m = folium.Map(location=[46.9655, 11.0088], zoom_start=13)

# Pisten zeichnen (Farbig nach Schwierigkeit)
p_farben = {"easy": "blue", "intermediate": "red", "advanced": "black"}
for element in data.get('elements', []):
    if 'geometry' in element:
        pts = [(p['lat'], p['lon']) for p in element['geometry']]
        diff = element.get('tags', {}).get('piste:difficulty', 'unknown')
        folium.PolyLine(pts, color=p_farben.get(diff, "gray"), weight=2).add_to(m)

if location:
    my_pos = [location['lat'], location['lon']]
    folium.Marker(my_pos, popup="DU", icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker(ziel_coords, popup=ziel_name, icon=folium.Icon(color='red')).add_to(m)
    folium.PolyLine([my_pos, ziel_coords], color="green", dash_array='5, 5').add_to(m)
    
st_folium(m, width="100%", height=600)
import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import requests
import json
import os
import math

# --- FUNKTIONEN ---

def berechne_distanz(pos1, pos2):
    """Berechnet die Entfernung in km zwischen zwei GPS-Punkten"""
    lat1, lon1 = pos1
    lat2, lon2 = pos2
    radius = 6371 # Erd-Radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c

# ... (Hier bleibt dein bisheriger Code für Seite einrichten und Daten laden gleich) ...

# (Wir springen direkt zu Punkt 5: Standort und Ziel eintragen)

if location:
    my_pos = [location['lat'], location['lon']]
    ziel_coords = huetten[ziel_name]
    
    # 1. Distanz berechnen
    distanz = berechne_distanz(my_pos, ziel_coords)
    
    # 2. Navigations-Anweisungen unter der Karte vorbereiten
    st.subheader("📍 Deine Route")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Entfernung", f"{distanz:.2f} km")
    with col2:
        # Schätzung: Skifahrer fahren ca. 20 km/h im Schnitt
        zeit = (distanz / 20) * 60
        st.metric("Geschätzte Zeit", f"{int(zeit)} Min")

    # 3. Anweisungs-Liste
    st.info(f"**Anweisung:** Folge der Richtungspfeil zur {ziel_name}. Nutze vorzugsweise die blauen Pisten in deiner Nähe.")

    # (Hier folgt der Code für die Karte m = folium.Map...)
# ... (dein bisheriger Code bis st_folium) ...

# 6. Interaktive Checkliste für deine Route
st.markdown("---")
st.subheader("📋 Dein Etappen-Plan")

# Wir definieren beispielhafte Etappen für Sölden
# In einer späteren Version werden diese automatisch aus dem Routing generiert
etappen = [
    "🚠 Auffahrt mit der Gaislachkoglbahn I",
    "⛷️ Abfahrt über die blaue Piste Nr. 38",
    "🎿 Kurzer Ziehweg Richtung Gamsstadl",
    "🥘 Einkehr / Ziel erreicht: " + ziel_name
]

# Erstellen der Checkboxen
for etappe in etappen:
    erledigt = st.checkbox(etappe, key=etappe)
    if erledigt:
        st.write(f"✅ *Sehr gut! Weiter geht's.*")

# Ein kleiner Motivations-Fortschrittsbalken
fortschritt = sum([1 for e in etappen if st.session_state.get(e)]) / len(etappen)
st.progress(fortschritt)
st.write(f"Du hast {int(fortschritt * 100)}% deines Weges geschafft!")
