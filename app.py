import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import requests
import json
import os
import math

# --- FUNKTIONEN ---

def berechne_distanz(pos1, pos2):
    """Berechnet die Entfernung in km zwischen zwei GPS-Punkten"""
    lat1, lon1 = pos1
    lat2, lon2 = pos2
    radius = 6371 # Erd-Radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c

# ... (Hier bleibt dein bisheriger Code für Seite einrichten und Daten laden gleich) ...

# (Wir springen direkt zu Punkt 5: Standort und Ziel eintragen)

if location:
    my_pos = [location['lat'], location['lon']]
    ziel_coords = huetten[ziel_name]
    
    # 1. Distanz berechnen
    distanz = berechne_distanz(my_pos, ziel_coords)
    
    # 2. Navigations-Anweisungen unter der Karte vorbereiten
    st.subheader("📍 Deine Route")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Entfernung", f"{distanz:.2f} km")
    with col2:
        # Schätzung: Skifahrer fahren ca. 20 km/h im Schnitt
        zeit = (distanz / 20) * 60
        st.metric("Geschätzte Zeit", f"{int(zeit)} Min")

    # 3. Anweisungs-Liste
    st.info(f"**Anweisung:** Folge der Richtungspfeil zur {ziel_name}. Nutze vorzugsweise die blauen Pisten in deiner Nähe.")

    # (Hier folgt der Code für die Karte m = folium.Map...)
# ... (dein restlicher Standort-Code unten bleibt gleich) ...
