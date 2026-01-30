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

# Hilfsfunktion für Entfernung (Haversine Formel)
def berechne_distanz(pos1, pos2):
    lat1, lon1 = pos1
    lat2, lon2 = pos2
    radius = 6371 # Erd-Radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# 2. Daten laden (Pisten, Hütten & Lifte)
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
        try:
            response = requests.get(overpass_url, params={'data': query})
            data = response.json()
            with open(DATA_FILE, "w") as f:
                json.dump(data, f)
            return data
        except:
            return {"elements": []}

data = load_ski_data()

# 3. Ziele sammeln
gefundene_ziele = {}
for element in data.get('elements', []):
    t = element.get('tags', {})
    name = t.get('name')
    if name:
        if 'aerialway' in t and 'geometry' in element:
            gefundene_ziele[f"🚠 {name}"] = [element['geometry'][0]['lat'], element['geometry'][0]['lon']]
        elif (t.get('amenity') in ['restaurant', 'bar', 'cafe'] or t.get('tourism') == 'alpine_hut'):
            if 'lat' in element and 'lon' in element:
                gefundene_ziele[f"🏠 {name}"] = [element['lat'], element['lon']]

# 4. Standort-Modus wählen (In der Seitenleiste)
st.sidebar.header("📍 Standorteinstellungen")
standort_modus = st.sidebar.radio(
    "Wie möchtest du deinen Standort bestimmen?", 
    ["GPS nutzen", "Manuell auswählen"]
)

my_pos = None

if standort_modus == "GPS nutzen":
    location = streamlit_js_eval(
        js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", 
        key="gps_tracker_v6_final"
    )
    if location:
        my_pos = [location['lat'], location['lon']]
    else:
        st.info("Warte auf GPS-Signal... Du kannst in der Seitenleiste links auf 'Manuell auswählen' umschalten.")
else:
    # MANUELLE EINGABE: Hier sind jetzt alle Hütten UND Lifte drin!
    # Wir sortieren die Liste alphabetisch für eine bessere Übersicht
    alle_startpunkte = sorted(gefundene_ziele.keys())
    start_name = st.selectbox(
        "Wo befindest du dich gerade? (Hütte oder Lift wählen)", 
        alle_startpunkte,
        help="Tippe einfach den Namen des Lifts oder der Hütte ein."
    )
    my_pos = gefundene_ziele[start_name]
    st.success(f"Startpunkt gesetzt auf: {start_name}")

# 5. Ziel-Auswahl und Sortierung (Basiert auf manuellem oder GPS-Punkt)
if my_pos:
    # Alle potenziellen Ziele nach Entfernung zum gewählten Startpunkt sortieren
    sortierte_liste = sorted(gefundene_ziele.items(), key=lambda x: berechne_distanz(my_pos, x[1]))
    
    # Die Liste für das Dropdown-Menü aufbereiten
    ziel_auswahl_namen = [f"{n} ({berechne_distanz(my_pos, c):.1f} km)" for n, c in sortierte_liste]
    
    st.markdown("### 🎯 Dein Ziel")
    auswahl_komplett = st.selectbox("Wohin soll es gehen?", ziel_auswahl_namen)
    
    # Namen für die Anzeige und Karte säubern
    reiner_name = auswahl_komplett.split(" (")[0]
    ziel_coords = gefundene_ziele[reiner_name]

    # --- KARTE ---
    m = folium.Map(location=my_pos, zoom_start=15) # Etwas näher ranzoomen
    
    # Startmarker (Blau)
    folium.Marker(
        my_pos, 
        popup="DEIN STANDORT", 
        icon=folium.Icon(color='blue', icon='person', prefix='fa')
    ).add_to(m)
    
    # Zielmarker (Rot)
    folium.Marker(
        ziel_coords, 
        popup=reiner_name, 
        icon=folium.Icon(color='red', icon='home')
    ).add_to(m)
    
    # Verbindungslinie
    folium.PolyLine([my_pos, ziel_coords], color="green", weight=5, opacity=0.8, dash_array='10, 10').add_to(m)
    
    st_folium(m, width="100%", height=500)

    # --- ETAPPEN PLAN ---
    st.markdown("---")
    st.subheader(f"📋 Plan von {standort_modus if standort_modus == 'GPS' else 'deinem Standort'} nach {reiner_name}")
    st.checkbox(f"📍 Start bei {start_name if standort_modus == 'Manuell auswählen' else 'aktuellem GPS'}")
    st.checkbox("⛷️ Piste befahren / Lift nutzen")
    st.checkbox(f"🥘 Ziel erreicht: {reiner_name}")
else:
    # Fallback-Ansicht wenn gar nichts gewählt ist
    st.warning("Bitte wähle einen Standort manuell oder erlaube GPS.")
    m_fallback = folium.Map(location=[46.9655, 11.0088], zoom_start=13)
    st_folium(m_fallback, width="100%", height=400)

# --- NOTRUF ---
st.markdown("---")
st.error("🆘 **Pistenrettung Sölden:** [+43 5254 508-0](tel:+4352545080)")
