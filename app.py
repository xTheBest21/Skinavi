import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import requests

# 1. Seite einrichten
st.set_page_config(page_title="SkiNavi Sölden", layout="wide")
st.title("⛷️ Sölden Real-Pisten-Navi")

# 2. Pisten-Daten laden (nur einmal!)
@st.cache_data
def load_ski_data():
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = """
    [out:json];
    way["piste:type"](46.93, 10.95, 47.00, 11.05);
    out geom;
    """
    try:
        response = requests.get(overpass_url, params={'data': query})
        return response.json()
    except:
        return {"elements": []}

data = load_ski_data()

# 3. GPS Standort abrufen (NUR EINMAL im gesamten Code!)
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
m = folium.Map(location=[46.9655, 11.0088], zoom_start=13)

# Echte Pisten einzeichnen
for element in data.get('elements', []):
    if 'geometry' in element:
        points = [(p['lat'], p['lon']) for p in element['geometry']]
        folium.PolyLine(points, color="gray", weight=1, opacity=0.5).add_to(m)

# Standort und Ziel eintragen
if location:
    my_pos = [location['lat'], location['lon']]
    folium.Marker(my_pos, popup="Du", icon=folium.Icon(color='blue')).add_to(m)
    
    ziel_coords = huetten[ziel_name]
    folium.Marker(ziel_coords, popup=ziel_name, icon=folium.Icon(color='red')).add_to(m)
    
    # Grüne Linie als Orientierung
    folium.PolyLine([my_pos, ziel_coords], color="green", weight=4).add_to(m)
    st.success("Standort gefunden! Grüne Linie zeigt die Richtung.")
else:
    st.info("Warte auf GPS-Signal... Bitte bestätige die Standort-Abfrage im Browser.")

# Karte im Vollbild-Modus anzeigen
st_folium(m, width="100%", height=600)
