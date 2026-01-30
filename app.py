import folium

# Wir erstellen eine Karte, die auf Sölden zentriert ist
# Die Zahlen sind die Koordinaten (Breitengrad, Längengrad)
soelden_karte = folium.Map(location=[46.9655, 11.0088], zoom_start=14, control_scale=True)

# Wir fügen eine Beispiel-Hütte hinzu (z.B. die Gamsstadl)
folium.Marker(
    [46.9415, 10.9835], 
    popup="Gamsstadl Hütte", 
    tooltip="Hier klicken für Route",
    icon=folium.Icon(color="red", icon="home")
).add_to(soelden_karte)

# Wir zeichnen eine Test-Piste (eine einfache blaue Linie)
pisten_koordinaten = [
    [46.9450, 10.9850],
    [46.9415, 10.9835]
]
folium.PolyLine(pisten_koordinaten, color="blue", weight=5, opacity=0.8, tooltip="Piste Nr. 38").add_to(soelden_karte)

# Karte anzeigen
soelden_karte
import requests
import folium

# 1. Die Anfrage an die OpenStreetMap-Datenbank (Overpass API)
# Wir suchen nach Pisten (piste:type) und Liften (aerialway) um Sölden
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
(
  way["piste:type"](46.93, 10.95, 47.00, 11.05);
  way["aerialway"](46.93, 10.95, 47.00, 11.05);
);
out geom;
"""

response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

# 2. Eine neue Karte erstellen
map_soelden = folium.Map(location=[46.9655, 11.0088], zoom_start=13)

# 3. Die Daten auf die Karte zeichnen
for element in data['elements']:
    if 'geometry' in element:
        points = [(p['lat'], p['lon']) for p in element['geometry']]
        
        # Unterscheidung: Lift oder Piste?
        if 'aerialway' in element['tags']:
            color = 'black'  # Lifte sind schwarz
            weight = 3
        else:
            # Pistenfarbe basierend auf Schwierigkeit (falls vorhanden)
            difficulty = element['tags'].get('piste:difficulty', 'unknown')
            color_map = {'easy': 'blue', 'intermediate': 'red', 'advanced': 'black', 'unknown': 'green'}
            color = color_map.get(difficulty, 'green')
            weight = 2
            
        folium.PolyLine(points, color=color, weight=weight).add_to(map_soelden)

map_soelden
import networkx as nx

# Wir erstellen ein leeres Netz
ski_netz = nx.DiGraph() # "Di" steht für "Directed" (gerichtet/Einbahnstraße)

# Wir fügen Wege hinzu: (Start, Ziel, Typ)
ski_netz.add_edge("Bergstation Giggijoch", "Gamsstadl", type="Piste", difficulty="blue")
ski_netz.add_edge("Gamsstadl", "Talstation Silberbrünnl", type="Piste", difficulty="blue")
ski_netz.add_edge("Talstation Silberbrünnl", "Bergstation Silberbrünnl", type="Lift")

# Die App berechnet nun automatisch den Weg
weg = nx.shortest_path(ski_netz, source="Bergstation Giggijoch", target="Bergstation Silberbrünnl")
print(f"Dein Weg: {weg}")
import streamlit as st
from streamlit_folium import st_folium
import folium

# 1. App-Titel und Design
st.set_page_config(page_title="SkiNavi Sölden", layout="centered")
st.title("⛷️ SkiNavi Sölden")

# 2. Auswahl der Zielhütte
huetten = {
    "Gamsstadl": [46.9415, 10.9835],
    "Rettenbachalm": [46.9455, 10.9650],
    "Sonnblick": [46.9720, 11.0110]
}

ziel = st.selectbox("Wohin möchtest du?", list(huetten.keys()))

# 3. Den "Route berechnen" Button
if st.button("Route anzeigen"):
    st.info(f"Berechne Weg zum {ziel}...")
    
    # Karte erstellen
    m = folium.Map(location=huetten[ziel], zoom_start=15)
    
    # Ziel markieren
    folium.Marker(huetten[ziel], popup=ziel, icon=folium.Icon(color='red')).add_to(m)
    
    # Hier würde jetzt dein Routing-Algorithmus die Linie zeichnen
    # Beispielhafte Linie (Piste)
    folium.PolyLine([[46.9500, 10.9800], huetten[ziel]], color="blue", weight=5).add_to(m)
    
    # Karte in der App anzeigen
    st_folium(m, width=700, height=500)
else:
    st.write("Wähle eine Hütte aus und klicke auf den Button.")
    from streamlit_js_eval import streamlit_js_eval

# Wir fragen das Handy nach den GPS-Daten
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", 
    key="get_location"
)

if location:
    my_lat = location['lat']
    my_lon = location['lon']
    st.success(f"Dein Standort wurde gefunden!")
    
    # Jetzt setzen wir den blauen Punkt auf die Karte
    folium.Marker(
        [my_lat, my_lon], 
        popup="Du bist hier", 
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)
