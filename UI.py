import streamlit as st
import pandas as pd




if "state" not in st.session_state:
    st.session_state["state"] = "state_start"

def go_to_state_start():
    st.session_state["state"] = "state_start"

def go_to_state_create_mechanism():
    st.session_state["state"] = "state_create_mechanism"

def go_to_state_load_mechanism():
    st.session_state["state"] = "state_load_mechanism"



if st.session_state["state"] == "state_start":
    st.title("Simulation der Kinematik eines ebenen Mechanismus")
    st.button("Neuen Mechanismus erstellen", on_click=go_to_state_create_mechanism)
    st.button("Mechanismus laden", on_click=go_to_state_load_mechanism)

elif st.session_state["state"] == "state_create_mechanism":
    st.header("Neuen Mechanismus erstellen")
    points = pd.DataFrame({
        "Punkt": [1, 2, 3],
        "x-Koordinate": [10, 20, 30],
        "y-Koordinate": [20, 30, 40],
        "Statisch?" : [False, False, False]
    })
    links = {
        "1" : {"1" : False, "2" : True, "3": True},
        "2" : {"1" : True, "2" : False, "3": True},
        "3" : {"1" : True, "2": True, "3": False}
    }
    st.write("Bitte hier Punkte eingtragen")
    table_points = st.data_editor(points, num_rows="dynamic")   #returns a pandas dataframe with all points in it
    st.write("Bitte hier Verbindungenn zwischen den Punkten eingtragen")
    table_links = st.data_editor(links, num_rows="dynamic")     #returns a graph with all links in it
    st.button("Speichern")
    st.button("Zurück", on_click=go_to_state_start)

elif st.session_state["state"] == "state_load_mechanism":
    st.header("Mechanismus laden")
    st.selectbox("Mechanismus auswählen",
                  ["Mechanismus 1", "Mechanismus 2", "Mechanismus 3"])
    st.button("Zurück", on_click=go_to_state_start)