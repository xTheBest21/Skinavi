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
            img.save(buffered, format="JPG")
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
        # --- KATEGORIE 1: PISTEN (1 - 38) ---
        "⛷️ Piste 1 (Blau)": (250, 350),
        "⛷️ Piste 2 (Rot)": (500, 280),
        "⛷️ Piste 4 (Blau)": (450, 400),
        "⛷️ Piste 5 (Rot)": (480, 320),
        "⛷️ Piste 7 (Blau)": (480, 920),
        "⛷️ Piste 8 (Schwarz)": (460, 950),
        "⛷️ Piste 10 (Blau)": (520, 750),
        "⛷️ Piste 11 (Blau)": (460, 680),
        "⛷️ Piste 13 (Blau)": (430, 830),
        "⛷️ Piste 14 (Blau)": (510, 850),
        "⛷️ Piste 15 (Blau)": (550, 920),
        "⛷️ Piste 19 (Rot)": (380, 820),
        "⛷️ Piste 20 (Rot)": (150, 780),
        "⛷️ Piste 21 (Rot)": (540, 930),
        "⛷️ Piste 22 (Rot)": (530, 940),
        "⛷️ Piste 23 (Blau)": (400, 650),
        "⛷️ Piste 30 (Blau)": (630, 600),
        "⛷️ Piste 32 (Blau)": (750, 480),
        "⛷️ Piste 33 (Schwarz)": (720, 430),
        "⛷️ Piste 37 (Blau)": (760, 350),
        "⛷️ Piste 38 (Blau)": (780, 280),

        # --- KATEGORIE 2: HÜTTEN & RESTAURANTS ---
        "🏠 Annemaries Hütte": (350, 380),
        "🏠 Bubis Schihütte": (320, 400),
        "🏠 Falcon Restaurant": (405, 330),
        "🏠 Gaislachalm": (300, 420),
        "🏠 Gampe Alm": (366, 912),
        "🏠 Gampe Thaya": (385, 892),
        "🏠 Gletschertisch": (710, 510),
        "🏠 Heidealm": (440, 430),
        "🏠 Hochsölden (Ort)": (350, 850),
        "🏠 Hühnersteign": (439, 777),
        "🏠 ice Q": (615, 290),
        "🏠 Löple Alm": (310, 430),
        "🏠 Rettenbach Market": (700, 480),
        "🏠 s´Stabele Schirmbar": (385, 806),
        "🏠 Sonnblick": (340, 840),
        "🏠 Wirtshaus Giggijoch": (515, 895),
        "🏠 Gaislachkogl-Alm": (290, 410),
        "🏠 Silbertaler Alm": (340, 450),
        "🏠 Eugen's Obstlerhütte": (370, 810),
        "🏠 Rotkogljochhütte": (625, 775),
        "🏠 Schwarzkoglhuette": (530, 650),
        "🏠 Bratkartoffel-Hütte": (410, 880),
        "🏠 Panorama Restaurant Tiefenbach": (745, 260),
        "🏠 Rettenbachalm": (580, 520),
        "🏠 Gampe Labe": (375, 900),
        "🏠 Haimbachalm": (460, 900),
        "🏠 Mittelstation-Wirt": (395, 320),

        # --- KATEGORIE 3: LIFTE & BAHNEN ---
        "🚠 Gaislachkogl I (Tal)": (130, 360),
        "🚠 Gaislachkogl I (Mittel)": (400, 310),
        "🚠 Gaislachkogl II (Gipfel)": (610, 280),
        "🚠 Giggijochbahn (Tal)": (70, 750),
        "🚠 Giggijochbahn (Berg)": (510, 880),
        "🚠 Gletscherexpress": (650, 550),
        "🚠 Schwarze Schneid I": (720, 500),
        "🚠 Schwarze Schneid II": (850, 400),
        "🚠 Tiefenbachbahn": (750, 250),
        "💺 Einzeiger": (550, 620),
        "💺 Giggijoch Sessel": (520, 850),
        "💺 Hainbachkar": (530, 920),
        "💺 Heidebahn": (450, 420),
        "💺 Langegg (Zubringer)": (420, 600),
        "💺 Rosskirpl": (550, 980),
        "💺 Rotkogl": (620, 780),
        "💺 Seekogl": (500, 950),
        "💺 Seiterjöchl": (700, 350),
        "💺 Silberbrünnl": (580, 950),
        "💺 Stabele": (430, 450),
        "💺 Wasserkar": (480, 350),
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

  # ERWEITERTE VERBINDUNGEN (LIFTE & PISTEN)
    # ERWEITERTE VERBINDUNGEN (Die Pisten-Logik)
    edges = [
        # --- SEKTOR GAISLACHKOGL ---
        ("🚠 Gaislachkogl II (Gipfel)", "🏠 ice Q"),
        ("🏠 ice Q", "⛷️ Piste 2 (Rot)"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Falcon Restaurant"),
        ("🏠 Falcon Restaurant", "⛷️ Piste 5 (Rot)"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Mittelstation-Wirt"),
        ("🏠 Mittelstation-Wirt", "⛷️ Piste 1 (Blau)"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Annemaries Hütte"),
        ("🏠 Annemaries Hütte", "🏠 Bubis Schihütte"),
        ("🏠 Bubis Schihütte", "⛷️ Piste 1 (Blau)"),
        ("⛷️ Piste 1 (Blau)", "🏠 Silbertaler Alm"),
        ("🏠 Silbertaler Alm", "🚠 Gaislachkogl I (Tal)"),
        ("💺 Stabele", "🏠 Gaislachalm"),
        ("🏠 Gaislachalm", "🏠 Löple Alm"),
        ("🏠 Löple Alm", "⛷️ Piste 1 (Blau)"),
        ("💺 Heidebahn", "🏠 Heidealm"),
        ("🏠 Heidealm", "⛷️ Piste 4 (Blau)"),

        # --- SEKTOR GIGGIJOCH / HOCHSÖLDEN ---
        ("🚠 Giggijochbahn (Berg)", "🏠 Wirtshaus Giggijoch"),
        ("🏠 Wirtshaus Giggijoch", "⛷️ Piste 13 (Blau)"),
        ("⛷️ Piste 13 (Blau)", "🏠 Hühnersteign"),
        ("🏠 Hühnersteign", "🏠 s´Stabele Schirmbar"),
        ("🏠 s´Stabele Schirmbar", "🏠 Gampe Alm"),
        ("🏠 Gampe Thaya", "🏠 Haimbachalm"),
        ("🏠 Haimbachalm", "⛷️ Piste 20 (Rot)"),
        ("⛷️ Piste 13 (Blau)", "⛷️ Piste 19 (Rot)"),
        ("⛷️ Piste 19 (Rot)", "🏠 Eugen's Obstlerhütte"),
        ("🏠 Eugen's Obstlerhütte", "🏠 Hochsölden (Ort)"),
        ("🏠 Hochsölden (Ort)", "🏠 Sonnblick"),
        ("🏠 Sonnblick", "⛷️ Piste 20 (Rot)"),
        ("💺 Silberbrünnl", "🏠 Bratkartoffel-Hütte"),
        ("🏠 Bratkartoffel-Hütte", "🚠 Giggijochbahn (Berg)"),

        # --- SEKTOR GOLDEN GATE & GLETSCHER ---
        ("💺 Rotkogl", "🏠 Rotkogljochhütte"),
        ("🏠 Rotkogljochhütte", "⛷️ Piste 30 (Blau)"),
        ("⛷️ Piste 11 (Blau)", "🏠 Schwarzkoglhuette"),
        ("🏠 Schwarzkoglhuette", "💺 Langegg (Zubringer)"),
        ("⛷️ Piste 30 (Blau)", "🏠 Rettenbachalm"),
        ("🏠 Rettenbachalm", "🚠 Gletscherexpress"),
        ("🚠 Gletscherexpress", "🏠 Rettenbach Market"),
        ("🏠 Rettenbach Market", "⛷️ Piste 32 (Blau)"),
        ("⛷️ Piste 32 (Blau)", "🏠 Gletschertisch"),
        ("🚠 Tiefenbachbahn", "🏠 Panorama Restaurant Tiefenbach"),
        ("🏠 Panorama Restaurant Tiefenbach", "⛷️ Piste 38 (Blau)"),

        # --- ZUSÄTZLICHE LIFT-VERBINDUNGEN ---
        ("🚠 Gaislachkogl I (Tal)", "🚠 Gaislachkogl I (Mittel)"),
        ("🚠 Gaislachkogl I (Mittel)", "🚠 Gaislachkogl II (Gipfel)"),
        ("🚠 Giggijochbahn (Tal)", "🚠 Giggijochbahn (Berg)"),
        ("💺 Langegg (Zubringer)", "🚠 Gaislachkogl I (Mittel)"),
        ("💺 Einzeiger", "🚠 Gletscherexpress")
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
# --- FILTER-LOGIK ---
st.sidebar.title("🔍 Filter & Auswahl")

# 1. Auswahl des Typs für Start und Ziel
kategorie_start = st.sidebar.radio("Start-Kategorie:", ["Alle", "⛷️ Pisten", "🏠 Hütten", "🚠 Lifte"])
kategorie_ziel = st.sidebar.radio("Ziel-Kategorie:", ["Alle", "⛷️ Pisten", "🏠 Hütten", "🚠 Lifte"])

# Hilfsfunktion zum Filtern der Liste
def filter_nodes(kategorie):
    if kategorie == "⛷️ Pisten":
        return [n for n in nodes.keys() if "⛷️" in n]
    elif kategorie == "🏠 Hütten":
        return [n for n in nodes.keys() if "🏠" in n]
    elif kategorie == "🚠 Lifte":
        return [n for n in nodes.keys() if "🚠" in n or "💺" in n]
    return sorted(nodes.keys())

# 2. Dynamische Dropdowns
start_liste = filter_nodes(kategorie_start)
ziel_liste = filter_nodes(kategorie_ziel)

start = st.sidebar.radio("Dein Standort", start_liste)
ziel = st.sidebar.radio("Wohin willst du?", ziel_liste)

show_coords = st.sidebar.checkbox("Koordinaten-Helfer (für neue Punkte)")
    
# 1. Wir definieren die Grenzen etwas weiter, damit das Handy nicht "blockiert"
map_bounds = [[0, 0], [3504, 4958]]

# 2. Die Karte mit mobilem Fokus erstellen
m = folium.Map(
    crs='Simple', 
    location=[500, 700], 
    zoom_start=0.01,  # Etwas näher starten für Handys
    tiles=None,
    # Wir erlauben dem User etwas mehr Platz zum Bewegen
    max_bounds=True,
    min_lat=-100, 
    max_lat=1100,
    min_lon=-100, 
    max_lon=1500, # Mehr Platz nach rechts!
    zoom_control=True
)

# 3. Das Bild hinzufügen
folium.raster_layers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=map_bounds,
    zindex=1,
    interactive=True # Wichtig für Touch
).add_to(m)

# 1. Definieren der Bildgröße (Pixel deines JPEGs)
# Wenn dein Bild z.B. 1400x1000 Pixel hat:
img_height = 3504
img_width = 4958
map_bounds = [[0, 0], [img_height, img_width]]

# 2. Die Karte erstellen
m = folium.Map(
    crs='Simple', 
    location=[img_height / 2, img_width / 2], # Startet in der Mitte des Bildes
    zoom_start=-0.01,
    min_zomm=10,
    max_zoom= 1,
    tiles=None,
    # HIER kommen die Bounds als Begrenzung rein:
    max_bounds=True,
    min_lat=0,
    max_lat=img_height,
    min_lon=0,
    max_lon=img_width
)

# 3. Das Bild auf genau diese Bounds legen
folium.raster_layers.ImageOverlay(
    image=f"data:image/jpg;base64,{img_data}",
    bounds=map_bounds,  # HIER wird das Bild "festgeklebt"
    zindex=1
).add_to(m)

# 4. Der ultimative CSS-Fix gegen das Schwarzwerden (speziell für Mobile)
m.get_root().header.add_child(folium.Element("""
    <style>
        .folium-map { 
            background-color: white !important; 
        }
        /* Verhindert graue Ränder auf dem iPhone/Android */
        .leaflet-container {
            background: #ffffff !important;
            outline: 0;
        }
    </style>
"""))

# Das Bild fest auf die Karte legen
folium.raster_layers.ImageOverlay(
    image=f"data:image/jpeg;base64,{img_data}",
    bounds=map_bounds,
    zindex=1
).add_to(m)

# --- TRICK: Hintergrundfarbe per CSS erzwingen ---
# Das verhindert das Schwarzwerden beim Zoomen
m.get_root().header.add_child(folium.Element("""
    <style>
        .folium-map { background-color: #ffffff !important; }
    </style>
"""))
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

# --- AUTOMATISCHE ROUTEN-LOGIK ---
route_guide = ""

if start != ziel:
    try:
        path = nx.shortest_path(G, source=start, target=ziel)
        path_coords = [nodes[node] for node in path]
        
        # 1. Die rote Linie und das Ziel zur Karte hinzufügen
        folium.PolyLine(path_coords, color="red", weight=8, opacity=0.8).add_to(m)
        folium.Marker(
            location=path_coords[-1],
            icon=folium.Icon(color="red", icon="flag", prefix="fa"),
            popup=f"ZIEL: {ziel}"
        ).add_to(m)
        
        # 2. Den Guide-Text intelligent zusammenbauen
        guide_schritte = []
        for i, station in enumerate(path):
            if i == 0:
                guide_schritte.append(f"🏁 **Start:** {station}")
            elif i == len(path) - 1:
                guide_schritte.append(f"🎯 **Ziel:** {station}")
            elif "⛷️" in station:
                guide_schritte.append(f"Abfahrt {station}")
            elif "🚠" in station or "💺" in station:
                guide_schritte.append(f"Lift {station}")
            else:
                guide_schritte.append(station)
        
        route_guide = " ➔ ".join(guide_schritte)
        
    except nx.NetworkXNoPath:
        st.sidebar.warning("Keine direkte Pistenverbindung gefunden. Wir arbeiten an weiteren Pisten!")
        route_guide = ""

# --- ANZEIGE DER KARTE (Nur einmal aufrufen!) ---
st_folium(
    m, 
    width=None, # None lässt es die volle Breite des Handys nutzen
    height=500, # Auf dem Handy ist 500px meist besser als 700px
    key="soelden_mobile_final",
    use_container_width=True
)

# --- ANZEIGE DES GUIDES (Unter der Karte) ---
if route_guide:
    st.markdown("### 🗺️ Dein persönlicher Ski-Guide")
    # Benutze info für eine schicke blaue Box oder success für grün
    st.info(route_guide)
