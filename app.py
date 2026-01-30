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

# FIX FÜR ZEILE 14 (aus deinem Screenshot image_80e2da.png)
IMAGE_URL = "https://raw.githubusercontent.com/xTheBest21/Skinavi/main/soelden_pistenplan.jpg"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]

@st.cache_resource
def get_image_as_base64(url):
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

img_b64 = get_image_as_base64(IMAGE_URL)

# 2. Das Ski-Netzwerk
@st.cache_resource
def build_graph():
    G = nx.DiGraph()
    # Beispiel-Punkte
    nodes = {
        "Gaislachkogl Tal": (130, 360),
        "Gaislachkogl Mittelstation": (400, 310),
        "Gaislachkogl Gipfel": (610, 280),
        "Giggijoch Tal": (70, 750),
        "Giggijoch Berg": (510, 880)
    }
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)
    G.add_edge("Gaislachkogl Tal", "Gaislachkogl Mittelstation")
    G.add_edge("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel")
    return G, nodes

G, nodes = build_graph()

# --- UI ---
st.title("⛷️ Ski Navi Sölden")

# FIX FÜR ZEILE 71 (aus deinem Screenshot image_814b55.png)
if img_b64 is None or "Fehler" in str(img_b64):
    st.error(f"⚠️ Bildfehler: {img_b64}")
    st.stop()

# Sidebar
start = st.sidebar.selectbox("Start", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Ziel", sorted(nodes.keys()))
show_coords = st.sidebar.checkbox("Koordinaten-Helfer (Klick auf Karte)")

# --- KARTE ---
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Bild sicher einbetten
folium.RasterLayers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_b64}",
    bounds=IMAGE_BOUNDS,
    opacity=1.0
).add_to(m)

if show_coords:
    m.add_child(folium.LatLngPopup())

if st.sidebar.button("Route berechnen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        folium.PolyLine(path_coords, color="red", weight=10).add_to(m)
        st.success(f"Weg: {' ➔ '.join(path)}")
    except:
        st.error("Keine Verbindung gefunden.")

st_folium(m, width=1000, height=700)
