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

# Wir nutzen einen stabilen Link zum Pistenplan
IMAGE_URL = "https://raw.githubusercontent.com/Soelden-Fan/SkiNavi/main/soelden_pistenplan.jpg"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]

@st.cache_resource
def get_map_data(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Bild verarbeiten und zu Base64 konvertieren
            img = Image.open(BytesIO(response.content))
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        return None
    return None

img_b64 = get_map_data(IMAGE_URL)

# 2. Das Ski-Netzwerk
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    # Koordinaten (Y, X) - Schätzwerte für den Plan
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

if img_b64 is None:
    st.error("⚠️ Der Pistenplan konnte nicht geladen werden. Bitte prüfe deine Internetverbindung.")
    st.stop()

# Sidebar
st.sidebar.header("Routenplanung")
start = st.sidebar.selectbox("Startpunkt", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Zielpunkt", sorted(nodes.keys()))
show_helper = st.sidebar.checkbox("Koordinaten-Helfer anzeigen")

# --- Karte ---
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Bild einbetten
folium.RasterLayers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_b64}",
    bounds=IMAGE_BOUNDS,
    opacity=1.0
).add_to(m)

# Klick-Helfer
if show_helper:
    m.add_child(folium.LatLngPopup())
    st.sidebar.info("Klicke auf die Karte für Y/X Koordinaten!")

if st.sidebar.button("Route berechnen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        folium.PolyLine(path_coords, color="red", weight=10, opacity=0.8).add_to(m)
        folium.Marker(nodes[start], icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(nodes[ziel], icon=folium.Icon(color='red')).add_to(m)
        st.success(f"Weg: {' ➔ '.join(path)}")
    except:
        st.error("Keine Verbindung gefunden!")

st_folium(m, width=1000, height=700)
