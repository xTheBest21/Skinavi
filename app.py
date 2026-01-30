import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium

# Seiten-Konfiguration
st.set_page_config(page_title="Ski Navi Sölden", layout="wide")

st.title("⛷️ Ski Navi Sölden")
st.markdown("Dein interaktiver Begleiter durch das Skigebiet Sölden.")

# 1. Daten-Setup (Beispiel-Knoten für Sölden)
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    # Koordinaten einiger Hotspots in Sölden
    nodes = {
        "Gaislachkogl Gipfel": (46.942, 10.967),
        "Gaislachkogl Mittelstation": (46.952, 10.985),
        "Gaislachkogl Tal": (46.960, 11.007),
        "Giggijoch Berg": (46.974, 10.975),
        "Giggijoch Tal": (46.971, 11.008),
        "Hintere Bachlhütte": (46.965, 10.980),
        "Rettenbachgletscher": (46.928, 10.941)
        # 2. Verbindungs-Logik (Pistenfarben & Lifte)
edges = [
    # Gaislachkogl Sektor
    ("Sölden Tal (Gaislachkogl)", "Gaislachkogl Mittelstation", "🚠 Lift", "Gaislachkoglbahn I"),
    ("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel (3058m)", "🚠 Lift", "Gaislachkoglbahn II"),
    ("Gaislachkogl Gipfel (3058m)", "Gaislachkogl Mittelstation", "⛷️ Rote Piste", "Piste 1"),
    ("Gaislachkogl Mittelstation", "Sölden Tal (Gaislachkogl)", "⛷️ Blaue Piste", "Piste 4/5"),
    
    # Giggijoch Sektor
    ("Giggijoch Tal", "Giggijoch Berg (2284m)", "🚠 Lift", "Giggijochbahn"),
    ("Giggijoch Berg (2284m)", "Hochsölden (2090m)", "⛷️ Blaue Piste", "Piste 13/15"),
    ("Giggijoch Berg (2284m)", "Rotkoglbahn Berg", "🚠 Lift", "Rotkoglbahn"),
    
    # Verbindung (Golden Gate)
    ("Giggijoch Berg (2284m)", "Rettenbachgletscher", "🚠 Lift", "Einzeiger / Gletscherexpress")
]
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

    # Verbindungen (Pisten & Lifte)
    edges = [
        ("Gaislachkogl Tal", "Gaislachkogl Mittelstation", "🚠 Lift", "Gaislachkoglbahn I"),
        ("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel", "🚠 Lift", "Gaislachkoglbahn II"),
        ("Gaislachkogl Gipfel", "Gaislachkogl Mittelstation", "⛷️ Piste", "Blaue 1"),
        ("Gaislachkogl Mittelstation", "Hintere Bachlhütte", "⛷️ Piste", "Rote 5"),
        ("Giggijoch Tal", "Giggijoch Berg", "🚠 Lift", "Giggijochbahn"),
        ("Giggijoch Berg", "Hintere Bachlhütte", "⛷️ Piste", "Blaue 11")
    ]
    
    for u, v, kind, label in edges:
        G.add_edge(u, v, kind=kind, label=label)
        
    return G, nodes

G, nodes = build_soelden_graph()

# 2. Sidebar für die Navigation
st.sidebar.header("Routenplanung")
start_node = st.sidebar.selectbox("Mein Standort:", options=sorted(list(nodes.keys())))
target_node = st.sidebar.selectbox("Mein Ziel:", options=sorted(list(nodes.keys())))

# 3. Karten-Logik
# Wir nutzen OpenSnowMap als Hintergrund-Layer
m = folium.Map(location=[46.955, 10.985], zoom_start=13, tiles=None)

# Standard OpenStreetMap
folium.TileLayer('OpenStreetMap', name="Standard Karte").add_to(m)

# Spezial-Layer für Skifahrer
folium.TileLayer(
    tiles='https://tiles.opensnowmap.org/pistes/{z}/{x}/{y}.png',
    attr='&copy; OpenSnowMap.org',
    name="Skipisten & Lifte",
    overlay=True,
    control=True
).add_to(m)

# Route berechnen, wenn der Button gedrückt wird
if st.sidebar.button("Route anzeigen"):
    try:
        path = nx.shortest_path(G, source=start_node, target=target_node)
        
        st.sidebar.success("Weg gefunden!")
        
        # Wegbeschreibung als Liste
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            edge_data = G.get_edge_data(u, v)
            st.sidebar.write(f"**{i+1}.** {edge_data['label']} ({edge_data['kind']})")
            st.sidebar.write(f"➔ bis {v}")

        # Route auf der Karte zeichnen
        path_coords = [nodes[node] for node in path]
        folium.PolyLine(path_coords, color="blue", weight=7, opacity=0.7).add_to(m)
        folium.Marker(nodes[start_node], popup="Start", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(nodes[target_node], popup="Ziel", icon=folium.Icon(color='red')).add_to(m)

    except nx.NetworkXNoPath:
        st.sidebar.error("Keine Verbindung gefunden. Wähle andere Punkte!")

# Karte in Streamlit rendern
st_folium(m, width="100%", height=600)
