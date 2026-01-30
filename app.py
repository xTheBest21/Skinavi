import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
import base64
import requests
from io import BytesIO
from PIL import Image

# 1. Seite konfigurieren - "wide" ist die Basis für volle Breite
st.set_page_config(page_title="Ski Navi Sölden Pro", layout="wide")

# CSS: Entfernt die Standard-Abstände von Streamlit für maximale Monitor-Ausnutzung
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100% !important;
        }
        iframe {
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

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

@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    # KNOTEN: Name : (Y, X)
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
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)
    
    edges = [
        ("🚠 Gaislachkogl II (Gipfel)", "🏠 ice Q"), ("🏠 ice Q", "⛷️ Piste 2 (Rot)"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Falcon Restaurant"), ("🏠 Falcon Restaurant", "⛷️ Piste 5 (Rot)"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Mittelstation-Wirt"), ("🏠 Mittelstation-Wirt", "⛷️ Piste 1 (Blau)"),
        ("🚠 Gaislachkogl I (Mittel)", "🏠 Annemaries Hütte"), ("🏠 Annemaries Hütte", "🏠 Bubis Schihütte"),
        ("🏠 Bubis Schihütte", "⛷️ Piste 1 (Blau)"), ("⛷️ Piste 1 (Blau)", "🏠 Silbertaler Alm"),
        ("🏠 Silbertaler Alm", "🚠 Gaislachkogl I (Tal)"), ("💺 Stabele", "🏠 Gaislachalm"),
        ("🏠 Gaislachalm", "🏠 Löple Alm"), ("🏠 Löple Alm", "⛷️ Piste 1 (Blau)"),
        ("💺 Heidebahn", "🏠 Heidealm"), ("🏠 Heidealm", "⛷️ Piste 4 (Blau)"),
        ("🚠 Giggijochbahn (Berg)", "🏠 Wirtshaus Giggijoch"), ("🏠 Wirt
