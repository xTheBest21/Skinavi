import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
from folium import plugins

# Seiten-Konfiguration
st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

st.title("⛷️ Ski Navi Sölden (Pistenplan-Edition)")

# 1. Bild-Setup
# WICHTIG: Die Datei muss im selben Ordner wie dein Script liegen!
IMAGE_PATH = "soelden_pistenplan.jpg"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]] # Definition der Bildgröße im Koordinatensystem

@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    
    # KNOTEN (X, Y Koordinaten auf deinem Bild geschätzt)
    # 0,0 ist unten links | 1000, 1400 ist oben rechts
    nodes = {
        "Sölden Tal (Giggijoch)": (50, 950),
        "Giggijoch Berg": (450, 950),
        "Sölden Tal (Gaislachkogl)": (70, 420),
        "Gaislachkogl Mittelstation": (380, 390),
        "Gaislachkogl Gipfel": (620, 280),
        "Hintere Bachlhütte": (350, 700),
        "Rettenbachgletscher": (700, 550),
        "Tiefenbachgletscher": (750, 200),
        "Rotkoglbahn Berg": (550, 750)
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

    # VERBINDUNGEN (Pisten & Lifte)
    edges = [
        ("Sölden Tal (Gaislachkogl)", "Gaislachkogl Mittelstation", "🚠 Lift", "Gaislachkoglbahn I"),
        ("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel", "🚠 Lift", "Gaislachkoglbahn II"),
        ("Gaislachkogl Gipfel", "Gaislachkogl Mittelstation", "⛷️ Piste", "Piste 1"),
        ("Sölden Tal (Giggijoch)", "Giggijoch Berg", "🚠 Lift", "Giggijochbahn"),
        ("Giggijoch Berg", "Hintere Bachlhütte", "⛷️ Piste", "Piste 11"),
        ("Giggijoch Berg", "Rotkoglbahn Berg", "🚠 Lift", "Rotkoglbahn"),
        ("Rotkoglbahn Berg", "Rettenbachgletscher", "🚠 Lift", "Gletscherexpress"),
    ]
    
    for u, v, kind, label in edges:
        G.add_edge(u, v, kind=kind, label=label)
        
    return G, nodes

G, nodes = build_soelden_graph()

# --- SIDEBAR ---
st.sidebar.image(IMAGE_PATH, caption="Sölden Pistenplan")
start_node = st.sidebar.selectbox("Startpunkt:", options=sorted(list(nodes.keys())))
target_node = st.sidebar.selectbox("Zielpunkt:", options=sorted(list(nodes.keys())))
calc_btn = st.sidebar.button("Route berechnen")

# --- KARTE ---
# Wir erstellen eine Karte ohne Hintergrund-Layer (crs=Simple)
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Das Bild als Hintergrund-Layer hinzufügen
folium.RasterLayers.ImageOverlay(
    image=IMAGE_PATH,
    bounds=IMAGE_BOUNDS,
    opacity=1.0,
    interactive=True,
    cross_origin=False
).add_to(m)

# Route einzeichnen
if calc_btn:
    try:
        path = nx.shortest_path(G, source=start_node, target=target_node)
        path_coords = [nodes[node] for node in path]
        
        # Linie zeichnen
        folium.PolyLine(path_coords, color="red", weight=10, opacity=0.7).add_to(m)
        
        # Wegbeschreibung
        st.info(f"Route: {' ➔ '.join(path)}")
    except:
        st.error("Keine Route gefunden!")

# Karte anzeigen
st_folium(m, width=1000, height=700)
