import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
import requests
import base64
from io import BytesIO
from PIL import Image

# 1. Seite konfigurieren
st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

# FIX FÜR ZEILE 14: Nur eine Zuweisung, saubere Anführungszeichen
IMAGE_URL = "https://raw.githubusercontent.com/xTheBest21/Skinavi/main/soelden_pistenplan.jpg"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]

@st.cache_resource
def get_map_base64(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            # Konvertierung zu RGB behebt den 'UnidentifiedImageError'
            if img.mode != "RGB":
                img = img.convert("RGB")
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        return f"Fehler: {e}"
    return None

img_b64 = get_map_base64(IMAGE_URL)

# 2. Das Ski-Netzwerk (Punkte auf dem Plan)
@st.cache_resource
def build_network():
    G = nx.DiGraph()
    # Koordinaten (Y, X)
    nodes = {
        "Gaislachkogl Tal": (130, 360),
        "Gaislachkogl Mittelstation": (400, 310),
        "Gaislachkogl Gipfel": (610, 280),
        "Giggijoch Tal": (70, 750),
        "Giggijoch Berg": (510, 880),
        "Rettenbachgletscher": (700, 480),
        "Hintere Bachlhütte": (350, 550)
    }
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)
    
    # Beispiel-Verbindungen
    G.add_edge("Gaislachkogl Tal", "Gaislachkogl Mittelstation", label="🚠 Gaislachkoglbahn I")
    G.add_edge("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel", label="🚠 Gaislachkoglbahn II")
    return G, nodes

G, nodes = build_network()

# --- UI ---
st.title("⛷️ Ski Navi Sölden")

if not img_b64 or "Fehler" in str(img_b64):
    st.error(f"⚠️ Bild konnte nicht geladen werden: {img_b64}")
    st.stop()

# Sidebar
start = st.sidebar.selectbox("Start", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Ziel", sorted(nodes.keys()))
show_helper = st.sidebar.checkbox("Koordinaten-Helfer (Klick auf Karte)")

# --- Karte ---
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Bild einbetten
folium.RasterLayers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_b64}",
    bounds=IMAGE_BOUNDS,
    opacity=1.0
).add_to(m)

if show_helper:
    m.add_child(folium.LatLngPopup())

# Route berechnen
if st.sidebar.button("Route anzeigen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        folium.PolyLine(path_coords, color="red", weight=10).add_to(m)
        st.success(f"Weg: {' ➔ '.join(path)}")
    except:
        st.error("Keine Verbindung gefunden.")

st_folium(m, width=1100, height=700)
