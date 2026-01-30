import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
import base64
import requests
from io import BytesIO
from PIL import Image

# 1. Seite einrichten
st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

# HINWEIS: Ersetze 'DEIN_NUTZERNAME' und 'DEIN_REPO' mit deinen echten GitHub-Daten!
# Dies ist der direkteste Weg, um das Bild zu laden.
IMAGE_URL = "https://raw.githubusercontent.com/DEIN_NUTZERNAME/DEIN_REPO/main/soelden_pistenplan.jpg"
IMAGE_BOUNDS = [[0, 0], [1000, 1400]]

@st.cache_resource
def load_image_to_base64(url):
    try:
        # Wir laden das Bild über das Internet, um lokale Pfadfehler zu vermeiden
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Teste ob es ein gültiges Bild ist
            img = Image.open(BytesIO(response.content))
            # Konvertiere zu Base64 für Folium
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        return f"Error: {e}"
    return None

img_b64 = load_image_to_base64(IMAGE_URL)

# 2. Das Ski-Netzwerk (Punkte auf dem Plan)
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    # Koordinaten (Y, X) - angepasst an den Plan
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

G, nodes = build_soelden_graph()

# --- UI ---
st.title("⛷️ Ski Navi Sölden")

if img_b64 is None or "Error" in str(img_b64):
    st.error(f"⚠️ Bildfehler
