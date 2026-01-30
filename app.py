import networkx as nx

G = nx.Graph()

# Verbindungen hinzufügen (Start, Ziel, Typ/Schwierigkeit)
G.add_edge("Giggijoch", "Silberbrünnl", type="Lift")
G.add_edge("Silberbrünnl", "Hintere Bachlhütte", type="Piste", difficulty="blue")
