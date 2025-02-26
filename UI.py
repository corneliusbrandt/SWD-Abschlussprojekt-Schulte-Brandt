import streamlit as st
import pandas as pd
import mechanism as mechanism
import visualiser as visualiser
import SVGImporter


st.set_page_config(layout="wide")

if "state" not in st.session_state:
    st.session_state["state"] = "state_start"

def go_to_state_start():
    st.session_state["state"] = "state_start"

def go_to_state_create_mechanism():
    st.session_state["state"] = "state_create_mechanism"

def go_to_state_load_mechanism():
    st.session_state["state"] = "state_load_mechanism"

def go_to_solve_mechanism():
    st.session_state["state"] = "state_solve_mechanism"

def go_to_state_import_svg():
    st.session_state["state"] = "state_import_svg"



if st.session_state["state"] == "state_start":
    st.title("Simulation der Kinematik eines ebenen Mechanismus")
    st.button("Neuen Mechanismus erstellen", on_click=go_to_state_create_mechanism)
    st.button("Mechanismus laden", on_click=go_to_state_load_mechanism)
    st.button("Mechanismus lösen", on_click=go_to_solve_mechanism)
    st.button("SVG importieren", on_click=go_to_state_import_svg)

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
        "Bahnkurve": [False for i in range(number_of_points)]
    }

    st.write("Bitte hier Punkte eingetragen")
    table_points = st.data_editor(points) 

    st.write("Bitte hier Verbindungen zwischen den Punkten eingetragen")
    links = {f"{i}": [False] * number_of_points for i in range(number_of_points)}
    table_links = st.data_editor(links, hide_index=False)


    #if st.button("Vorschau des Mechanismus"):
        #temporary_mechanism = mechanism.Mechanism(mechanism_name, table_points, table_links)
        #visualiser = visualiser.Visualiser(temporary_mechanism)
        #visualiser.draw_mechanism()

    if st.button("Speichern"):
        print("Points:", table_points)
        print("Links:", table_links)
        # mechanism.Mechanism(mechanism_name, table_points, table_links).store_data()
        try:
            mechanism.Mechanism(mechanism_name, table_points, table_links).store_data()
            st.success("Mechanismus gespeichert")
        except Exception as e:
            st.error(f"Fehler beim Speichern des Mechanismus: {e}")
        st.button("Mechanismus laden", on_click=go_to_state_load_mechanism)

    st.button("Zurück", on_click=go_to_state_start)

elif st.session_state["state"] == "state_load_mechanism":
    st.header("Mechanismus bearbeiten")
    mechanism_list = mechanism.Mechanism.find_all()
    if len(mechanism_list) == 0:
        st.warning("Keine Mechanismen gefunden")
    else:
        col1, col2 = st.columns([2, 1])
        loaded_mechanism_name = col1.selectbox("Mechanismus auswählen",
                                        [mechanism.name for mechanism in mechanism_list])
        loaded_mechanism_instance = mechanism.Mechanism.find_by_attribute("name", loaded_mechanism_name)

        col1.write(f"Name: {loaded_mechanism_instance.name}")
        loaded_mechanism_instance.table_points = col1.data_editor(loaded_mechanism_instance.table_points)
        loaded_mechanism_instance.table_links = col1.data_editor(loaded_mechanism_instance.table_links, hide_index=False)

        col2.write("Visualisierung des Mechanismus")
        with col2:
            visualiser = visualiser.Visualiser(loaded_mechanism_name)
            visualiser.draw_mechanism()

        if st.button("Speichern"):
            loaded_mechanism_instance.store_data()
            st.success("Mechanismus gespeichert")
            st.rerun()
        st.button("Löschen", on_click=loaded_mechanism_instance.delete_data)

    st.button("Zurück", on_click=go_to_state_start)

elif st.session_state["state"] == "state_solve_mechanism":
        st.header("Mechanismus lösen")
        mechanism_list = mechanism.Mechanism.find_all()
        if len(mechanism_list) == 0:
            st.warning("Keine Mechanismen gefunden")
        else:
            col1, col2 = st.columns([1, 1])
            with col1:
                selected_mechanism_name = st.selectbox("Mechanismus auswählen", [mech.name for mech in mechanism_list])
                selected_mechanism_instance = mechanism.Mechanism.find_by_attribute("name", selected_mechanism_name)

                st.write(f"Name: {selected_mechanism_instance.name}")
                st.write("Punkte:")
                st.dataframe(selected_mechanism_instance.table_points)
                st.write("Verbindungen:")
                st.dataframe(selected_mechanism_instance.table_links)

                if st.button("Mechanismus lösen"):
                    selected_mechanism_instance.solve_mechanism()
                    solution = selected_mechanism_instance.kinematics.solved_points
                    st.success("Der Mechanismus wird gelöst und automatisch in ihrem Download-Ordner gespeichert.")
                    #st.write("Lösung:")
                    #st.write(solution)
                
                    with col2:
                        visualiser = visualiser.Visualiser(selected_mechanism_name)
                        visualiser.animate_mechanism(solution)

        st.button("Zurück", on_click=go_to_state_start)
        

            

elif st.session_state["state"] == "state_import_svg":
    st.header("SVG Datei importieren")
    uploaded_file = st.file_uploader("SVG Datei hochladen", type="svg")

    if uploaded_file is not None:
        svg_content = uploaded_file.read().decode("utf-8")
        parsed_data = SVGImporter.parse_svg(svg_content)

        st.success("SVG Datei erfolgreich importiert")
        
        mechanism_name = st.text_input("Name des Mechanismus", value="Imported Mechanism")
        if "points" in parsed_data and "links" in parsed_data:
            points = parsed_data["Punkte"]
            links = parsed_data["Glieder"]
        else:
            st.error("Fehler: Die SVG-Datei enthält keine gültigen Punkte und Verbindungen.")
            st.stop()

        st.write("Punkte:")
        points = st.data_editor(points)

        st.write("Verbindungen:")
        links = st.data_editor(links, hide_index=False)

        st.write("Punkte:")
        table_points = st.data_editor(points)

        st.write("Verbindungen:")
        table_links = st.data_editor(links, hide_index=False)

        col1, col2 = st.columns([2, 1])
        with col2:
            visualiser = visualiser.Visualiser(mechanism_name)
            visualiser.draw_mechanism()

        if st.button("Speichern"):
            try:
                mechanism.Mechanism(mechanism_name, table_points, table_links).store_data()
                st.success("Mechanismus gespeichert")
            except Exception as e:
                st.error(f"Fehler beim Speichern des Mechanismus: {e}")
            st.button("Mechanismus laden", on_click=go_to_state_load_mechanism)

    st.button("Zurück", on_click=go_to_state_start)