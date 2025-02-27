import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mechanism as mechanism
import streamlit as st
import numpy as np
import pandas as pd
import io
import os


class Visualiser:
    def __init__(self, mechanism_to_visualise_name, mechanism_to_visualise=None):
        if mechanism_to_visualise:
            self.mechanism_to_visualise = mechanism_to_visualise
        else:
            self.mechanism_to_visualise = mechanism.Mechanism.find_by_attribute("name", mechanism_to_visualise_name)

    def data_to_graph(self):
        G = nx.Graph()
        for n, p1 in enumerate(self.mechanism_to_visualise.table_points["Punkt"]):
            (x , y) = (self.mechanism_to_visualise.table_points["x-Koordinate"][n], self.mechanism_to_visualise.table_points["y-Koordinate"][n])
            G.add_node(p1, pos=(x, y))

        links = self.mechanism_to_visualise.table_links
        for i, p1 in enumerate(self.mechanism_to_visualise.table_points["Punkt"]):
            print("Data Type p1:", type(p1))
            for j, p2 in enumerate(self.mechanism_to_visualise.table_points["Punkt"]):
                if p1 in links and links[p1][j]:
                    G.add_edge(p1, p2)
        return G
    
    def calc_trajectory(self, solved_points):
        # Calculates the trajectory of the point where the parameter "Bahnkurve" is set to True
        point_index = 0
        for n, p1 in enumerate(self.mechanism_to_visualise.table_points["Bahnkurve"]):
            if p1:
                point_index = n
                print(f"Point {n} is a trajectory point.")
                trajectory = []
                for point in solved_points:
                    trajectory.append((point["x-Koordinate"][point_index], point["y-Koordinate"][point_index]))
                return trajectory
            else:
                print(f"Point {n} is not a trajectory point.")

    def save_trajectory_to_csv(self, solved_points):
        # Saves the trajectory of the point where the parameter "Bahnkurve" is set to True to a csv file
        trajectory = self.calc_trajectory(solved_points)
        if trajectory:
            df = pd.DataFrame(trajectory, columns=["x-Koordinate", "y-Koordinate"])
            buffer = io.BytesIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            return buffer
            
        
        
    
    def draw_mechanism(self):
        #Function for drawing a static picture of the mechanism
        G = self.data_to_graph()
        pos = nx.get_node_attributes(G, 'pos')

        fig, ax = plt.subplots()
        nx.draw(G, pos, with_labels=True, node_size=50, node_color='red', edge_color='blue', width=2.0, ax=ax)
        st.pyplot(fig)

    def animate_mechanism(self, solved_points):
        # Function for animating the mechanism

        # Calculate the radius for the circle around the rotation point
        rotation_index = self.mechanism_to_visualise.kinematics.data_gelenke['Punkt'].index(self.mechanism_to_visualise.kinematics.rotations_Punkt)
        antrieb_index = self.mechanism_to_visualise.kinematics.data_gelenke['Punkt'].index(self.mechanism_to_visualise.kinematics.antrieb)
        radius = np.linalg.norm(self.mechanism_to_visualise.kinematics.gelenke[rotation_index] - self.mechanism_to_visualise.kinematics.gelenke[antrieb_index])

        # Calculate the trajectory of the point where the parameter "Bahnkurve" is set to True
        trajectory_array = self.calc_trajectory(solved_points)

        fig, ax = plt.subplots()
        ax.set_xlim(-50, 50)
        ax.set_ylim(-70, 50)
        ax.set_aspect('equal', adjustable='box')
        ax.grid(True)  # Enable grid
        ax.axhline(0, color='black',linewidth=0.5)  # X-axis
        ax.axvline(0, color='black',linewidth=0.5)  # Y-axis
        G = self.data_to_graph()
        pos = nx.get_node_attributes(G, 'pos')

        # Add a circle around the rotation point
        circle = plt.Circle(self.mechanism_to_visualise.kinematics.gelenke[rotation_index], radius, color='r', fill=False)
        ax.add_artist(circle)

        # Add the trajectory
        if trajectory_array:
            x, y = zip(*trajectory_array)
            trajectory, = ax.plot(x, y, '-', lw=1, color='red')
            ax.add_artist(trajectory)


        #Draw the mechanism
        nx.draw(G, pos, node_size=50, node_color='red', edge_color='blue', width=2.0, ax=ax)        

        def update_animation(frame):
            ax.clear()
            ax.set_xlim(-50, 50)
            ax.set_ylim(-70, 50)
            ax.set_aspect('equal', adjustable='box')
            ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)  # Enable grid
            ax.axhline(0, color='black',linewidth=0.5)  # X-axis
            ax.axvline(0, color='black',linewidth=0.5)  # Y-axis
            ax.add_artist(circle)
            if trajectory_array:
                ax.add_artist(trajectory)
            for n, p1 in enumerate(solved_points[frame]["Punkt"]):
                (x , y) = (solved_points[frame]["x-Koordinate"][n], solved_points[frame]["y-Koordinate"][n])
                pos[p1] = (x, y)
            nx.draw(G, pos, node_size=50, node_color='red', edge_color='blue', width=2.0, ax=ax)
            
            

        mechanism_animation = animation.FuncAnimation(fig, update_animation, frames=len(solved_points), interval=20)

        #buffer = io.BytesIO()
        #mechanism_animation.save(buffer, writer="ffmpeg")
        #buffer.seek(0)
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", "mechanism.gif")
        mechanism_animation.save(downloads_path, writer=animation.PillowWriter(fps=10))
        st.image(downloads_path, use_container_width=True)
        



#if __name__ == "__main__":
    #visualiser = Visualiser("4 Punkt")
    #visualiser.draw_mechanism()


        


        
    
