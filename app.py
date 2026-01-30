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

@st.cache_resource
def get_image_base64(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
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
    
    # Namen jetzt mit Emojis für die Sidebar
    nodes = {
        # 🚠 Lifts / Stationen
        "🚠 Gaislachkogl Tal": (130, 360),
        "🚠 Gaislachkogl Mittel": (400, 310),
        "🚠 Gaislachkogl Gipfel": (610, 280),
        "🚠 Giggijoch Tal": (70, 750),
        "🚠 Giggijoch Berg": (510, 880),
        
        # 🏠 Hütten / Restaurants
        "🏠 Falcon Restaurant": (405, 330),
        "🏠 Annemaries Hütte": (350, 380),
        "🏠 Bubis Schihütte": (320, 400),
        "🏠 Wirtshaus Giggijoch": (515, 895),
        "🏠 Hühnersteign": (450, 820),
        
        # ❄️ Gletscher
        "❄️ Rettenbachferner": (720, 500),
        "❄️ Tiefenbachferner": (750, 250)
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

    # WICHTIG: Die Verbindungen müssen exakt die gleichen Namen 
    # inklusive der Emojis nutzen!
    lifte = [
        ("🚠 Gaislachkogl Tal", "🚠 Gaislachkogl Mittel"),
        ("🚠 Gaislachkogl Mittel", "🚠 Gaislachkogl Gipfel"),
        ("🚠 Giggijoch Tal", "🚠 Giggijoch Berg")
    ]
    
    pisten = [
        ("🚠 Gaislachkogl Gipfel", "🚠 Gaislachkogl Mittel"),
        ("🚠 Gaislachkogl Mittel", "🏠 Falcon Restaurant"),
        ("🏠 Falcon Restaurant", "🚠 Gaislachkogl Mittel"), # Verbindung zurück zur Bahn
        ("🚠 Gaislachkogl Mittel", "🏠 Annemaries Hütte")
    ]
    
    for u, v in lifte + pisten:
        G.add_edge(u, v)
        
    return G, nodes

# --- DATEN LADEN ---
# Dies muss vor dem UI stehen!
G, nodes = build_soelden_graph()

# --- UI ---
st.title("⛷️ Ski Navi Sölden")

if img_data is None or "Fehler" in str(img_data):
    st.error(f"⚠️ Bild konnte nicht geladen werden: {img_data}")
    st.stop()

# Sidebar
start = st.sidebar.selectbox("Start", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Ziel", sorted(nodes.keys()))
show_coords = st.sidebar.checkbox("Koordinaten-Helfer anzeigen")

# --- KARTE ---
map_bounds = [[0, 0], [1000, 1400]]

m = folium.Map(
    crs='Simple',
    location=[500, 700],
    zoom_start=-0.5,
    min_zoom=-2,
    max_zoom=3
)

folium.raster_layers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=map_bounds,
    opacity=1.0,
    interactive=True
).add_to(m)

m.options['maxBounds'] = map_bounds

# Helfer-Tool
if show_coords:
    m.add_child(folium.LatLngPopup())

# --- ROUTE BERECHNEN ---
if st.sidebar.button("Route berechnen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        
        # Route zeichnen
        folium.PolyLine(path_coords, color="red", weight=8, opacity=0.8, popup="Deine Route").add_to(m)
        
        # Marker
        folium.CircleMarker(path_coords[0], radius=8, color="green", fill=True, popup=f"START: {start}").add_to(m)
        folium.CircleMarker(path_coords[-1], radius=8, color="blue", fill=True, popup=f"ZIEL: {ziel}").add_to(m)
        
        st.success(f"Route: {' ➔ '.join(path)}")
    except nx.NetworkXNoPath:
        st.error("Keine Verbindung gefunden!")
    except Exception as e:
        st.error(f"Fehler: {e}")

# --- ANZEIGE ---
st_folium(m, width=1000, height=700, key="main_map")
