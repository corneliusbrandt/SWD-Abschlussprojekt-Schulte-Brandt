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
            # print("Data Type p1:", type(p1))
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
                # print(f"Point {n} is a trajectory point.")
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
        ax.set_aspect('equal', adjustable='box')
        nx.draw(G, pos, with_labels=True, node_size=50, node_color='red', edge_color='blue', width=2.0, ax=ax)
        st.pyplot(fig)

    def animate_mechanism(self, solved_points, errors):
        # Function for animating the mechanism and plotting the error

        # Calculate the radius for the circle around the rotation point
        rotation_index = self.mechanism_to_visualise.kinematics.data_gelenke['Punkt'].index(self.mechanism_to_visualise.kinematics.rotations_Punkt)
        antrieb_index = self.mechanism_to_visualise.kinematics.data_gelenke['Punkt'].index(self.mechanism_to_visualise.kinematics.antrieb)
        radius = np.linalg.norm(self.mechanism_to_visualise.kinematics.gelenke[rotation_index] - self.mechanism_to_visualise.kinematics.gelenke[antrieb_index])

        # Calculate the trajectory of the point where the parameter "Bahnkurve" is set to True
        trajectory_array = self.calc_trajectory(solved_points)

        fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
        min_x = min(point["x-Koordinate"][n] for point in solved_points for n in range(len(point["x-Koordinate"])))
        max_x = max(point["x-Koordinate"][n] for point in solved_points for n in range(len(point["x-Koordinate"])))
        min_y = min(point["y-Koordinate"][n] for point in solved_points for n in range(len(point["y-Koordinate"])))
        max_y = max(point["y-Koordinate"][n] for point in solved_points for n in range(len(point["y-Koordinate"])))

        # Calculate the center and range
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        range_x = (max_x - min_x) * 1.5
        range_y = (max_y - min_y) * 1.5

        # Set the new limits
        ax1.set_xlim(center_x - range_x / 2, center_x + range_x / 2)
        ax1.set_ylim(center_y - range_y / 2, center_y + range_y / 2)
        ax1.set_aspect('equal', adjustable='box')
        G = self.data_to_graph()
        pos = nx.get_node_attributes(G, 'pos')

        # Add a circle around the rotation point
        circle = plt.Circle(self.mechanism_to_visualise.kinematics.gelenke[rotation_index], radius, color='r', fill=False)
        ax1.add_artist(circle)

        # Add the trajectory
        if trajectory_array:
            x, y = zip(*trajectory_array)
            trajectory, = ax1.plot(x, y, '-', lw=1, color='red')
            ax1.add_artist(trajectory)

        # Draw the mechanism
        nx.draw(G, pos, node_size=50, node_color='red', edge_color='blue', width=2.0, ax=ax1)

        def update_animation(frame):
            ax1.clear()
            ax1.set_xlim(center_x - range_x / 2, center_x + range_x / 2)
            ax1.set_ylim(center_y - range_y / 2, center_y + range_y / 2)
            ax1.add_artist(circle)
            if trajectory_array:
                ax1.add_artist(trajectory)
            for n, p1 in enumerate(solved_points[frame]["Punkt"]):
                (x , y) = (solved_points[frame]["x-Koordinate"][n], solved_points[frame]["y-Koordinate"][n])
                pos[p1] = (x, y)
            nx.draw(G, pos, node_size=50, node_color='red', edge_color='blue', width=2.0, ax=ax1)

            # Update error plot
            ax2.clear()
            ax2.plot(errors[:frame+1], color='blue')
            ax2.set_xlim(0, len(solved_points))
            ax2.set_ylim(0, max(errors) * 1.1)
            ax2.set_xlabel('Frame')
            ax2.set_ylabel('Error')

        mechanism_animation = animation.FuncAnimation(fig, update_animation, frames=len(solved_points), interval=20)

        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", "mechanism.gif")
        mechanism_animation.save(downloads_path, writer=animation.PillowWriter(fps=10))
        st.image(downloads_path, use_container_width=True)
        



#if __name__ == "__main__":
    #visualiser = Visualiser("4 Punkt")
    #visualiser.draw_mechanism()


        


        
    
