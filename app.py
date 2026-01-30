import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
from PIL import Image
import os

# Konfiguration der Seite
st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

# 1. Bild-Pfad definieren
# Stelle sicher, dass die Datei exakt so heißt wie im GitHub-Repo
IMAGE_PATH = "soelden_pistenplan.jpg"
# Lokales Koordinatensystem für das Bild (0 bis 1000 für die Achsen)
IMAGE_BOUNDS = [[0, 0], [1000, 1400]] 

# Funktion zum sicheren Laden des Bildes
def get_ski_map():
    if os.path.exists(IMAGE_PATH):
        try:
            return Image.open(IMAGE_PATH)
        except Exception as e:
            st.error(f"Fehler beim Öffnen des Bildes: {e}")
            return None
    return None

img_data = get_ski_map()

# 2. Das Ski-Netzwerk (Graph) aufbauen
@st.cache_resource
def build_ski_network():
    G = nx.DiGraph()
    
    # KNOTEN: (Y, X) Koordinaten auf dem Bild geschätzt
    # 0,0 ist unten links | 1000, 1400 ist oben rechts
    nodes = {
        "Sölden Tal (Giggijoch)": (70, 750),
        "Giggijoch Berg": (510, 880),
        "Sölden Tal (Gaislachkogl)": (130, 360),
        "Gaislachkogl Mittelstation": (400, 310),
        "Gaislachkogl Gipfel": (610, 280),
        "Hintere Bachlhütte": (350, 550),
        "Rettenbachgletscher": (700, 480),
        "Tiefenbachgletscher": (720, 150),
        "Rotkoglbahn Berg": (530, 680)
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

    # KANTEN: (Start, Ziel, Typ, Name)
    connections = [
        ("Sölden Tal (Gaislachkogl)", "Gaislachkogl Mittelstation", "🚠 Lift", "Gaislachkoglbahn I"),
        ("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel", "🚠 Lift", "Gaislachkoglbahn II"),
        ("Gaislachkogl Gipfel", "Gaislachkogl Mittelstation", "⛷️ Piste", "Piste 1 (Rot)"),
        ("Gaislachkogl Mittelstation", "Hintere Bachlhütte", "⛷️ Piste", "Piste 5 (Rot)"),
        ("Sölden Tal (Giggijoch)", "Giggijoch Berg", "🚠 Lift", "Giggijochbahn"),
        ("Giggijoch Berg", "Hintere Bachlhütte", "⛷️ Piste", "Piste 11 (Blau)"),
        ("Giggijoch Berg", "Rotkoglbahn Berg", "🚠 Lift", "Rotkoglbahn"),
        ("Rotkoglbahn Berg", "Rettenbachgletscher", "🚠 Lift", "Gletscherexpress"),
    ]
    
    for u, v, kind, label in connections:
        G.add_edge(u, v, kind=kind, label=label)
        
    return G, nodes

# Prüfen ob Bild da ist, sonst stoppen
if img_data is None:
    st.error(f"⚠️ Die Datei '{IMAGE_PATH}' wurde nicht gefunden. Bitte lade sie in dein GitHub-Hauptverzeichnis hoch!")
    st.stop()

G, nodes = build_ski_network()

# --- UI Layout ---
st.title("⛷️ Ski Navi Sölden")

# Sidebar für Auswahl
st.sidebar.header("Routenplaner")
start_point = st.sidebar.selectbox("Startpunkt wählen:", options=sorted(list(nodes.keys())))
end_point = st.sidebar.selectbox("Ziel wählen:", options=sorted(list(nodes.keys())))

# Button zur Berechnung
if st.sidebar.button("Weg berechnen"):
    try:
        # Kürzester Pfad mit NetworkX
        path = nx.shortest_path(G, source=start_point, target=end_point)
        
        st.sidebar.success("Route berechnet!")
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            data = G.get_edge_data(u, v)
            st.sidebar.write(f"**{i+1}. {data['label']}**")
            st.sidebar.write(f" von {u} nach {v}")
    except nx.NetworkXNoPath:
        st.sidebar.error("Keine Verbindung gefunden! (Vielleicht eine Piste bergauf gewählt?)")
        path = None
else:
    path = None

# --- KARTE RENDERN ---
# Simple CRS für statische Bilder
m = folium.Map(crs='Simple', bounds=IMAGE_BOUNDS, zoom_start=1)

# Pistenplan als Overlay
folium.RasterLayers.ImageOverlay(
    image=img_data,
    bounds=IMAGE_BOUNDS,
    opacity=1.0,
    interactive=True
).add_to(m)

# Route auf Karte zeichnen
if path:
    path_coords = [nodes[node] for node in path]
    folium.PolyLine(path_coords, color="red", weight=10, opacity=0.8).add_to(m)
    folium.Marker(nodes[start_point], popup="START", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(nodes[end_point], popup="ZIEL", icon=folium.Icon(color='red')).add_to(m)

# Karte in Streamlit anzeigen
st_folium(m, width=1100, height=750)
