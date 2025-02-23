import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mechanism as mechanism
import streamlit as st
import io


class Visualiser:
    def __init__(self, mechanism_to_visualise):
        self.mechanism_to_visualise = mechanism.Mechanism.find_by_attribute("name", mechanism_to_visualise)

    def data_to_graph(self):
        G = nx.Graph()
        for n, p1 in enumerate(self.mechanism_to_visualise.table_points["Punkt"]):
            (x , y) = (self.mechanism_to_visualise.table_points["x-Koordinate"][n], self.mechanism_to_visualise.table_points["y-Koordinate"][n])
            G.add_node(p1, pos=(x, y))

        links = self.mechanism_to_visualise.table_links
        for i, p1 in enumerate(self.mechanism_to_visualise.table_points["Punkt"]):
            for j, p2 in enumerate(self.mechanism_to_visualise.table_points["Punkt"]):
                if links[p1][j]:
                    G.add_edge(p1, p2)
        return G
    
    def draw_mechanism(self):
        G = self.data_to_graph()
        pos = nx.get_node_attributes(G, 'pos')
        fig, ax = plt.subplots()
        nx.draw(G, pos, with_labels=True, node_size=50, node_color='red', edge_color='blue', width=2.0, ax=ax)
        st.pyplot(fig)

    def animate_mechanism(self):
        fig, ax = plt.subplots()
        G = self.data_to_graph()
        pos = nx.get_node_attributes(G, 'pos')
        

        def update_animation(frame):
            # Here comes a function that updates the position of the nodes by getting them out of the database for each step
            pass

        mechanism_animation = animation.FuncAnimation(fig, update_animation, frames=360, interval=20)

        buffer = io.BytesIO()
        mechanism_animation.save(buffer, format='gif', writer=animation.PillowWriter(fps=10))
        buffer.seek(0)
        st.image(buffer, use_column_width=True)
        



if __name__ == "__main__":
    visualiser = Visualiser("Test1")
    visualiser.draw_mechanism()


        


        
    
