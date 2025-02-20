import streamlit as st
import pandas as pd
import mechanism as mechanism




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

    mechanism_name = st.text_input("Bitte hier Name des Mechanismus eingeben")
    number_of_points = st.number_input("Anzahl der Punkte", min_value=1, step=1, value=4)
    points = {
        "Punkt": [f"{i}" for i in range(number_of_points)],
        "x-Koordinate": [0 for i in range(number_of_points)],
        "y-Koordinate": [0 for i in range(number_of_points)],
        "Statisch": [False for i in range(number_of_points)],
        "Kurbel" : [False for i in range(number_of_points)],
    }

    st.write("Bitte hier Punkte eingetragen")
    table_points = st.data_editor(points) 

    st.write("Bitte hier Verbindungen zwischen den Punkten eingetragen")
    links = {point: [False] * len(points["Punkt"]) for point in points["Punkt"]}
    table_links = st.data_editor(links, hide_index=False)
    
    if st.button("Speichern"):
        mechanism.Mechanism(mechanism_name, table_points, table_links).store_data()
        st.success("Mechanismus gespeichert")
        st.button("Mechanismus laden", on_click=go_to_state_load_mechanism)

    st.button("Zurück", on_click=go_to_state_start)

elif st.session_state["state"] == "state_load_mechanism":
    st.header("Mechanismus simulieren oder bearbeiten")
    mechanism_list = mechanism.Mechanism.find_all()
    if len(mechanism_list) == 0:
        st.warning("Keine Mechanismen gefunden")
    else:
        loaded_mechanism_name = st.selectbox("Mechanismus auswählen",
                                        [mechanism.name for mechanism in mechanism_list])
        loaded_mechanism_instance = mechanism.Mechanism.find_by_attribute("name", loaded_mechanism_name)
        st.write(f"Name: {loaded_mechanism_instance.name}")
        loaded_mechanism_instance.table_points = st.data_editor(loaded_mechanism_instance.table_points)
        loaded_mechanism_instance.table_links = st.data_editor(loaded_mechanism_instance.table_links)
        if st.button("Speichern"):
            loaded_mechanism_instance.store_data()
            st.success("Mechanismus gespeichert")
        st.button("Löschen", on_click=loaded_mechanism_instance.delete_data)

    st.button("Zurück", on_click=go_to_state_start)
