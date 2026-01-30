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

# CSS für maximale Monitor-Ausnutzung
st.markdown("""
    <style>
        .block-container {
            padding: 1rem 1rem 0rem 1rem !important;
            max-width: 100% !important;
        }
        iframe {
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

IMAGE_URL = "https://raw.githubusercontent.com/xTheBest21/Skinavi/main/soelden_pistenplan.jpg"

@st.cache_resource
def get_image_base64(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img = img.convert("RGB")
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except: return None

img_data = get_image_base64(IMAGE_URL)

@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    # Beispiel-Nodes (müssen mit Koordinaten-Helfer neu kalibriert werden!)
    nodes = {
        "⛷️ Piste 1 (Blau)": (1500, 2000), 
        "🏠 ice Q": (2800, 1500),
        "🚠 Gaislachkogl II (Gipfel)": (2850, 1450)
    }
    for name, pos in nodes.items(): G.add_node(name, pos=pos)
    # Hier fehlen deine restlichen Nodes/Edges aus dem vorigen Code...
    return G, nodes

G, nodes = build_soelden_graph()

# --- UI Sidebar ---
st.sidebar.title("🔍 Navigation")
start = st.sidebar.selectbox("Dein Standort", sorted(nodes.keys()))
ziel = st.sidebar.selectbox("Wohin willst du?", sorted(nodes.keys()))
show_coords = st.sidebar.checkbox("Koordinaten-Helfer")

# --- KARTEN-LOGIK (DIE FIXIERUNG) ---
img_height, img_width = 3504, 4958
# Wir definieren die Grenzen exakt: [[unten, links], [oben, rechts]]
map_bounds = [[0, 0], [img_height, img_width]]

m = folium.Map(
    crs='Simple',
    location=[img_height / 2, img_width / 2], # Kamera auf Bildmitte
    zoom_start=-2,
    min_zoom=-4,
    max_zoom=1,
    tiles=None,
    max_bounds=True
)

# Das Bild genau in die Bounds legen
folium.raster_layers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=map_bounds,
    zindex=1
).add_to(m)

# WICHTIG: Die Karte zwingen, diese Bounds als Welt anzuzeigen
m.fit_bounds(map_bounds)

# Marker setzen
if start in nodes:
    folium.Marker(
        location=nodes[start],
        popup="Dein Standort",
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)

if show_coords:
    m.add_child(folium.LatLngPopup())

# --- FINALE ANZEIGE ---
# height=850 sorgt dafür, dass das Bild auf dem Monitor schön groß wird
output = st_folium(
    m, 
    width=None, 
    height=850, 
    use_container_width=True,
    key="soelden_fixed"
)

if show_coords and output and output.get("last_clicked"):
    st.write(f"Koordinaten für Code: `{output['last_clicked']['lat']:.0f}, {output['last_clicked']['lng']:.0f}`")
