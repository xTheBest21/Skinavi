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
    # Deine Stationen
    nodes = {
        "Gaislachkogl Tal": (130, 360),
        "Gaislachkogl Mittelstation": (400, 310),
        "Gaislachkogl Gipfel": (610, 280),
        "Giggijoch Tal": (70, 750),
        "Giggijoch Berg": (510, 880),
        "Rettenbachgletscher": (700, 480)
    }
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

    # Verbindungen
    edges = [
        ("Gaislachkogl Tal", "Gaislachkogl Mittelstation"),
        ("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel"),
        ("Giggijoch Tal", "Giggijoch Berg")
    ]
    for u, v in edges:
        G.add_edge(u, v)
    return G, nodes

G, nodes = build_soelden_graph()

# --- UI ---
st.title("⛷️ Ski Navi Sölden")

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
    zoom_start=10,
    min_zoom=4,
    max_zoom=10
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

# Helfer-Tool
if show_coords:
    m.add_child(folium.LatLngPopup())

# Route berechnen
if st.sidebar.button("Route berechnen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        folium.PolyLine(path_coords, color="red", weight=10).add_to(m)
        st.success(f"Route: {' ➔ '.join(path)}")
    except Exception as e:
        st.error("Keine Verbindung gefunden.")

# Anzeige in Streamlit
st_folium(m, width=1000, height=700)
