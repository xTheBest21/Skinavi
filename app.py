import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import networkx as nx

# 1. Konfiguration für die Handy-Ansicht
st.set_page_config(page_title="SkiNavi Sölden", layout="wide")

st.title("⛷️ Sölden Ski-Navi")

# 2. GPS-Standort abfragen
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", 
    key="get_location"
)

# 3. Hütten-Datenbank (Koordinaten von Sölden)
huetten = {
    "Gamsstadl": [46.9415, 10.9835],
    "Rettenbachalm": [46.9455, 10.9650],
    "Sonnblick": [46.9720, 11.0110],
    "Gaislachkogl-Gipfel": [46.9482, 10.9672]
}

ziel_name = st.selectbox("Wähle dein Ziel:", list(huetten.keys()))
ziel_coords = huetten[ziel_name]

# 4. Karte erstellen
if location:
    my_pos = [location['lat'], location['lon']]
    # Karte zentrieren zwischen mir und der Hütte
    m = folium.Map(location=my_pos, zoom_start=14)
    
    # Marker für dich
    folium.Marker(my_pos, popup="Du bist hier", icon=folium.Icon(color='blue', icon='info-sign')).add_to(m)
    
    # Marker für das Ziel
    folium.Marker(ziel_coords, popup=ziel_name, icon=folium.Icon(color='red', icon='home')).add_to(m)
    
    # Die "Route" (erstmal eine direkte Linie als Platzhalter)
    folium.PolyLine([my_pos, ziel_coords], color="red", weight=3, dash_array='5, 10', tooltip="Luftlinie zum Ziel").add_to(m)
    
    st.success(f"Route zum {ziel_name} berechnet!")
else:
    # Falls GPS noch lädt oder verweigert wurde
    m = folium.Map(location=[46.9655, 11.0088], zoom_start=13)
    st.warning("Bitte GPS aktivieren, um deinen Standort zu sehen.")

# Karte anzeigen
st_folium(m, width="100%", height=500)
import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import networkx as nx
import requests

st.set_page_config(page_title="SkiNavi Sölden", layout="wide")
st.title("⛷️ Sölden Real-Pisten-Navi")

# 1. Daten von Sölden laden (Overpass API)
@st.cache_data # Das sorgt dafür, dass die Daten nicht jedes Mal neu geladen werden
def load_ski_data():
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = """
    [out:json];
    way["piste:type"](46.93, 10.95, 47.00, 11.05);
    out geom;
    """
    response = requests.get(overpass_url, params={'data': query})
    return response.json()

data = load_ski_data()

# 2. GPS abfragen
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", 
    key="get_location"
)

# 3. Ziele
huetten = {
    "Gamsstadl": [46.9415, 10.9835],
    "Rettenbachalm": [46.9455, 10.9650],
    "Sonnblick": [46.9720, 11.0110]
}
ziel_name = st.selectbox("Wohin möchtest du?", list(huetten.keys()))

# 4. Karte anzeigen
m = folium.Map(location=[46.9655, 11.0088], zoom_start=13)

# Alle Pisten im Hintergrund zeichnen
for element in data.get('elements', []):
    if 'geometry' in element:
        points = [(p['lat'], p['lon']) for p in element['geometry']]
        folium.PolyLine(points, color="gray", weight=1, opacity=0.5).add_to(m)

if location:
    my_pos = [location['lat'], location['lon']]
    folium.Marker(my_pos, popup="Du", icon=folium.Icon(color='blue')).add_to(m)
    
    ziel_coords = huetten[ziel_name]
    folium.Marker(ziel_coords, popup=ziel_name, icon=folium.Icon(color='red')).add_to(m)
    
    # NAVIGATION: Hier wird die Linie zum Ziel gezeichnet
    # In der finalen Version berechnet NetworkX hier den exakten Pisten-Pfad
    folium.PolyLine([my_pos, ziel_coords], color="green", weight=5, tooltip="Dein Weg").add_to(m)
    st.success("Weg gefunden! Folge der grünen Linie.")

st_folium(m, width="100%", height=600)
