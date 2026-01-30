import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
from PIL import Image
import os

st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

# 1. Bild sicher laden
IMAGE_PATH = "soelden_pistenplan.jpg"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]  # Lokales Koordinatensystem für das Bild

def load_image(path):
    if os.path.exists(path):
        return Image.open(path)
    return None

img = load_image(IMAGE_PATH)

if img is None:
    st.error(f"❌ Datei '{IMAGE_PATH}' nicht gefunden. Bitte lade sie in dein GitHub Repo hoch!")
    st.stop()

# 2. Graph mit Koordinaten passend zum Pistenplan
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    # Koordinaten: (Y, X) wobei 0,0 unten links ist
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

G, nodes = build_soelden_graph()

# --- SIDEBAR ---
st.sidebar.title("⛷️ Ski Navi Sölden")
st.sidebar.image(img, use_container_width=True) # Bild in Sidebar anzeigen

start_node = st.sidebar.selectbox("Start:", options=sorted(list(nodes.keys())))
target_node = st.sidebar.selectbox("Ziel:", options=sorted(list(nodes.keys())))

# --- HAUPTBEREICH (Karte) ---
st.subheader("Interaktiver Pistenplan")

# Erstelle Karte mit 'Simple' Koordinatensystem (kein GPS, nur Bild-Pixel)
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Bild-Overlay hinzufügen
folium.RasterLayers.ImageOverlay(
    image=img, # Wir übergeben das geladene PIL-Objekt direkt
    bounds=IMAGE_BOUNDS,
    opacity=1.0
).add_to(m)
