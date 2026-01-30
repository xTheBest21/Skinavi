import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
import base64
import requests
from io import BytesIO
from PIL import Image

# 1. SEITE KONFIGURIEREN
st.set_page_config(page_title="Ski Navi Sölden Pro", layout="wide")

# CSS: Entfernt Streamlit-Ränder für echte Vollbild-Nutzung am Monitor
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        iframe {
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

# BILD LADEN
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

# 2. DAS SKI-NETZWERK (Nodes & Edges)
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    nodes = {
        "⛷️ Piste 1 (Blau)": (250, 350), "⛷️ Piste 2 (Rot)": (500, 280),
        "⛷️ Piste 4 (Blau)": (450, 400), "⛷️ Piste 5 (Rot)": (480, 320),
        "⛷️ Piste 7 (Blau)": (480, 920), "⛷️ Piste 8 (Schwarz)": (460, 950),
        "⛷️ Piste 10 (Blau)": (520, 750), "⛷️ Piste 11 (Blau)": (460, 680),
        "⛷️ Piste 13 (Blau)": (430, 830), "⛷️ Piste 14 (Blau)": (510, 850),
        "⛷️ Piste 15 (Blau)": (550, 920), "⛷️ Piste 19 (Rot)": (380, 820),
        "⛷️ Piste 20 (Rot)": (150, 780), "⛷️ Piste 21 (Rot)": (540, 930),
        "⛷️ Piste 22 (Rot)": (530, 940), "⛷️ Piste 23 (Blau)": (400, 650),
        "⛷️ Piste 30 (Blau)": (630, 600), "⛷️ Piste 32 (Blau)": (750, 480),
        "⛷️ Piste 33 (Schwarz)": (720, 430), "⛷️ Piste 37 (Blau)": (760, 350),
        "⛷️ Piste 38 (Blau)": (780, 280),
        "🏠 Annemaries Hütte": (350, 380), "🏠 Bubis Schihütte": (320, 400),
        "🏠 Falcon Restaurant": (405, 330), "🏠 Gaislachalm": (300, 420),
        "🏠 Gampe Alm": (366, 912), "🏠 Gampe Thaya": (385, 892),
        "🏠 Gletschertisch": (710, 510), "🏠 Heidealm": (440, 430),
        "🏠 Hochsölden (Ort)": (350, 850), "🏠 Hühnersteign": (439, 777),
        "🏠 ice Q": (615, 290), "🏠 Löple Alm": (310, 430),
        "🏠 Rettenbach Market": (700, 480), "🏠 s´Stabele Schirmbar": (385, 806),
        "🏠 Sonnblick": (340, 840), "🏠 Wirtshaus Giggijoch": (515, 895),
        "🏠 Gaislachkogl-Alm": (290, 410), "🏠 Silbertaler Alm": (340, 450),
        "🏠 Eugen's Obstlerhütte": (370, 810), "🏠 Rotkogljochhütte": (625, 775),
        "🏠 Schwarzkoglhuette": (530, 650), "🏠 Bratkartoffel-Hütte": (410, 880),
        "🏠 Panorama Restaurant Tiefenbach": (745, 260), "🏠 Rettenbachalm": (580, 520),
        "🏠 Gampe Labe": (375, 900), "🏠 Haimbachalm": (460, 900),
        "🏠 Mittelstation-Wirt": (395, 320),
        "🚠 Gaislachkogl I (Tal)": (130, 360), "🚠 Gaislachkogl I (Mittel)": (400, 310),
        "🚠 Gaislachkogl II (Gipfel)": (610, 280), "🚠 Giggijochbahn (Tal)": (70, 750),
        "🚠 Giggijochbahn (Berg)": (510, 880), "🚠 Gletscherexpress": (650, 550),
        "🚠 Schwarze Schneid I": (720, 500), "🚠 Schwarze Schneid II": (850, 400),
        "🚠 Tiefenbachbahn": (750, 250), "💺 Einzeiger": (550, 620),
        "💺 Giggijoch Sessel": (520, 850), "💺 Hainbachkar": (530, 920),
        "💺 Heidebahn": (450, 420), "💺 Langegg (Zubringer)": (420, 600),
        "💺 Rosskirpl": (550, 980), "💺 Rotkogl": (620, 780),
        "💺 Seekogl": (500, 950), "💺 Seiterjöchl": (700, 350),
        "💺 Silberbrünnl": (580, 950), "💺 Stabele": (430, 450),
        "💺 Wasserkar": (480, 350),
    }
    for name, pos in nodes.items(): G.add_node(name, pos=pos)

    edges = [
        ("🚠 Gaislachkogl II (Gipfel)", "🏠 ice Q"), ("🏠 ice Q", "⛷️ Piste 2 (Rot)"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Falcon Restaurant"), ("🏠 Falcon Restaurant", "⛷️ Piste 5 (Rot)"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Mittelstation-Wirt"), ("🏠 Mittelstation-Wirt", "⛷️ Piste 1 (Blau)"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Annemaries Hütte"), ("🏠 Annemaries Hütte", "🏠 Bubis Schihütte"),
        ("🏠 Bubis Schihütte", "⛷️ Piste 1 (Blau)"), ("⛷️ Piste 1 (Blau)", "🏠 Silbertaler Alm"),
        ("🏠 Silbertaler Alm", "🚠 Gaislachkogl I (Tal)"), ("💺 Stabele", "🏠 Gaislachalm"),
        ("🏠 Gaislachalm", "🏠 Löple Alm"), ("🏠 Löple Alm", "⛷️ Piste 1 (Blau)"),
        ("💺 Heidebahn", "🏠 Heidealm"), ("🏠 Heidealm", "⛷️ Piste 4 (Blau)"),
        ("🚠 Giggijochbahn (Berg)", "🏠 Wirtshaus Giggijoch"), ("🏠 Wirtshaus Giggijoch", "⛷️ Piste 13 (Blau)"),
        ("⛷️ Piste 13 (Blau)", "🏠 Hühnersteign"), ("🏠 Hühnersteign", "🏠 s´Stabele Schirmbar"),
        ("🏠 s´Stabele Schirmbar", "🏠 Gampe Alm"), ("🏠 Gampe Thaya", "🏠 Haimbachalm"),
        ("🏠 Haimbachalm", "⛷️ Piste 20 (Rot)"), ("⛷️ Piste 13 (Blau)", "⛷️ Piste 19 (Rot)"),
        ("⛷️ Piste 19 (Rot)", "🏠 Eugen's Obstlerhütte"), ("🏠 Eugen's Obstlerhütte", "🏠 Hochsölden (Ort)"),
        ("🏠 Hochsölden (Ort)", "🏠 Sonnblick"), ("🏠 Sonnblick", "⛷️ Piste 20 (Rot)"),
        ("💺 Silberbrünnl", "🏠 Bratkartoffel-Hütte"), ("🏠 Bratkartoffel-Hütte", "🚠 Giggijochbahn (Berg)"),
        ("💺 Rotkogl", "🏠 Rotkogljochhütte"), ("🏠 Rotkogljochhütte", "⛷️ Piste 30 (Blau)"),
        ("⛷️ Piste 11 (Blau)", "🏠 Schwarzkoglhuette"), ("🏠 Schwarzkoglhuette", "💺 Langegg (Zubringer)"),
        ("⛷️ Piste 30 (Blau)", "🏠 Rettenbachalm"), ("🏠 Rettenbachalm", "🚠 Gletscherexpress"),
        ("🚠 Gletscherexpress", "🏠 Rettenbach Market"), ("🏠 Rettenbach Market", "⛷️ Piste 32 (Blau)"),
        ("⛷️ Piste 32 (Blau)", "🏠 Gletschertisch"), ("🚠 Tiefenbachbahn", "🏠 Panorama Restaurant Tiefenbach"),
        ("🏠 Panorama Restaurant Tiefenbach", "⛷️ Piste 38 (Blau)"), ("🚠 Gaislachkogl I (Tal)", "🚠 Gaislachkogl I (Mittel)"),
        ("🚠 Gaislachkogl I (Mittel)", "🚠 Gaislachkogl II (Gipfel)"), ("🚠 Giggijochbahn (Tal)", "🚠 Giggijochbahn (Berg)"),
        ("💺 Langegg (Zubringer)", "🚠 Gaislachkogl I (Mittel)"), ("💺 Einzeiger", "🚠 Gletscherexpress")
    ]
    G.add_edges_from(edges)
    return G, nodes

G, nodes = build_soelden_graph()

# 3. UI SIDEBAR
st.sidebar.title("🔍 Navigation & Filter")
kategorie_start = st.sidebar.radio("Start-Kategorie:", ["Alle", "⛷️ Pisten", "🏠 Hütten", "🚠 Lifte"])
kategorie_ziel = st.sidebar.radio("Ziel-Kategorie:", ["Alle", "⛷️ Pisten", "🏠 Hütten", "🚠 Lifte"])

def filter_nodes(kategorie):
    if kategorie == "⛷️ Pisten": return [n for n in nodes.keys() if "⛷️" in n]
    elif kategorie == "🏠 Hütten": return [n for n in nodes.keys() if "🏠" in n]
    elif kategorie == "🚠 Lifte": return [n for n in nodes.keys() if "🚠" in n or "💺" in n]
    return sorted(nodes.keys())

start = st.sidebar.radio("Dein Standort", filter_nodes(kategorie_start))
ziel = st.sidebar.radio("Wohin willst du?", filter_nodes(kategorie_ziel))
show_coords = st.sidebar.checkbox("Koordinaten-Helfer")

# 4. KARTEN-LOGIK (Zentriert & Fixiert)
img_height, img_width = 3504, 4958
map_bounds = [[0, 0], [img_height, img_width]]

m = folium.Map(
    crs='Simple',
    location=[img_height / 2, img_width / 2],
    zoom_start=-2,
    min_zoom=-4,
    max_zoom=1,
    tiles=None,
    max_bounds=True
)

folium.raster_layers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=map_bounds,
    zindex=1
).add_to(m)

# 5. MARKER & ROUTE
if start in nodes:
    folium.map.Marker(
        nodes[start],
        icon=folium.DivIcon(html=f"""<div style="font-size: 30pt; color: green; text-align: center;">⬇️</div>""")
    ).add_to(m)

route_guide = ""
if start != ziel:
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        folium.PolyLine(path_coords, color="red", weight=8, opacity=0.8).add_to(m)
        folium.Marker(location=path_coords[-1], icon=folium.Icon(color="red", icon="flag")).add_to(m)
        route_guide = " ➔ ".join(path)
    except:
        st.sidebar.warning("Keine Verbindung gefunden.")

if show_coords:
    m.add_child(folium.LatLngPopup())

# 6. ANZEIGE
st.title("⛷️ Sölden Ski-Navi")
output = st_folium(
    m, 
    width=None, 
    height=800, # Höhe für Monitor optimiert
    use_container_width=True,
    key="soelden_map"
)

if route_guide:
    st.info(f"**Route:** {route_guide}")

if show_coords and output and output.get("last_clicked"):
    st.write(f"Koordinaten: `{output['last_clicked']['lat']:.0f}, {clicked['lng']:.0f}`")
