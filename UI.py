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
    col1, col2 = st.columns([2, 1])
    with col1:
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
    col2.write("Visualisierung des Mechanismus")
    with col2:
        # temp_mechanism_instance = mechanism.Mechanism("Preview", data_glieder, data_gelenke)
        # visualiser = visualiser.Visualiser("Preview", temp_mechanism_instance)
        # visualiser.draw_mechanism()'
        try:
            temp_mechanism_instance = mechanism.Mechanism("Preview", points, links, temp=True)
            visualiser = visualiser.Visualiser("Preview", temp_mechanism_instance)
            visualiser.draw_mechanism()
        except Exception as e:
            st.warning(f"Warnung: {e}")


    #if st.button("Vorschau des Mechanismus"):
        #temporary_mechanism = mechanism.Mechanism(mechanism_name, table_points, table_links)
        #visualiser = visualiser.Visualiser(temporary_mechanism)
        #visualiser.draw_mechanism()

    if st.button("Speichern"):
        # print("Points:", table_points)
        # print("Links:", table_links)
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
        temp_table_points = loaded_mechanism_instance.table_points.copy()
        temp_table_links = loaded_mechanism_instance.table_links.copy()

        col1.write(f"Name: {loaded_mechanism_instance.name}")
        temp_table_points = col1.data_editor(temp_table_points)
        temp_table_links = col1.data_editor(temp_table_links, hide_index=False)

        col2.write("Visualisierung des Mechanismus")
        with col2:
            try:
                temp_mechanism_instance = mechanism.Mechanism("Preview", temp_table_points, temp_table_links, temp=True)
                visualiser = visualiser.Visualiser("Preview", temp_mechanism_instance)
                visualiser.draw_mechanism()
            except Exception as e:
                st.warning(f"Warnung: {e}")

        if st.button("Speichern"):
            try:
                temp_mechanism_instance = mechanism.Mechanism("Preview", temp_table_points, temp_table_links)
                loaded_mechanism_instance.table_points = temp_table_points
                loaded_mechanism_instance.table_links = temp_table_links
                loaded_mechanism_instance.store_data()
                st.success("Mechanismus gespeichert")
            except Exception as e:
                st.error(f"Fehler beim Speichern des Mechanismus: {e}")

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
                step_size = st.number_input("Schrittweite für die Lösung", min_value=1, step=1, value=1)
                selected_mechanism_instance.kinematics.set_step_size(step_size)

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
                        st.download_button(
                            label="Bahnkurve als CSV-Datei herunterladen",
                            data=visualiser.save_trajectory_to_csv(solution),
                            file_name="daten.csv",
                            mime="text/csv",
                        )

                        

        st.button("Zurück", on_click=go_to_state_start)
        

            

elif st.session_state["state"] == "state_import_svg":
    st.header("SVG Datei importieren")
    uploaded_file = st.file_uploader("SVG Datei hochladen", type="svg")

    if uploaded_file is not None:
        if "uploaded_file_content" not in st.session_state:
            svg_content = uploaded_file.read().decode("utf-8")
            st.session_state["uploaded_file_content"] = svg_content
        else:
            svg_content = st.session_state["uploaded_file_content"]

        parsed_data_gelenke, parsed_data_glieder = SVGImporter.parse_svg(svg_content)

        st.success("SVG Datei erfolgreich importiert")
        
        mechanism_name = st.text_input("Name des Mechanismus", value="Imported Mechanism")

        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("Punkte:")
            data_gelenke = st.data_editor(parsed_data_gelenke)
            # print("Glieder Type:", type(data_gelenke))
            # print("Glieder:", data_gelenke)


            st.write("Verbindungen:")
            data_glieder = st.data_editor(parsed_data_glieder, hide_index=False)
            # print("Gelenke Type:", type(data_glieder))
            # print("Gelenke:", data_glieder)

            # selected_point = st.selectbox("Punkt zum Löschen auswählen", data_gelenke["Punkt"])
            
            # if st.button("Punkt löschen"):
            #     if selected_point in data_gelenke["Punkt"]:
            #         index_to_delete = data_gelenke["Punkt"].index(selected_point)
            #         data_glieder = {key: [val for i, val in enumerate(values) if i != index_to_delete] for key, values in data_glieder.items()}
            #         data_gelenke = {key: [val for i, val in enumerate(values) if i != index_to_delete] for key, values in data_gelenke.items()}
            #         data_gelenke = {key: [val for i, val in enumerate(values) if i != index_to_delete] for key, values in data_gelenke.items()}
            #         st.success(f"Punkt {selected_point} wurde gelöscht")
            #     else:
            #         st.warning(f"Punkt {selected_point} nicht gefunden")
        
        col2.write("Visualisierung des Mechanismus")
        with col2:
            # temp_mechanism_instance = mechanism.Mechanism("Preview", data_glieder, data_gelenke)
            # visualiser = visualiser.Visualiser("Preview", temp_mechanism_instance)
            # visualiser.draw_mechanism()'
            try:
                temp_mechanism_instance = mechanism.Mechanism("Preview", data_gelenke, data_glieder, temp=True)
                visualiser = visualiser.Visualiser("Preview", temp_mechanism_instance)
                visualiser.draw_mechanism()
            except Exception as e:
                st.warning(f"Warnung: {e}")

        if st.button("Speichern"):
            try:
                mechanism.Mechanism(mechanism_name, data_gelenke, data_glieder).store_data()
                st.success("Mechanismus gespeichert")
            except Exception as e:
                st.error(f"Fehler beim Speichern des Mechanismus: {e}")
            st.button("Mechanismus laden", on_click=go_to_state_load_mechanism)

    st.button("Zurück", on_click=go_to_state_start)