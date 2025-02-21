import networkx as nx
import matplotlib.pyplot as plt
import mechanism as mechanism
import streamlit as st


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
        nx.draw(G, pos, with_labels=True, node_size=100, edge_color='blue')
        st.pyplot(fig)
        



if __name__ == "__main__":
    visualiser = Visualiser("Test1")
    visualiser.draw_mechanism()


        


        
    
