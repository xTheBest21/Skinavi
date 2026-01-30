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
        "Tiefenbachgletscher": (46
