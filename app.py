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
        "🏠 Gampe Thaya": (385, 892),
        "🏠 Gampe Alm": (366.0625, 912.5000),
        "🏠 Hühnersteign": (439, 777),
        "🏠 Hochsölden (Ort)": (350, 850),
        "🏠 Sonnblick": (340, 840),
        "🏠 s´Stabele Schirmbar": (385.5, 806.7500),
        
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
        "🏠 Rettenbach Market": (700, 480),

        # --- PISTEN-VERBINDUNGEN ---
    "⛷️ Piste 1 (Gaislachkogl Talfahrt)": (250, 350),
    "⛷️ Piste 11 (Giggijoch Verbindung)": (480, 700),
    "⛷️ Piste 13 (Giggijoch Talabfahrt)": (300, 800),
    "⛷️ Piste 30 (Gletscherverbindung)": (650, 450),
    "⛷️ Piste 38 (Tiefenbachferner)": (780, 300),
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

  # ERWEITERTE VERBINDUNGEN (LIFTE & PISTEN)
    edges = [
        # --- LIFTE (Weg nach oben) ---
        ("🚠 Gaislachkogl I (Tal)", "🚠 Gaislachkogl I (Mittel)"),
        ("🚠 Gaislachkogl I (Mittel)", "🚠 Gaislachkogl II (Gipfel)"),
        ("🚠 Giggijochbahn (Tal)", "🚠 Giggijochbahn (Berg)"),
        ("💺 Langegg (Zubringer)", "🚠 Gaislachkogl I (Mittel)"),
        ("💺 Einzeiger", "🚠 Gletscherexpress"),
        ("💺 Silberbrünnl", "💺 Rotkogl"),
        ("💺 Stabele", "🚠 Gaislachkogl I (Mittel)"),
        
        # --- DER NEUE GUIDE-WEG (Giggijoch / Hochsölden) ---
        ("🚠 Giggijochbahn (Berg)", "🏠 Hühnersteign"),
        ("🏠 Hühnersteign", "🏠 s´Stabele Schirmbar"),
        ("🏠 s´Stabele Schirmbar", "🏠 Gampe Alm"),
        ("🏠 Gampe Alm", "🏠 Gampe Thaya"),
        ("🏠 Gampe Thaya", "⛷️ Piste 13 (Giggijoch Talabfahrt)"),
        ("🏠 Hochsölden (Ort)", "🏠 Sonnblick"),
        ("🏠 Sonnblick", "🏠 Gampe Alm"), # Verbindungsweg von Hochsölden
        
        # --- GAISLACHKOGL HÜTTEN-WEGE ---
        ("🚠 Gaislachkogl II (Gipfel)", "🏠 ice Q"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Falcon Restaurant"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Annemaries Hütte"),
        ("🏠 Annemaries Hütte", "🏠 Bubis Schihütte"),
        ("🏠 Bubis Schihütte", "🏠 Gaislachalm"),
        ("🏠 Gaislachalm", "🏠 Löple Alm"),
        ("🏠 Löple Alm", "⛷️ Piste 1 (Gaislachkogl Talfahrt)"),
        
        # --- HAUPTPISTEN & VERBINDUNGEN ---
        ("🚠 Giggijochbahn (Berg)", "⛷️ Piste 11 (Giggijoch Verbindung)"),
        ("⛷️ Piste 11 (Giggijoch Verbindung)", "💺 Langegg (Zubringer)"),
        ("⛷️ Piste 13 (Giggijoch Talabfahrt)", "🚠 Giggijochbahn (Tal)"),
        ("🚠 Gaislachkogl I (Mittel)", "⛷️ Piste 1 (Gaislachkogl Talfahrt)"),
        ("⛷️ Piste 1 (Gaislachkogl Talfahrt)", "🚠 Gaislachkogl I (Tal)"),
        
        # --- GLETSCHER-NETZ ---
        ("🚠 Schwarze Schneid II", "⛷️ Piste 30 (Gletscherverbindung)"),
        ("⛷️ Piste 30 (Gletscherverbindung)", "💺 Einzeiger"),
        ("🚠 Tiefenbachbahn", "⛷️ Piste 38 (Tiefenbachferner)"),
        ("⛷️ Piste 38 (Tiefenbachferner)", "🏠 Gletschertisch")
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
    
# --- KARTE INITIALISIEREN ---
map_bounds = [[0, 0], [1000, 1400]]
m = folium.Map(crs='Simple', location=[500, 700], zoom_start=-0.5)

# Pistenplan Overlay
folium.raster_layers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=map_bounds
).add_to(m)

# Koordinaten-Klick-Helfer (LatLngPopup)
if show_coords:
    m.add_child(folium.LatLngPopup())
    
# --- PFEIL ANZEIGEN (SOFORT BEI AUSWAHL) ---
if start in nodes:
    start_coords = nodes[start]
    folium.map.Marker(
        start_coords,
        icon=folium.DivIcon(
            html=f"""<div style="font-size: 30pt; color: green; position: relative; top: -40px; text-align: center;">
                        <div style="animation: bounce 1s infinite;">⬇️</div>
                     </div>
                     <style>
                        @keyframes bounce {{
                            0%, 100% {{ transform: translateY(0); }}
                            50% {{ transform: translateY(-15px); }}
                        }}
                     </style>"""
        )
    ).add_to(m)

# --- AUTOMATISCHE ROUTEN-LOGIK (Kein Button mehr nötig) ---

# Wir berechnen die Route nur, wenn Start und Ziel nicht gleich sind
if start != ziel:
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        
        # 1. Die rote Linie und das Ziel direkt zur Karte 'm' hinzufügen
        folium.PolyLine(path_coords, color="red", weight=8, opacity=0.8).add_to(m)
        folium.Marker(
            location=path_coords[-1],
            icon=folium.Icon(color="red", icon="flag", prefix="fa"),
            popup=f"ZIEL: {ziel}"
        ).add_to(m)
        
        # 2. Den Guide-Text vorbereiten
        route_guide = " ➔ ".join(path)
        
    except nx.NetworkXNoPath:
        st.sidebar.warning("Keine direkte Pistenverbindung gefunden.")
        route_guide = ""
else:
    route_guide = ""
    # Wenn Start == Ziel, zeigen wir nur den Startpfeil (ist bereits oben im Code)

# --- ANZEIGE DER KARTE ---
# Wichtig: 'key' hilft Streamlit, die Karte beim Switchen der Ziele flüssig darzustellen
st_folium(m, width=1100, height=700, key="soelden_map_auto")

# --- ANZEIGE DES GUIDES UNTER DER KARTE ---
if route_guide:
    st.markdown("### 🗺️ Dein Live-Wegweiser")
    st.success(f"**Route:** {route_guide}")

# --- ANZEIGE DER KARTE ---
st_folium(m, width=1100, height=700, key="soelden_map")

# --- ANZEIGE DES GUIDES (Unter der Karte) ---
if route_guide:
    st.markdown("### 🗺️ Dein Weg zum Ziel")
    st.success(f"**Route:** {route_guide}")
