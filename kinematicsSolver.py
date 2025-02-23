import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class EbeneKinematik:
    def __init__(self, data):
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
        gelenke = self.gelenke.reshape(-1, 1)
        print("Gelenke:\n", gelenke)
        L = np.dot(self.glieder, self.gelenke).reshape(2, 2)
        # print(L)
        l = np.linalg.norm(L, axis=1)
        # print(l)

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
    
    def solve(self, step_size):
        """
        Löst das Kinematik-System, indem der Antriebspunkt von 0 bis 360 Grad in einem gegebenen Intervall rotiert wird.
        :param step_size: Schrittweite in Grad
        """
        initial_length = self.cal_length()
        
        def objective_function(free_points):
            self.gelenke[~self.data['statisch']] = free_points.reshape(-1, 2)
            lengths = self.cal_length()
            error = np.sum((lengths - initial_length) ** 2)
            return error
        
        for angle in range(0, 360, step_size):
            rotated_point = self.rotate_Point(angle)
            self.gelenke[[i for i, p in enumerate(self.data['Punkt']) if p == self.antrieb][0]] = rotated_point * 2
            
            free_points_initial = self.gelenke[~self.data['statisch']].flatten()
            result = minimize(objective_function, free_points_initial, method='BFGS')
            
            if result.success:
                self.gelenke[~self.data['statisch']] = result.x.reshape(-1, 2)
            else:
                print(f"Optimization failed at angle {angle} degrees.")
      
    
    def visualize(self):
        """
        Visualisiert das Kinematik-System.
        """
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        
        # Plot points
        for i, punkt in enumerate(self.data['Punkt']):
            ax.plot(self.gelenke[i][0], self.gelenke[i][1], 'o', label=punkt)
            ax.text(self.gelenke[i][0], self.gelenke[i][1], f' {punkt}', fontsize=12)
        
        # Plot links
        for glied in self.glieder:
            start_idx = np.where(glied == 1)[0][0]
            end_idx = np.where(glied == -1)[0][0]
            ax.plot([self.gelenke[start_idx][0], self.gelenke[end_idx][0]], 
                    [self.gelenke[start_idx][1], self.gelenke[end_idx][1]], 'k-')
        
        ax.legend()
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
kinematik.solve(10)

# Visualize the kinematic system
kinematik.visualize()