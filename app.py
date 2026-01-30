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

# Link zu deinem Bild auf GitHub (Raw-Link)
IMAGE_URL = "https://github.com/xTheBest21/Skinavi/blob/main/soelden_pistenplan.jpg"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]

@st.cache_resource
def get_image_as_base64(url):
    try:
        # Bild von URL laden (robuster als lokaler Pfad auf dem Server)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        return f"Error: {str(e)}"
    return None

img_b64 = get_image_as_base64(IMAGE_URL)

# 2. Das Ski-Netzwerk
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    # Koordinaten (Y, X) - angepasst an den Plan
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

    edges = [
        ("Gaislachkogl Tal", "Gaislachkogl Mittelstation", "🚠 Lift", "Gaislachkoglbahn I"),
        ("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel", "🚠 Lift", "Gaislachkoglbahn II"),
        ("Gaislachkogl Gipfel", "Gaislachkogl Mittelstation", "⛷️ Piste", "Piste 1"),
        ("Giggijoch Tal", "Giggijoch Berg", "🚠 Lift", "Giggijochbahn"),
        ("Giggijoch Berg", "Rettenbachgletscher", "🚠 Lift", "Gletscherexpress"),
        ("Giggijoch Berg", "Hintere Bachlhütte", "⛷️ Piste", "Piste 11")
    ]
    for u, v, kind, label in edges:
        G.add_edge(u, v, kind=kind, label=label)
    return G, nodes

G, nodes = build_soelden_graph()

# --- UI ---
st.title("⛷️ Ski Navi Sölden")

# Fehlerbehandlung für das Bild (Fix für den SyntaxError in deinem Screenshot)
if img_b64 is None or "Error" in str(img_b64):
    st.error(f"Bildfehler: {img_b64}")
    st.info("Bitte prüfe, ob der Link IMAGE_URL korrekt ist.")
    st.stop()

# Sidebar
st.sidebar.header("Navigation")
start = st.sidebar.selectbox("Start", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Ziel", sorted(nodes.keys()))
show_coords = st.sidebar.checkbox("Koordinaten-Helfer anzeigen")

# --- KARTE ---
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Bild als Base64 einbetten (Die sicherste Methode gegen UnidentifiedImageError)
folium.RasterLayers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_b64}",
    bounds=IMAGE_BOUNDS,
    opacity=1.0
).add_to(m)

# Koordinaten-Helfer für dich
if show_coords:
    m.add_child(folium.LatLngPopup())
    st.sidebar.info("Klicke auf das Bild für Y/X Koordinaten!")

if st.sidebar.button("Weg berechnen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        folium.PolyLine(path_coords, color="red", weight=10, opacity=0.8).add_to(m)
        folium.Marker(nodes[start], icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(nodes[ziel], icon=folium.Icon(color='red')).add_to(m)
        st.success(f"Route gefunden: {' ➔ '.join(path)}")
    except:
        st.error("Keine direkte Verbindung gefunden!")

st_folium(m, width=1000, height=700)
