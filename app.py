import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
import base64
import requests
from io import BytesIO
from PIL import Image

# 1. Seite konfigurieren
st.set_page_config(page_title="Ski Navi Sölden Pro", layout="wide")

# Bild-URL (Pistenplan)
IMAGE_URL = "https://raw.githubusercontent.com/xTheBest21/Skinavi/main/soelden_pistenplan.jpg"

@st.cache_resource
def get_image_base64(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if img.mode != "RGB":
                img = img.convert("RGB")
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        return None

img_data = get_image_base64(IMAGE_URL)

# 2. Das Ski-Netzwerk (Hütten & Lifte)
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    
    # KNOTEN: Name : (Y, X)
    nodes = {
        # --- SEKTOR GAISLACHKOGL ---
        "🚠 Gaislachkogl I (Tal)": (130, 360),
        "🚠 Gaislachkogl I (Mittel)": (400, 310),
        "🚠 Gaislachkogl II (Gipfel)": (610, 280),
        "💺 Heidebahn": (450, 420),
        "💺 Wasserkar": (480, 350),
        "💺 Stabele": (430, 450),
        "🏠 Falcon Restaurant": (405, 330),
        "🏠 ice Q": (615, 290),
        "🏠 Bubis Schihütte": (320, 400),
        "🏠 Annemaries Hütte": (350, 380),
        "🏠 Gaislachalm": (300, 420),
        "🏠 Löple Alm": (310, 430),
        "🏠 Heidealm": (440, 430),

        # --- SEKTOR GIGGIJOCH / HOCHSÖLDEN ---
        "🚠 Giggijochbahn (Tal)": (70, 750),
        "🚠 Giggijochbahn (Berg)": (510, 880),
        "💺 Silberbrünnl": (580, 950),
        "💺 Rosskirpl": (550, 980),
        "💺 Hainbachkar": (530, 920),
        "💺 Seekogl": (500, 950),
        "💺 Rotkogl": (620, 780),
        "💺 Giggijoch Sessel": (520, 850),
        "🏠 Wirtshaus Giggijoch": (515, 895),
        "🏠 Gampe Thaya": (400, 750),
        "🏠 Gampe Lamm": (390, 740),
        "🏠 Hühnersteign": (450, 820),
        "🏠 Hochsölden (Ort)": (350, 850),
        "🏠 Sonnblick": (340, 840),

        # --- VERBINDUNG GOLDEN GATE ---
        "💺 Langegg (Zubringer)": (420, 600),
        "💺 Einzeiger": (550, 620),
        "🚠 Gletscherexpress": (650, 550),

        # --- GLETSCHER ---
        "🚠 Schwarze Schneid I": (720, 500),
        "🚠 Schwarze Schneid II": (850, 400),
        "🚠 Tiefenbachbahn": (750, 250),
        "💺 Seiterjöchl": (700, 350),
        "🏠 Gletschertisch": (710, 510),
        "🏠 Rettenbach Market": (700, 480)
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

   # ERWEITERTE VERBINDUNGEN (LIFTE & PISTEN)
    edges = [
        # LIFTE (Hoch)
        ("🚠 Gaislachkogl I (Tal)", "🚠 Gaislachkogl I (Mittel)"),
        ("🚠 Gaislachkogl I (Mittel)", "🚠 Gaislachkogl II (Gipfel)"),
        ("🚠 Giggijochbahn (Tal)", "🚠 Giggijochbahn (Berg)"),
        ("💺 Langegg (Zubringer)", "🚠 Gaislachkogl I (Mittel)"),
        ("💺 Einzeiger", "🚠 Gletscherexpress"),
        ("💺 Silberbrünnl", "💺 Rotkogl"),
        ("💺 Stabele", "🚠 Gaislachkogl I (Mittel)"),
        
        # PISTEN & HÜTTEN-ZUSTIEGE (Runter)
        ("🚠 Gaislachkogl II (Gipfel)", "🏠 ice Q"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Falcon Restaurant"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Annemaries Hütte"),
        ("🏠 Annemaries Hütte", "🏠 Bubis Schihütte"),
        ("🏠 Bubis Schihütte", "🏠 Gaislachalm"),
        ("🚠 Giggijochbahn (Berg)", "🏠 Hühnersteign"),
        ("🏠 Hühnersteign", "🏠 Hochsölden (Ort)"),
        ("🏠 Hochsölden (Ort)", "🏠 Gampe Thaya"),
        ("🏠 Gampe Thaya", "🚠 Giggijochbahn (Tal)"), # Talabfahrt
        ("💺 Rotkogl", "💺 Langegg (Zubringer)") # Verbindungsweg
    ]
    
    for u, v in edges:
        G.add_edge(u, v)
        
    return G, nodes

# --- WICHTIG: DATEN ERST ERSTELLEN ---
G, nodes = build_soelden_graph()

# --- UI ---
st.title("⛷️ Sölden Ski-Navi: Hütten & Lifte")

if img_data is None:
    st.error("Bild konnte nicht geladen werden.")
    st.stop()

# Sidebar Auswahl
start = st.sidebar.selectbox("Dein Standort", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Wohin willst du?", sorted(nodes.keys()))
show_coords = st.sidebar.checkbox("Koordinaten-Helfer (für neue Punkte)")

# Karte initialisieren
map_bounds = [[0, 0], [1000, 1400]]
m = folium.Map(crs='Simple', location=[500, 700], zoom_start=-0.5)

# Pistenplan Overlay
folium.raster_layers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=map_bounds
).add_to(m)

# Koordinaten-Klick-Helfer
if show_coords:
    m.add_child(folium.LatLngPopup())

# Route berechnen
if st.sidebar.button("Route berechnen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        
        # Linie zeichnen
        folium.PolyLine(path_coords, color="red", weight=7, opacity=0.8).add_to(m)
        
        # Start & Ziel Marker
        folium.CircleMarker(path_coords[0], radius=10, color="green", fill=True).add_to(m)
        folium.CircleMarker(path_coords[-1], radius=10, color="blue", fill=True).add_to(m)
        
        st.success(f"Weg: {' ➔ '.join(path)}")
    except:
        st.error("Keine direkte Skiverbindung gefunden!")

# Anzeige
st_folium(m, width=1100, height=700)
