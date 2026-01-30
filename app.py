import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
import base64
import requests
from io import BytesIO

# 1. Konfiguration
st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

# Wir nutzen einen stabilen Link zu deinem Bild (oder einem Platzhalter, falls dieser hakt)
# Du kannst hier später deinen eigenen GitHub-Raw-Link einfügen
IMAGE_URL = "https://raw.githubusercontent.com/Soelden-Fan/SkiNavi/main/soelden_pistenplan.jpg" 
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]

@st.cache_resource
def load_map_image(url):
    try:
        response = requests.get(url)
        img_data = response.content
        base64_img = base64.b64encode(img_data).decode()
        return base64_img
    except:
        return None

img_b64 = load_map_image(IMAGE_URL)

# 2. Das Netzwerk (Graph)
@st.cache_resource
def build_soelden_network():
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

G, nodes = build_soelden_network()

# --- UI ---
st.title("⛷️ Ski Navi Sölden")

if not img_b64:
    st.error("Bild-Server nicht erreichbar. Bitte prüfe deine Internetverbindung oder den IMAGE_URL Link.")
    st.stop()

# Sidebar
st.sidebar.header("Navigation")
start = st.sidebar.selectbox("Start", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Ziel", sorted(nodes.keys()))
show_coords = st.sidebar.checkbox("Koordinaten-Helfer anzeigen")

# --- KARTE ---
# Simple-System für flache Bilder
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Bild einbetten
folium.RasterLayers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_b64}",
    bounds=IMAGE_BOUNDS,
    opacity=1.0
).add_to(m)

# Koordinaten-Klick-Tool (für dich zum Bauen)
if show_coords:
    m.add_child(folium.LatLngPopup())
    st.sidebar.info("Klicke auf die Karte, um die Y/X Koordinaten für neue Punkte zu sehen!")

# Route berechnen
if st.sidebar.button("Route anzeigen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        folium.PolyLine(path_coords, color="red", weight=10, opacity=0.8).add_to(m)
        folium.Marker(nodes[start], icon=folium.Icon(color='green', icon='play')).add_to(m)
        folium.Marker(nodes[ziel], icon=folium.Icon(color='red', icon='stop')).add_to(m)
        st.success(f"Weg: {' ➔ '.join(path)}")
    except:
        st.error("Keine Verbindung gefunden.")

# Anzeige
st_folium(m, width=1000, height=700)
