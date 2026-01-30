import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
from PIL import Image
import requests
from io import BytesIO
import base64

# 1. Konfiguration
st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

# ANPASSEN: Ersetze 'DEIN_NUTZERNAME' und 'DEIN_REPO' durch deine echten GitHub-Daten
GITHUB_IMAGE_URL = "https://raw.githubusercontent.com/DEIN_NUTZERNAME/DEIN_REPO/main/soelden_pistenplan"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]

def load_image_robust():
    # Versuch 1: Lokal laden
    try:
        img = Image.open("soelden_pistenplan")
        return img
    except:
        # Versuch 2: Von GitHub laden (Fallback)
        try:
            response = requests.get(GITHUB_IMAGE_URL)
            img = Image.open(BytesIO(response.content))
            return img
        except:
            return None

img = load_image_robust()

if img is None:
    st.error("❌ Das Bild konnte nicht geladen werden. Bitte prüfe, ob 'soelden_pistenplan' im GitHub-Ordner liegt.")
    st.stop()

# Bild für Folium vorbereiten (Base64)
buffered = BytesIO()
img.save(buffered, format="JPEG")
img_str = base64.b64encode(buffered.getvalue()).decode()

# 2. Graph / Netzwerk
@st.cache_resource
def build_network():
    G = nx.DiGraph()
    # Koordinaten (Y, X) - 0 bis 1000
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

G, nodes = build_network()

# 3. Sidebar
st.sidebar.title("⛷️ Ski Navi Sölden")
st.sidebar.image(img, use_container_width=True)

start_node = st.sidebar.selectbox("Start:", sorted(nodes.keys()))
target_node = st.sidebar.selectbox("Ziel:", sorted(nodes.keys()))

# 4. Karte
st.subheader("Interaktiver Pistenplan")
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Bild einbetten
folium.RasterLayers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_str}",
    bounds=IMAGE_BOUNDS,
    opacity=1.0
).add_to(m)

if st.sidebar.button("Route berechnen"):
    try:
        path = nx.shortest_path(G, source=start_node, target=target_node)
        path_coords = [nodes[node] for node in path]
        folium.PolyLine(path_coords, color="red", weight=10, opacity=0.8).add_to(m)
        folium.Marker(nodes[start_node], icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(nodes[target_node], icon=folium.Icon(color='red')).add_to(m)
        st.success(f"Route: {' -> '.join(path)}")
    except:
        st.error("Kein Weg gefunden!")

st_folium(m, width=1000, height=700)
