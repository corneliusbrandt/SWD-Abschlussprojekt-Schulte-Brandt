import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class EbeneKinematik:
    def __init__(self, data, step_size=10):	
        """
        Initialisiert das Kinematik-System.
        :param data: Dictionary mit den Schlüsseln 'Punkt', 'X-Koordinate', 'Y-Koordinate', 'statisch', 'Kurbel' und 'Glieder'
        """
        self.data = data
        self.gelenke = np.array([[data['X-Koordinate'][i], data['Y-Koordinate'][i]] for i in range(len(data['Punkt']))], dtype=float)
        print("Gelenk Vektor:\n", self.gelenke)
        self.rotations_Punkt = data['Punkt'][[i for i, (k, s) in enumerate(zip(data['Kurbel'], data['statisch'])) if k and s][0]]
        print("Rotation Point:", self.rotations_Punkt)
        self.fester_punkt = data['Punkt'][[i for i, (k, s) in enumerate(zip(data['Kurbel'], data['statisch'])) if not k and s][0]]
        print("Fester Punkt:", self.fester_punkt)
        self.antrieb = data['Punkt'][[i for i, (k, s) in enumerate(zip(data['Kurbel'], data['statisch'])) if k and not s][0]]
        print("Antrieb:", self.antrieb)
        self.glieder = np.array(data['Glieder'])
        print("Glieder Matrix:\n", self.glieder)
        self.step_size = step_size
        
        self.check_system()

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
        return True
    
    def cal_length(self):
        """
        Berechnet die Längen der Glieder.
        :return: Array mit den Längen der Glieder
        """
        gelenke = self.gelenke[~(np.array(self.data['statisch']) & np.array(self.data['Kurbel']))].reshape(-1, 1)
        print("Gelenke:\n", gelenke)
        L = np.dot(self.glieder, gelenke).reshape(2, 2)
        # print(L)
        l = np.linalg.norm(L, axis=1)
        # print(l)

        return l

    def rotate_Point(self,angle):
        """
        Rotiert den Punkt um den Winkel angle.
        :param angle: Winkel in Grad
        :return: Rotierter Punkt
        """
        angle = np.radians(angle)
        rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        antrieb_koordinate = np.array([self.data['X-Koordinate'][self.data['Punkt'].index(self.antrieb)], self.data['Y-Koordinate'][self.data['Punkt'].index(self.antrieb)]])
        rotations_koordinate = np.array([self.data['X-Koordinate'][self.data['Punkt'].index(self.rotations_Punkt)], self.data['Y-Koordinate'][self.data['Punkt'].index(self.rotations_Punkt)]])
        print("Antrieb Koordinate vor Rotation:", antrieb_koordinate)
        print("Rotations Koordinate:", rotations_koordinate)
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
        print("Initial Length:", initial_length)
        
        def objective_function(free_points):
            self.gelenke[~np.array(self.data['statisch'])] = free_points.reshape(-1, 2)
            lengths = self.cal_length()
            print("Lengths:", lengths)
            error = np.sum((lengths - initial_length) ** 2)
            return error
        
        all_points = []
        
        for angle in range(0, 360, self.step_size):
            rotated_point = self.rotate_Point(angle)
            self.gelenke[[i for i, p in enumerate(self.data['Punkt']) if p == self.antrieb][0]] = rotated_point * 2
            
            free_points_initial = self.gelenke[~np.array(self.data['statisch'])].flatten()
            result = minimize(objective_function, free_points_initial, method='BFGS')
            
            if result.success:
                self.gelenke[~np.array(self.data['statisch'])] = result.x.reshape(-1, 2)
            else:
                print(f"Optimization failed at angle {angle} degrees.")
            
            all_points.append(self.gelenke.copy())
        
        return np.array(all_points)
      
    
    def visualize(self):
        fig, ax = plt.subplots()
        ax.set_xlim(-50, 50)
        ax.set_ylim(-50, 50)
        lines, = ax.plot([], [], 'o-', lw=2)

        def init():
            lines.set_data([], [])
            return lines,

        def update(frame):
            all_points = self.solve()
            x_data = all_points[frame][:, 0]
            y_data = all_points[frame][:, 1]
            lines.set_data(x_data, y_data)
            return lines,

        ani = animation.FuncAnimation(fig, update, frames=len(range(0, 360, self.step_size)), init_func=init, blit=True)
        plt.show()

data = {
    'Punkt': ['A', 'B', 'C', 'D'],
    'X-Koordinate': [0, 10, -25, -30],
    'Y-Koordinate': [0, 35, 10, 0],
    'statisch': [True, False, False, True],
    'Kurbel': [False, False, True, True],
    'Glieder': [[1,  0, -1,  0,  0,  0], [0,  1,  0, -1,  0,  0], [0,  0,  1,  0, -1,  0], [0,  0,  0,  1,  0, -1]]
}

# Initialize the kinematics system
kinematik = EbeneKinematik(data)

# Check if the system is valid
if kinematik.check_system():
    print("System is valid.")
else:
    print("System is invalid.")

# Calculate the lengths of the links
kinematik.cal_length()

# Solve the kinematic system
kinematik.solve()

# Visualize the kinematic system
kinematik.visualize()