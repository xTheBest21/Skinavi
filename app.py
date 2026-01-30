import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
import requests
import base64
from io import BytesIO

# 1. Seite konfigurieren
st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

# WICHTIG: Wir nutzen eine URL, um Ladeprobleme zu vermeiden
# Ich habe hier einen Beispiel-Link gesetzt. Ersetze ihn ggf. durch deinen GitHub-Raw-Link.
IMAGE_URL = "https://raw.githubusercontent.com/Soelden-Fan/SkiNavi/main/soelden_pistenplan.jpg"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]

@st.cache_resource
def get_base64_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
    except:
        return None
    return None

img_b64 = get_base64_image(IMAGE_URL)

# 2. Das Ski-Netzwerk (Punkte auf dem Bild)
@st.cache_resource
def build_network():
    G = nx.DiGraph()
    # Koordinaten (Y, X) - Schätzwerte passend zum Plan
    nodes = {
        "Gaislachkogl Tal": (130, 360),
        "Gaislachkogl Mittelstation": (400, 310),
        "Gaislachkogl Gipfel": (610, 280),
        "Giggijoch Tal": (70, 750),
        "Giggijoch Berg": (510, 880),
        "Rettenbachgletscher": (700, 480),
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

G, nodes = build_network()

# --- UI ---
st.title("⛷️ Ski Navi Sölden")

if not img_b64:
    st.error("Bild-Fehler: Die App konnte den Pistenplan nicht laden. Bitte Internetverbindung prüfen.")
    st.stop()

#
