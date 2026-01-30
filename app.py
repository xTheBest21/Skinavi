import streamlit as st

st.title("Sölden Test-Modus")
st.write("Wenn du das liest, ist der alte Fehler weg!")

option = st.selectbox("Test Auswahl", ["A", "B", "C"], key="test_select_v1")
st.write(f"Du hast {option} gewählt.")
