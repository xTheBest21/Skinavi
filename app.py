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

# FIX FÜR ZEILE 14: Sauberer Link ohne doppelte Namen
IMAGE_URL = "https://raw.githubusercontent.com/xTheBest21/Skinavi/main/soelden_pistenplan.jpg"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]

@st.cache_resource
def get_image_base64(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            # Falls das Bild CMYK oder RGBA ist, konvertieren wir es für Folium zu RGB
            if img.mode != "RGB":
                img = img.convert("RGB")
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        return f"Fehler beim Laden: {str(e)}"
    return None

# Bild laden
img_data = get_image_base64(IMAGE_URL)

# 2. Das Ski-Netzwerk
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    # Deine Stationen (Y, X)
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
    G.add_edge("Gaislachkogl Tal", "Gaislachkogl Mittelstation", label="Gaislachkoglbahn I")
    G.add_edge("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel", label="Gaislachkoglbahn II")
    G.add_edge("Giggijoch Tal", "Giggijoch Berg", label="Giggijochbahn")
    return G, nodes

G, nodes = build_soelden_graph()

# --- Benutzeroberfläche ---
st.title("⛷️ Ski Navi Sölden")

# FIX FÜR ZEILE 71: Richtige Syntax für Fehlermeldungen
if img_data is None or "Fehler" in str(img_data):
    st.error(f"⚠️ {img_data if img_data else 'Bild konnte nicht geladen werden.'}")
    st.info("Tipp: Überprüfe, ob das Bild auf GitHub wirklich 'soelden_pistenplan.jpg' heißt.")
    st.stop()

# Sidebar
start = st.sidebar.selectbox("Startpunkt", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Zielpunkt", sorted(nodes.keys()))
show_helper = st.sidebar.checkbox("Koordinaten-Helfer (Klick auf Karte)")

# --- Karte erstellen ---
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Bild als Overlay hinzufügen
folium.RasterLayers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=IMAGE_BOUNDS,
    opacity=1.0
).add_to(m)

# Klick-Helfer
if show_helper:
    m.add_child(folium.LatLngPopup())

# Routenberechnung
if st.sidebar.button("Route berechnen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        folium.PolyLine(path_coords, color="red", weight=8, opacity=0.8).add_to(m)
        st.success(f"Weg gefunden: {' ➔ '.join(path)}")
    except:
        st.error("Keine Verbindung gefunden!")

# Karte anzeigen
st_folium(m, width=1000, height=700)
