import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
import base64
import requests
from io import BytesIO
from PIL import Image

# 1. Seite konfigurieren
st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

# Bild-URL
IMAGE_URL = "https://raw.githubusercontent.com/xTheBest21/Skinavi/main/soelden_pistenplan.jpg"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]

@st.cache_resource
def get_image_base64(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            # Wandelt CMYK/RGBA in RGB um (verhindert Fehler bei JPGs)
            if img.mode != "RGB":
                img = img.convert("RGB")
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        return f"Fehler: {str(e)}"
    return None

img_data = get_image_base64(IMAGE_URL)

# 2. Das Ski-Netzwerk
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    
    # Koordinaten (Y, X)
    nodes = {
        "Gaislachkogl Tal": (130, 360),
        "Gaislachkogl Mittel": (400, 310),
        "Gaislachkogl Gipfel": (610, 280),
        "Heidebahn Berg": (450, 420),
        "Wasserkar": (480, 350),
        "Giggijoch Tal": (70, 750),
        "Giggijoch Berg": (510, 880),
        "Rotkogljoch": (620, 780),
        "Silberbrünnl": (580, 950),
        "Langegg": (420, 600),
        "Einzeiger": (550, 620),
        "Rettenbachferner": (720, 500),
        "Tiefenbachferner": (750, 250),
        "Schwarze Schneid": (850, 400)
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

    # 1. LIFTE (Hochfahren)
    lifte = [
        ("Gaislachkogl Tal", "Gaislachkogl Mittel"),
        ("Gaislachkogl Mittel", "Gaislachkogl Gipfel"),
        ("Giggijoch Tal", "Giggijoch Berg"),
        ("Giggijoch Berg", "Rotkogljoch"),
        ("Langegg", "Gaislachkogl Mittel"),
        ("Langegg", "Einzeiger"),
        ("Einzeiger", "Rettenbachferner"),
        ("Rettenbachferner", "Schwarze Schneid")
    ]
    
    # 2. PISTEN (Runterfahren) - HIER KOMMEN SIE HIN
    pisten = [
        ("Gaislachkogl Gipfel", "Gaislachkogl Mittel"), # Abfahrt oben
        ("Gaislachkogl Mittel", "Gaislachkogl Tal"),    # Talabfahrt
        ("Giggijoch Berg", "Langegg"),                 # Verbindungspiste
        ("Rettenbachferner", "Einzeiger"),              # Vom Gletscher zurück
        ("Schwarze Schneid", "Rettenbachferner"),
        ("Schwarze Schneid", "Tiefenbachferner")        # Skitunnel
    ]
    
    # Alle Verbindungen in den Graphen laden
    for u, v in lifte + pisten:
        G.add_edge(u, v)
        
    return G, nodes
# --- UI ---
# 5. UI INITIALISIEREN
st.title("⛷️ Ski Navi Sölden")
start = st.sidebar.selectbox("Start", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Ziel", sorted(nodes.keys()))
show_coords = st.sidebar.checkbox("Koordinaten-Helfer anzeigen")

# Fehlerprüfung
if img_data is None or "Fehler" in str(img_data):
    st.error(f"⚠️ Bild konnte nicht geladen werden: {img_data}")
    st.stop()

# Sidebar
start = st.sidebar.selectbox("Start", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Ziel", sorted(nodes.keys()))
show_coords = st.sidebar.checkbox("Koordinaten-Helfer anzeigen")

# --- KARTE ---
# Wir definieren die Bildgröße
map_bounds = [[0, 0], [1000, 1400]]

# Karte ganz einfach ohne restriktive Parameter erstellen
m = folium.Map(
    crs='Simple',
    location=[500, 700],
    zoom_start=0.01,
    min_zoom=0.01,
    max_zoom=5
)

# Das Bild als Overlay hinzufügen
img_overlay = folium.raster_layers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=map_bounds,
    opacity=1.0,
    interactive=True
).add_to(m)

# 1. Zwingt die Kamera zum Bild
m.fit_bounds(map_bounds)

# 2. DER TRICK: Wir setzen die Grenzen hart per Skript, 
# nachdem die Karte geladen wurde. Das verhindert das "Verschwinden".
m.max_bounds = True
m.options['maxBounds'] = map_bounds
# 7. ROUTEN-BERECHNUNG (DIESEN CODE HIER EINFÜGEN)
if st.sidebar.button("Route berechnen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        
        # Linie zeichnen
        folium.PolyLine(path_coords, color="red", weight=10, opacity=0.7).add_to(m)
        
        # Start-Marker (Grün)
        folium.CircleMarker(path_coords[0], radius=10, color="green", fill=True).add_to(m)
        
        # Ziel-Marker (Blau)
        folium.CircleMarker(path_coords[-1], radius=10, color="blue", fill=True).add_to(m)
        
        st.success(f"Route: {' ➔ '.join(path)}")
    except:
        st.error("Keine Verbindung gefunden!")

# 8. KARTE ANZEIGEN (Das ist immer die letzte Zeile)
st_folium(m, width=1000, height=700)
# Helfer-Tool
if show_coords:
    m.add_child(folium.LatLngPopup())

# Route berechnen
if st.sidebar.button("Route berechnen"):
    try:
        # Den Pfad berechnen
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        
        # 1. Die Route als Linie zeichnen
        folium.PolyLine(
            path_coords, 
            color="red", 
            weight=10, 
            opacity=0.8,
            popup="Deine Route"
        ).add_to(m)
        
        # 2. Start-Punkt markieren (Grün)
        folium.CircleMarker(
            path_coords[0], 
            radius=10, 
            color="green", 
            fill=True, 
            fill_opacity=1,
            popup=f"START: {start}"
        ).add_to(m)
        
        # 3. Ziel-Punkt markieren (Blau)
        folium.CircleMarker(
            path_coords[-1], 
            radius=10, 
            color="blue", 
            fill=True, 
            fill_opacity=1,
            popup=f"ZIEL: {ziel}"
        ).add_to(m)
        
        st.success(f"Route gefunden: {' ➔ '.join(path)}")
        
    except nx.NetworkXNoPath:
        st.error("Keine Verbindung gefunden! Du kommst von hier nicht direkt zum Ziel.")
    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")
# Anzeige in Streamlit
st_folium(m, width=1000, height=700)
