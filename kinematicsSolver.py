import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class EbeneKinematik:
    def __init__(self, data_gelenke, data_glieder, step_size=1, temp=False):	
        """
        Initialisiert das Kinematik-System.
        :param data_gelenke: Dictionary mit den Schlüsseln 'Punkt', 'X-Koordinate', 'Y-Koordinate', 'Statisch', 'Kurbel'
        :param data_glieder: Dictionary mit dem Schlüssel 'Glieder'
        :param step_size: Schrittweite in Grad
        """
        if not temp:
            self.check_input(data_gelenke, data_glieder)
        
        self.data_gelenke = data_gelenke
        

        self.gelenke = np.array([[data_gelenke['x-Koordinate'][i], data_gelenke['y-Koordinate'][i]] for i in range(len(data_gelenke['Punkt']))], dtype=float)
        # print("Gelenk Vektor:\n", self.gelenke)

        rotation_point = [i for i, (k, s) in enumerate(zip(data_gelenke['Kurbel'], data_gelenke['Statisch'])) if k and s]
        # print("Rotation Point Index:", rotation_point)
        self.rotations_Punkt = data_gelenke['Punkt'][rotation_point[0]]
        # print("Rotation Point:", self.rotations_Punkt)

        
        
        self.fester_punkt = data_gelenke['Punkt'][[i for i, (k, s) in enumerate(zip(data_gelenke['Kurbel'], data_gelenke['Statisch'])) if not k and s][0]]
        # print("Fester Punkt:", self.fester_punkt)
        # print("Data Type Fester Punkt:", type(self.fester_punkt))

        self.antrieb = data_gelenke['Punkt'][[i for i, (k, s) in enumerate(zip(data_gelenke['Kurbel'], data_gelenke['Statisch'])) if k and not s][0]]
        # print("Antrieb:", self.antrieb)

        self.step_size = step_size

        self.solved_points = None
        self.erros = None
        data_glieder = {"Glieder": np.array(list(data_glieder.values()))}
        self.data_glieder = data_glieder
        rotation_index = data_gelenke['Punkt'].index(self.rotations_Punkt)
        self.data_glieder['Glieder'] = np.delete(self.data_glieder['Glieder'], rotation_index, axis=0)
        self.data_glieder['Glieder'] = np.delete(self.data_glieder['Glieder'], rotation_index, axis=1)
        self.glieder = np.array(data_glieder['Glieder'])
        self.create_glieder()

        if not temp:
            self.check_system()

    def check_input(self, data_gelenke, data_glieder):
        """
        Überprüft, ob die Eingabedaten gültig sind.
        :param data_gelenke: Dictionary mit den Schlüsseln 'Punkt', 'x-Koordinate', 'y-Koordinate', 'Statisch', 'Kurbel'
        :param data_glieder: Dictionary mit dem Schlüssel 'Glieder'
        :return: True, wenn die Eingabedaten gültig sind, sonst False
        """
        if not isinstance(data_gelenke, dict):
            raise TypeError("data_gelenke must be a dictionary.")
        if not isinstance(data_glieder, dict):
            raise TypeError("data_glieder must be a dictionary.")
        if 'Punkt' not in data_gelenke or 'x-Koordinate' not in data_gelenke or 'y-Koordinate' not in data_gelenke or 'Statisch' not in data_gelenke or 'Kurbel' not in data_gelenke:
            raise ValueError("data_gelenke must contain the keys 'Punkt', 'x-Koordinate', 'y-Koordinate', 'Statisch', and 'Kurbel'.")
        if not data_glieder:
            raise ValueError("data_glieder must not be empty.")
        if not data_gelenke:
            raise ValueError("data_gelenke must not be empty.")
        if not any(data_gelenke['Kurbel']):
            raise ValueError("Es muss mindestens einen Punkt geben, der 'Kurbel' ist.")
        if not any(data_gelenke['Statisch']):
            raise ValueError("Es muss mindestens einen Punkt geben, der 'Statisch' ist.")
        if not any(k and not s for k, s in zip(data_gelenke['Kurbel'], data_gelenke['Statisch'])):
            raise ValueError("Es muss mindestens einen Punkt geben, der 'Kurbel' ist und nicht 'Statisch'.")
        if not any(not k and s for k, s in zip(data_gelenke['Kurbel'], data_gelenke['Statisch'])):
            raise ValueError("Es muss mindestens einen Punkt geben, der 'Statisch' ist und nicht 'Kurbel'.")
        if len(data_gelenke['Punkt']) != len(data_gelenke['x-Koordinate']) or len(data_gelenke['Punkt']) != len(data_gelenke['y-Koordinate']) or len(data_gelenke['Punkt']) != len(data_gelenke['Statisch']) or len(data_gelenke['Punkt']) != len(data_gelenke['Kurbel']):
            raise ValueError("The lengths of the lists in data_gelenke must be equal.")
        if not any(k and s for k, s in zip(data_gelenke['Kurbel'], data_gelenke['Statisch'])):
            raise ValueError("Es muss mindestens einen Punkt geben, der sowohl 'Kurbel' als auch 'Statisch' ist.")
        
        return True

    
    def check_system(self):
        """
        Überprüft, ob das System gültig ist.
        :return: True, wenn das System gültig ist, sonst False
        """
        if len(self.fester_punkt) > 1 or len(self.fester_punkt) < 1:
            raise ValueError("Es darf nur ein fester Punkt existieren.")
        if len(self.antrieb) > 1 or len(self.antrieb) < 1:
            raise ValueError("Es darf nur ein Antrieb existieren.") 
        if self.antrieb == self.fester_punkt:
            raise ValueError("Der feste Punkt und der Antrieb dürfen nicht identisch sein.")
        if not self.rotations_Punkt:
            raise ValueError("Es muss mindestens einen Rotationspunkt geben.")
        if len(self.glieder)/2 > self.calc_constraints():               # /2 weil die Glieder Matrix doppelt so viele Zeilen hat wie die Anzahl der Glieder
            raise ValueError("Das System ist überbestimmt.")
        if len(self.glieder)/2 < self.calc_constraints():
            raise ValueError("Das System ist unterbestimmt.")
        if len(self.glieder)/2 == 0:
            raise ValueError("Das System ist nicht vollständig.")

        
        
        return True
    
    def calc_constraints(self):
        n = len(self.data_gelenke['Punkt']) - 1#damit der Rotationspunkt nicht mitgezählt wird
        # print("n",n)
        benötigte_glieder = n * 2 - 4
        # print("benötigte_glieder",benötigte_glieder)
        return benötigte_glieder

    
    def create_glieder(self):
        """
        Erstellt die Glieder-Matrix basierend auf den Verbindungen zwischen den Punkten.
        :return: None
        """
        # print("Data Glieder:\n", self.data_glieder)
        data = np.array(self.data_glieder['Glieder'], dtype=int)
        # print("Data:\n", data)
        num_points = len(data)
        connections = []
        
        # Identify connections from the input matrix
        for i in range(num_points):
            for j in range(num_points):
                if data[i][j] == 1:
                    connections.append((i, j))
        
        num_connections = len(connections)
        output_matrix = np.zeros((num_connections * 2, num_points * 2))
        
        for idx, (start, end) in enumerate(connections):
            row_x = idx * 2
            row_y = row_x + 1
            output_matrix[row_x][start * 2] = 1  # x start
            output_matrix[row_x][end * 2] = -1   # x end
            output_matrix[row_y][start * 2 + 1] = 1  # y start
            output_matrix[row_y][end * 2 + 1] = -1   # y end
    
        self.glieder = output_matrix

    
    def cal_length(self, gelenke=None):
        """
        Berechnet die Längen der Glieder.
        :return: Array mit den Längen der Glieder
        """
        if gelenke is None:
            gelenke = self.gelenke[~(np.array(self.data_gelenke['Statisch']) & np.array(self.data_gelenke['Kurbel']))].reshape(-1, 1)
        else:
            gelenke = gelenke[~(np.array(self.data_gelenke['Statisch']) & np.array(self.data_gelenke['Kurbel']))].reshape(-1, 1)
            # print("Gelenke von Optimise:\n", gelenke)
        # print("Gelenke (cal_length):\n", gelenke)
        # print("Glieder:\n", self.glieder)
        L_matrix = np.dot(self.glieder, gelenke)
        # print("L\n",L_matrix)
        # print("len",len(self.glieder))
        # print("len reshape",len(self.glieder) // 2)
        len_reshape = len(self.glieder) // 2
        L_matrix = L_matrix.reshape(len_reshape, 2)
        # print("L Reshape\n",L_matrix)
        l = np.linalg.norm(L_matrix, axis=1)
        # print("l",l)

        return l

    def rotate_Point(self,angle):
        """
        Rotiert den Punkt um den Winkel angle.
        :param angle: Winkel in Grad
        :return: Rotierter Punkt
        """
        angle = np.radians(angle)
        rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        antrieb_koordinate = np.array([self.data_gelenke['x-Koordinate'][self.data_gelenke['Punkt'].index(self.antrieb)], self.data_gelenke['y-Koordinate'][self.data_gelenke['Punkt'].index(self.antrieb)]])
        rotations_koordinate = np.array([self.data_gelenke['x-Koordinate'][self.data_gelenke['Punkt'].index(self.rotations_Punkt)], self.data_gelenke['y-Koordinate'][self.data_gelenke['Punkt'].index(self.rotations_Punkt)]])
        # print("Antrieb Koordinate vor Rotation:", antrieb_koordinate)
        # print("Rotations Koordinate:", rotations_koordinate)
        translated_point = antrieb_koordinate - rotations_koordinate
        rotated_point = np.dot(rotation_matrix, translated_point) + rotations_koordinate
        return rotated_point
    
    def solve(self):
        """
        Löst das Kinematik-System, indem der Antriebspunkt von 0 bis 360 Grad in einem gegebenen Intervall rotiert wird.
        :param step_size: Schrittweite in Grad
        :return: Array mit allen Punkten für jeden Winkel
        """
        initial_length = self.cal_length()
        gelenke = self.gelenke
        # print("Initial Length:", initial_length)
        
        def objective_function(free_points):
            # Update the positions of the free points in the gelenke array
            gelenke[~(np.array(self.data_gelenke['Statisch']) | np.array(self.data_gelenke['Kurbel']))] = free_points.reshape(-1, 2)
            lengths = self.cal_length(gelenke)
            # print("Lengths:", lengths)
            # print("Lengths:", lengths)
            # print("Initial Length:", initial_length)
            error = np.sum((lengths - initial_length) ** 2)
            # print("Error:", error)
            return error
        
        all_points = []
        errors = []
        
        for angle in range(0, 360, self.step_size):
            rotated_point = self.rotate_Point(angle)
            gelenke[[i for i, p in enumerate(self.data_gelenke['Punkt']) if p == self.antrieb][0]] = rotated_point
            
            free_points_initial = gelenke[~(np.array(self.data_gelenke['Statisch']) | np.array(self.data_gelenke['Kurbel']))].flatten()
            result = minimize(objective_function, free_points_initial, tol=0.05)
            
            if result.success:
                self.gelenke[~(np.array(self.data_gelenke['Statisch']) | np.array(self.data_gelenke['Kurbel']))] = result.x.reshape(-1, 2)
            else:
                print(f"Optimization failed at angle {angle} degrees.")
            
            all_points.append(self.gelenke.copy())
            errors.append(objective_function(result.x))
        
        # print("All Points:\n", all_points)
        self.solved_points = []
        for points in all_points:
            step_dict = {
            'Punkt': self.data_gelenke['Punkt'],
            'x-Koordinate': points[:, 0].tolist(),
            'y-Koordinate': points[:, 1].tolist()
            }
            self.solved_points.append(step_dict)
        
        #print("Errors:", errors)
        
        self.errors = errors
        
        #return np.array(all_points)
    def set_step_size(self, step_size):
        """
        Setzt die Schrittweite.
        :param step_size: Schrittweite in Grad
        :return: None
        """
        self.step_size = step_size
      
    
    # def visualize(self):
    #     fig, ax = plt.subplots()
    #     ax.set_xlim(-50, 50)
    #     ax.set_ylim(-50, 50)
    #     ax.set_aspect('equal', adjustable='box')
    #     lines, = ax.plot([], [], 'o-', lw=2)

    #     # Calculate the radius for the circle
    #     rotation_index = self.data_gelenke['Punkt'].index(self.rotations_Punkt)
    #     antrieb_index = self.data_gelenke['Punkt'].index(self.antrieb)
    #     radius = np.linalg.norm(self.gelenke[rotation_index] - self.gelenke[antrieb_index])

    #     # Add a circle around the rotation point
    #     circle = plt.Circle(self.gelenke[rotation_index], radius, color='r', fill=False)
    #     ax.add_artist(circle)

    #     def init():
    #         lines.set_data([], [])
    #         return lines,

    #     def update(frame):
    #         all_points = self.solve()
    #         x_data = all_points[frame][:, 0]
    #         y_data = all_points[frame][:, 1]
    #         lines.set_data(x_data, y_data)
    #         return lines,

    #     ani = animation.FuncAnimation(fig, update, frames=len(range(0, 360, self.step_size)), init_func=init, blit=True)
    #     plt.show()




