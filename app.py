import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium

st.title("Sölden Ski-Navigator ⛷️")

# 1. Netzwerk-Daten definieren (Beispiel-Daten Sölden)
@st.cache_resource
def build_soelden_graph():
    G = nx.DiGraph()
    
    # Knoten: (Name, {Koordinaten})
    nodes = {
        "Gaislachkogl Tal": (46.960, 11.007),
        "Gaislachkogl Mittelstation": (46.952, 10.985),
        "Gaislachkogl Gipfel": (46.942, 10.967),
        "Giggijoch Tal": (46.971, 11.008),
        "Giggijoch Berg": (46.974, 10.975),
        "Hintere Bachlhütte": (46.965, 10.980)
    }
    
    for name, pos in nodes.items():
        G.add_node(name, pos=pos)

    # Kanten: (Start, Ziel, Typ, Name)
    # Beachte: Pisten meist nur bergab, Lifte bergauf
    edges = [
        ("Gaislachkogl Tal", "Gaislachkogl Mittelstation", "Lift", "Gaislachkoglbahn I"),
        ("Gaislachkogl Mittelstation", "Gaislachkogl Gipfel", "Lift", "Gaislachkoglbahn II"),
        ("Gaislachkogl Gipfel", "Gaislachkogl Mittelstation", "Piste", "Piste 1"),
        ("Gaislachkogl Mittelstation", "Hintere Bachlhütte", "Piste", "Piste 5"),
        ("Giggijoch Tal", "Giggijoch Berg", "Lift", "Giggijochbahn"),
        ("Giggijoch Berg", "Hintere Bachlhütte", "Piste", "Piste 11"),
    ]
    
    for u, v, kind, label in edges:
        G.add_edge(u, v, kind
