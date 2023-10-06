#Rahman ve Rahim Olan Allah'ın Adıyla

#YAML'dan da alınabilir
from enums import *
from State import *
import numpy as np


class InitializerParams:
    def __init__(self, simulation_enabled, real_enabled, area_dimension):
        self.simulation_enabled = simulation_enabled #True or False
        self.real_enabled = real_enabled #True or False
        self.area_dimensions = np.array(area_dimension) #Flying environment dimension for the Path Planning Search Space [m] = [(xmin,xmax),(ymin,ymax),(zmin,zmax)]


class NavigationParams: 
    def __init__(self, correct_error_with_pid, agressiveness_kt, max_velocity, navigation_waypoints, threshold):
        self.correct_error_with_pid = correct_error_with_pid #For real flight performance this must be equal = FALSE
        self.agressiveness_kt = agressiveness_kt #This is parameter for how the movement of drones aggressive or not! If big, this means more aggresive.
        self.max_velocity = max_velocity #Maximum Velocity of swarm center in m/s, used in trajectory generation constraint. [m/s]
        self.navigation_waypoints = navigation_waypoints #Navigation waypoints in list,which type of this Position() class. [x,y] in [m]
                                                         #Look  at ------> State.py LISTE ICERISINDE POSITION CLASSI OLMALI
        self.threshold = threshold #Threshold for swarm center position. In the meters (distance to desired swarm center position) [m]


class TakeoffParams:
    def __init__(self,takeoff_height,threshold):
        self.takeoff_height = takeoff_height #Takeoff height in meter. [m]
        self.threshold = threshold #Threshold in meters. Remaining Distance [m]


class LandingParams:
    def __init__(self,threshold):
        self.landing_waypoints = {} #Not used Also. This can be used for specific landing location 
        self.threshold = threshold #Threshold in meters. Remaining Distance [m]


class LoiterParams:
    def __init__(self,loiter_time):
        self.loiter_time = loiter_time #Loiter time in seconds. [s]