# if __name__ == "__main__":
    # data_gelenke = {
    #     'Punkt': ['A', 'B', 'C', 'D', 'E'],
    #     'x-Koordinate': [0, 10, -25, -30, -10],
    #     'y-Koordinate': [0, 35, 10, 0, 20],
    #     'Statisch': [True, False, False, True, False],
    #     'Kurbel': [False, False, True, True, False]
    # }

    # data_glieder = {
    #     'Glieder': [[False, True, False, False], [False, False, True, True], [False, False, False, False],[False, False, False, False]]
    # }
# data_gelenke = {
#     'Punkt': ['1', '2', '3', '4'],
#     'x-Koordinate': [0, 10, -25, -30],
#     'y-Koordinate': [0, 35, 10, 0],
#     'Statisch': [True, False, False, True],
#     'Kurbel': [False, False, True, True]
# }

# data_glieder = {
#     'Glieder': [[False, True, False], [False, False, True], [False, False, False]]
# }

# # Initialize the kinematics system
# kinematik = EbeneKinematik(data_gelenke, data_glieder)

# # Check if the system is valid
# if kinematik.check_system():
#     print("System is valid.")
# else:
#     print("System is invalid.")

# # Calculate the lengths of the links
# kinematik.cal_length()

# # Solve the kinematic system
# kinematik.solve()

# # Visualize the kinematic system
# # kinematik.visualize()