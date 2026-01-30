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

# Bild-URL
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
        return f"Fehler: {str(e)}"
    return None

img_data = get_image_base64(IMAGE_URL)

# 2. Das Ski-Netzwerk
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    
    # Namen jetzt mit Emojis für die Sidebar
    nodes = {
        # --- GAISLACHKOGL SEKTOR ---
        "🚠 Gaislachkogl I (Tal)": (130, 360),
        "🚠 Gaislachkogl I (Mittel)": (400, 310),
        "🚠 Gaislachkogl II (Gipfel)": (610, 280),
        "💺 Heidebahn": (450, 420),
        "💺 Wasserkar": (480, 350),
        "💺 Stabele": (430, 450),
        "🏠 Falcon Restaurant": (405, 330),
        "🏠 ice Q (Gipfel)": (615, 290),
        "🏠 Bubis Schihütte": (320, 400),
        "🏠 Annemaries Hütte": (350, 380),
        "🏠 Gaislachalm": (300, 420),
        "🏠 Löple Alm": (310, 430),

        # --- GIGGIJOCH SEKTOR ---
        "🚠 Giggijochbahn (Tal)": (70, 750),
        "🚠 Giggijochbahn (Berg)": (510, 880),
        "💺 Silberbrünnl": (580, 950),
        "💺 Rosskirpl": (550, 980),
        "💺 Hainbachkar": (530, 920),
        "💺 Seekogl": (500, 950),
        "💺 Rotkogl": (620, 780),
        "🏠 Wirtshaus Giggijoch": (515, 895),
        "🏠 Panorama Alm": (480, 850),
        "🏠 Hühnersteign": (450, 820),
        "🏠 Gampe Thaya": (400, 750),
        "🏠 Eugen's Obstlerhütte": (150, 740),

        # --- VERBINDUNG & GLETSCHER ---
        "💺 Langegg (Zubringer)": (420, 600),
        "💺 Einzeiger": (550, 620),
        "🚠 Gletscherexpress": (650, 550),
        "🚠 Schwarze Schneid I": (720, 500),
        "🚠 Schwarze Schneid II": (850, 400),
        "🚠 Tiefenbachbahn": (750, 250),
        "🏠 Gletschertisch": (710, 510),
        "🏠 Rettenbach Market": (700, 480),
        "❄️ Schwarze Schneid (Gipfel)": (900, 400),
        "❄️ Tiefenbachferner": (760, 240)
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

    # WICHTIG: Die Verbindungen müssen exakt die gleichen Namen 
    # inklusive der Emojis nutzen!
  lifte = [
        # Gaislachkogl
        ("🚠 Gaislachkogl I (Tal)", "🚠 Gaislachkogl I (Mittel)"),
        ("🚠 Gaislachkogl I (Mittel)", "🚠 Gaislachkogl II (Gipfel)"),
        ("💺 Heidebahn", "🚠 Gaislachkogl I (Mittel)"),
        # Giggijoch
        ("🚠 Giggijochbahn (Tal)", "🚠 Giggijochbahn (Berg)"),
        ("💺 Silberbrünnl", "💺 Rotkogl"),
        # Verbindung
        ("💺 Langegg (Zubringer)", "🚠 Gaislachkogl I (Mittel)"),
        ("💺 Einzeiger", "🚠 Gletscherexpress")
    ]
    
    pisten = [
        # Von der Hütte zur Bahn oder ins Tal
        ("🏠 Falcon Restaurant", "🚠 Gaislachkogl I (Mittel)"),
        ("🏠 ice Q (Gipfel)", "🚠 Gaislachkogl II (Gipfel)"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Bubis Schihütte"),
        ("🏠 Bubis Schihütte", "🏠 Gaislachalm"),
        ("🏠 Gaislachalm", "🚠 Gaislachkogl I (Tal)"),
        # Giggijoch Abfahrten
        ("🚠 Giggijochbahn (Berg)", "🏠 Hühnersteign"),
        ("🏠 Hühnersteign", "🏠 Gampe Thaya"),
        ("🏠 Gampe Thaya", "🚠 Giggijochbahn (Tal)")
    ]
    
    for u, v in lifte + pisten:
        G.add_edge(u, v)
        
    return G, nodes

# --- DATEN LADEN ---
# Dies muss vor dem UI stehen!
G, nodes = build_soelden_graph()

# --- UI ---
st.title("⛷️ Ski Navi Sölden")

if img_data is None or "Fehler" in str(img_data):
    st.error(f"⚠️ Bild konnte nicht geladen werden: {img_data}")
    st.stop()

# Sidebar
start = st.sidebar.selectbox("Start", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Ziel", sorted(nodes.keys()))
show_coords = st.sidebar.checkbox("Koordinaten-Helfer anzeigen")

# --- KARTE ---
map_bounds = [[0, 0], [1000, 1400]]

m = folium.Map(
    crs='Simple',
    location=[500, 700],
    zoom_start=-0.5,
    min_zoom=-2,
    max_zoom=3
)

folium.raster_layers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=map_bounds,
    opacity=1.0,
    interactive=True
).add_to(m)

m.options['maxBounds'] = map_bounds

# Helfer-Tool
if show_coords:
    m.add_child(folium.LatLngPopup())

# --- ROUTE BERECHNEN ---
if st.sidebar.button("Route berechnen"):
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        
        # Route zeichnen
        folium.PolyLine(path_coords, color="red", weight=8, opacity=0.8, popup="Deine Route").add_to(m)
        
        # Marker
        folium.CircleMarker(path_coords[0], radius=8, color="green", fill=True, popup=f"START: {start}").add_to(m)
        folium.CircleMarker(path_coords[-1], radius=8, color="blue", fill=True, popup=f"ZIEL: {ziel}").add_to(m)
        
        st.success(f"Route: {' ➔ '.join(path)}")
    except nx.NetworkXNoPath:
        st.error("Keine Verbindung gefunden!")
    except Exception as e:
        st.error(f"Fehler: {e}")

# --- ANZEIGE ---
st_folium(m, width=1000, height=700, key="main_map")
