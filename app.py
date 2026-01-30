import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import requests
import json
import os

st.set_page_config(
    page_title="SkiNavi Sölden",
    page_icon="⛷️", # Dies wird dein Browser-Tab Icon
    layout="wide",
    initial_sidebar_state="collapsed"
)
# 2. Daten laden (mit Offline-Speicher-Logik)
@st.cache_data
def load_ski_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = """
        [out:json];
        way["piste:type"](46.93, 10.95, 47.00, 11.05);
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

# 3. GPS Standort abrufen
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", 
    key="unique_gps_key" 
)

# 4. Ziel-Auswahl
huetten = {
    "Gamsstadl": [46.9415, 10.9835],
    "Rettenbachalm": [46.9455, 10.9650],
    "Sonnblick": [46.9720, 11.0110]
}
ziel_name = st.selectbox("Wohin möchtest du?", list(huetten.keys()))

# 5. Die Karte bauen
m = folium.Map(location=[46.9655, 11.0088], zoom_start=14)

# Farbschema für Pisten
pisten_farben = {
    "easy": "blue",
    "intermediate": "red",
    "advanced": "black",
    "expert": "black"
}

# Pisten einzeichnen
for element in data.get('elements', []):
    if 'geometry' in element:
        points = [(p['lat'], p['lon']) for p in element['geometry']]
        tags = element.get('tags', {})
        schwierigkeit = tags.get('piste:difficulty', 'unknown')
        farbe = pisten_farben.get(schwierigkeit, "gray")
        
        folium.PolyLine(
            points, 
            color=farbe, 
            weight=3 if farbe != "gray" else 1, 
            opacity=0.7,
            tooltip=tags.get('name', 'Piste')
        ).add_to(m)

# Standort und Ziel eintragen
if location:
    my_pos = [location['lat'], location['lon']]
    folium.Marker(my_pos, popup="Du", icon=folium.Icon(color='blue')).add_to(m)
    
    ziel_coords = huetten[ziel_name]
    folium.Marker(ziel_coords, popup=ziel_name, icon=folium.Icon(color='red')).add_to(m)
    
    # Grüne Orientierungslinie
    folium.PolyLine([my_pos, ziel_coords], color="green", weight=4, dash_array='5, 5').add_to(m)
    st.success("Route bereit! Die gestrichelte Linie zeigt die Richtung.")
else:
    st.info("Warte auf GPS... Bitte oben im Browser 'Erlauben' klicken.")

# Karte anzeigen
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
