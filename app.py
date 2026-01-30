import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium

# Seiten-Konfiguration
st.set_page_config(page_title="Ski Navi Sölden", layout="wide", page_icon="⛷️")

# Styling für ein modernes Interface
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# 1. Daten-Setup basierend auf dem Sölden Pistenplan
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    
    # Koordinaten-Punkte (Knoten)
    # Format: "Name": (Breitengrad, Längengrad)
    nodes = {
        "Sölden Tal (Gaislachkogl)": (46.9607, 11.0075),
        "Gaislachkogl Mittelstation": (46.9515, 10.9855),
        "Gaislachkogl Gipfel (3058m)": (46.9422, 10.9672),
        "Heuberg / Wasserkar": (46.9555, 10.9950),
        "Giggijoch Tal": (46.9715, 11.0085),
        "Giggijoch Berg (2284m)": (46.9745, 10.9755),
        "Hochsölden (2090m)": (46.9785, 10.9905),
        "Rotkoglbahn Berg": (46.9635, 10.9655),
        "Rettenbachgletscher (Basis)": (46.9285, 10.9415),
        "Hintere Bachlhütte": (46.9655, 10.9805),
        "Tiefenbachgletscher": (46.9215, 10.9255)
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

    # Verbindungen (Kanten) - Pisten sind Einbahnstraßen!
    # Format: (Start, Ziel, Typ, Name, Schwierigkeit/Gewicht)
    edges = [
        # Gaislachkogl Sektor
        ("Sölden Tal (Gaislachkogl)", "Gaislachkogl Mittelstation", "🚠 Lift", "Gaislachkoglbahn I", 1),
        ("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel (3058m)", "🚠 Lift", "Gaislachkoglbahn II", 1),
        ("Gaislachkogl Gipfel (3058m)", "Gaislachkogl Mittelstation", "⛷️ Piste", "Piste 1 (Rot)", 2),
        ("Gaislachkogl Mittelstation", "Sölden Tal (Gaislachkogl)", "⛷️ Piste", "Piste 4 (Blau)", 1),
        ("Gaislachkogl Mittelstation", "Heuberg / Wasserkar", "⛷️ Piste", "Piste 5 (Rot)", 2),
        
        # Giggijoch Sektor
        ("Giggijoch Tal", "Giggijoch Berg (2284m)", "🚠 Lift", "Giggijochbahn", 1),
        ("Giggijoch Berg (2284m)", "Hochsölden (2090m)", "⛷️ Piste", "Piste 13 (Blau)", 1),
        ("Giggijoch Berg (2284m)", "Rotkoglbahn Berg", "🚠 Lift", "Rotkoglbahn", 1),
        ("Giggijoch Berg (2284m)", "Hintere Bachlhütte", "⛷️ Piste", "Piste 11 (Rot)", 2),
        
        # Verbindung zum Gletscher (Golden Gate)
        ("Giggijoch Berg (2284m)", "Rettenbachgletscher (Basis)", "🚠 Lift", "Gletscherexpress", 1),
        ("Rettenbachgletscher (Basis)", "Tiefenbachgletscher", "🚠 Lift", "Gletscherverbindung", 1)
    ]
    
    for u, v, kind, label, weight in edges:
        G.add_edge(u, v, kind=kind, label=label, weight=weight)
        
    return G, nodes

G, nodes = build_soelden_graph()

# --- SIDEBAR ---
st.sidebar.title("⛷️ Ski Navi Einstellungen")
st.sidebar.info("Navigiere sicher durch Sölden.")

# Auswahlboxen für Start und Ziel
start_node = st.sidebar.selectbox("Dein Standort:", options=sorted(list(nodes.keys())))
target_node = st.sidebar.selectbox("Dein Ziel:", options=sorted(list(nodes.keys())))

# Button zur Berechnung
calc_button = st.sidebar.button("Route berechnen", use_container_width=True)

# Kleiner Tipp in der Sidebar
st.sidebar.markdown("---")
st.sidebar.write("**Hinweis:** Pisten sind als Einbahnstraßen programmiert. Du kannst also nicht die Piste hochfahren! 😉")

# --- HAUPTBEREICH ---
st.title("Sölden Interaktive Skikarte")

# Karte initialisieren
# Zentrum von Sölden Skigebiet
m = folium.Map(location=[46.955, 10.985], zoom_start=13, tiles=None)

# Layer 1: Standard Karte
folium.TileLayer('OpenStreetMap', name="Standard Karte").add_to(m)

# Layer 2: OpenSnowMap (Pisten-Details)
folium.TileLayer(
    tiles='https://tiles.opensnowmap.org/pistes/{z}/{x}/{y}.png',
    attr='&copy; OpenSnowMap.org',
    name="Skipisten & Lifte",
    overlay=True,
    control=True
).add_to(m)

# Logik bei Button-Klick
if calc_button:
    if start_node == target_node:
        st.warning("Du bist bereits am Ziel!")
    else:
        try:
            # Dijkstra Algorithmus für den effizientesten Weg
            path = nx.shortest_path(G, source=start_node, target=target_node, weight='weight')
            
            # Wegbeschreibung anzeigen
            st.subheader("Deine Route:")
            cols = st.columns(len(path)-1)
            
            path_coords = []
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                edge_data = G.get_edge_data(u, v)
                
                with st.expander(f"Schritt {i+1}: {edge_data['label']}"):
                    st.write(f"Von: **{u}**")
                    st.write(f"Nach: **{v}**")
                    st.write(f"Typ: {edge_data['kind']}")
                
                path_coords.append(nodes[u])
                if i == len(path)-2: # Letzten Punkt hinzufügen
                    path_coords.append(nodes[v])

            # Zeichnen auf der Karte
            folium.PolyLine(path_coords, color="#FF4B4B", weight=8, opacity=0.8, popup="Deine Route").add_to(m)
            folium.Marker(nodes[start_node], popup="START", icon=folium.Icon(color='green', icon='play')).add_to(m)
            folium.Marker(nodes[target_node], popup="ZIEL", icon=folium.Icon(color='red', icon='stop')).add_to(m)
            
            # Karte automatisch auf die Route zentrieren
            m.fit_bounds(path_coords)

        except nx.NetworkXNoPath:
            st.error("Keine Verbindung gefunden! Bitte wähle einen anderen Zielpunkt oder prüfe die Liftverbindungen.")

# Karte rendern
st_folium(m, width="100%", height=600)

# Optional: Bild des Pistenplans als Referenz unter der Karte
with st.expander("Original Pistenplan Sölden anzeigen"):
    st.image("https://www.soelden.com/main/DE/WI/Skigebiet/Pistenplan/images/pistenplan-soelden.jpg", use_column_width=True)
