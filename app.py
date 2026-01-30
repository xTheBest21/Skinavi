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
# 1. Wir definieren die Grenzen (unten-links und oben-rechts)
# Diese Werte müssen exakt mit IMAGE_BOUNDS übereinstimmen
map_bounds = [[0, 0], [1000, 1400]]

m = folium.Map(
    crs='Simple', 
    min_zoom=0.5,  # Erlaubt ein kleines Puffer-Herauszoomen
    max_zoom=4,
    max_bounds=True, # Aktiviert die Sperre
    location=[500, 700], # Startet in der Mitte des Bildes
    zoom_start=0.5
)

# 2. Die Sperre festlegen: Der Nutzer kann nicht aus diesem Rechteck herauswischen
m.set_max_bounds(map_bounds)

# 3. Das Bild einfügen
folium.raster_layers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=map_bounds,
    opacity=1.0
).add_to(m)

# 4. Sicherstellen, dass die Karte beim Laden das ganze Bild zeigt
m.fit_bounds(map_bounds)

# Helfer-Tool (nur wenn Haken in Sidebar gesetzt)
if show_coords:
    m.add_child(folium.LatLngPopup())
