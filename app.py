import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
from PIL import Image
import os
import base64
from io import BytesIO

# 1. Grundkonfiguration
st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

IMAGE_PATH = "soelden_pistenplan.jpg"
# Lokales Koordinatensystem: Y von 0-1000, X von 0-1400
IMAGE_BOUNDS = [[0, 0], [1000, 1400]] 

# Hilfsfunktion: Bild in Base64 umwandeln (verhindert Ladeprobleme im Browser)
def get_image_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# 2. Bild laden
if os.path.exists(IMAGE_PATH):
    try:
        pil_img = Image.open(IMAGE_PATH)
        img_base64 = get_image_base64(pil_img)
    except Exception as e:
        st.error(f"Fehler beim Verarbeiten des Bildes: {e}")
        st.stop()
else:
    st.error(f"Datei '{IMAGE_PATH}' nicht gefunden! Bitte lade sie direkt neben der app.py in GitHub hoch.")
    st.stop()

# 3. Das Netzwerk (Graph)
@st.cache_resource
def build_network():
    G = nx.DiGraph()
    # Koordinaten (Y, X) - angepasst an das Bildformat
    nodes = {
        "Gaislachkogl Tal": (130, 360),
        "Gaislachkogl Mittelstation": (400, 310),
        "Gaislachkogl Gipfel": (610, 280),
        "Giggijoch Tal": (70, 750),
        "Giggijoch Berg": (510, 880),
        "Rettenbachgletscher": (700, 480),
        "Tiefenbachgletscher": (720, 150),
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

# --- UI Sidebar ---
st.sidebar.title("⛷️ Ski Navi Sölden")
st.sidebar.image(pil_img, caption="Aktueller Pistenplan", use_container_width=True)

start_node = st.sidebar.selectbox("Wo bist du?", options=sorted(list(nodes.keys())))
target_node = st.sidebar.selectbox("Wo willst du hin?", options=sorted(list(nodes.keys())))

# --- Hauptbereich: Karte ---
st.subheader("Interaktive Navigation")

# Karte mit Simple-CRS (für flache Bilder)
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Das Bild als Base64-Overlay (sehr robust)
folium.RasterLayers.ImageOverlay(image=f"data:image/jpeg;base64,{img_base64}", bounds=IMAGE_BOUNDS, opacity=1.0).add_to(m)

# Routenberechnung
if st.sidebar.button("Route berechnen"):
    try:
        path = nx.shortest_path(G, source=start_node, target=target_node)
        path_coords = [nodes[node] for node in path]
        
        # Linie und Marker zeichnen
        folium.PolyLine(path_coords, color="red", weight=8, opacity=0.8).add_to(m)
        folium.Marker(nodes[start_node], popup="START", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(nodes[target_node], popup="ZIEL", icon=folium.Icon(color='red')).add_to(m)
        
        st.success(f"Weg gefunden: {' ➔ '.join(path)}")
    except nx.NetworkXNoPath:
        st.error("Keine Verbindung zwischen diesen Punkten möglich.")

# Karte anzeigen
st_folium(m, width=1100, height=750)
