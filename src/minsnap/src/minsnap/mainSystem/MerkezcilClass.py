#Rahman ve Rahim Olan Allah'ın Adıyla, Hamd Alemlerin Rabb'i Allah'a Mahsustur!!!

import math
import numpy as np
#FOR TRAJECTORY IMPORT
from numpy import linalg as LA
from scipy import optimize
from copy import deepcopy

from State import DesiredTrajectoryState
from utils import Hessian, polyder, normalize, position_to_numpy
import time
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import linear_sum_assignment as hungarian


from Parameters import *
from enums import *



class TrajGenerator:
    def __init__(self , order = 10):
        #Order can not change, for this implementation
        self.waypoints = None
        self.order = order
        self.yaw = 0
        self.heading = np.zeros(2)
        self.trajectory_generated = False
    

    def generate_trajectory_for_path(self,initial_position,waypoints,max_vel,gamma,path_manipulate_coef):
        waypoints.insert(0,initial_position)
        waypoints = position_to_numpy(waypoints)
        self.manipulate_coef = path_manipulate_coef
        self.waypoints = waypoints/self.manipulate_coef #waypoints numpy array
        len,dim = waypoints.shape
        self.dim = dim
        self.len = len
        self.max_vel = max_vel
        self.gamma = gamma
        self.TS = np.zeros(self.len)  #Segment time'lar initialize edildi
        self.optimize() # UPDATE THE COEFFICIENT OF TRAJECTORY, Her cagirilista yeni trajectory olusturur
    #RAHMAN VE RAHIM OLAN ALLAH'ın ADIYLA!

    def generate_trajectory_for_rotate(self,initial_position,waypoints,step_size,max_vel,gamma):
        np.insert(waypoints,0,np.array([initial_position.x,initial_position.y,initial_position.z]))
        #waypoints = position_to_numpy(waypoints)
        self.waypoints = waypoints #waypoints numpy array
        len,dim = waypoints.shape
        self.dim = dim
        self.len = len
        self.max_vel = max_vel
        self.gamma = gamma
        self.TS = np.zeros(self.len)  #Segment time'lar initialize edildi
        self.optimize_for_fixed_time(step_size) # UPDATE THE COEFFICIENT OF TRAJECTORY, Her cagirilista yeni trajectory olusturur

    def generate_trajectory(self,initial_position,waypoints,max_vel,gamma):
        waypoints.insert(0,initial_position)
        waypoints = position_to_numpy(waypoints)
        self.waypoints = waypoints #waypoints numpy array
        len,dim = waypoints.shape
        self.dim = dim
        self.len = len
        self.max_vel = max_vel
        self.gamma = gamma
        self.TS = np.zeros(self.len)  #Segment time'lar initialize edildi
        self.optimize() # UPDATE THE COEFFICIENT OF TRAJECTORY, Her cagirilista yeni trajectory olusturur
    
    def reset(self):
        self.dim = None
        self.len = None
        self.TS = None
        self.waypoints = None
        self.coeffs = None
        self.trajectory_generated = False
    
    def get_cost(self,T):
        coeffs,cost = self.MinimizeSnap(T)
        cost = cost + self.gamma*np.sum(T)
        return cost

    def optimize_for_fixed_time(self,step_size):
        T = np.ones(self.len-1)*(1/step_size)

        self.TS[1:] = np.cumsum(T)
        self.coeffs, self.cost = self.MinimizeSnap(T)

    def optimize(self):
        diff = self.waypoints[0:-1] - self.waypoints[1:]
        Tmin = LA.norm(diff,axis = -1)/self.max_vel #Olabilecek en dusuk hız, bizim verdigimiz max_vel ile belirlenir
        t1 = time.time()
        T = optimize.minimize(self.get_cost,Tmin, method="COBYLA",constraints= ({'type': 'ineq', 'fun': lambda T: T-Tmin}))['x']
        #print("NE KADAR SURDU",time.time()-t1)

        #T'yi optimize etmek icin GAMMA'lı cost isin icine katılarak cost hesaplandı, evet okey

        self.TS[1:] = np.cumsum(T)
        self.coeffs, self.cost = self.MinimizeSnap(T)

    def MinimizeSnap(self,T):
        unkns = 4*(self.len - 2)

        Q = Hessian(T)
        A,B = self.get_constraints(T)

        invA = LA.inv(A)

        if unkns != 0:
            R = invA.T@Q@invA

            Rfp = R[:-unkns,-unkns:]
            Rpp = R[-unkns:,-unkns:]

            B[-unkns:,] = -LA.inv(Rpp)@Rfp.T@B[:-unkns,]

        P = invA@B
        cost = np.trace(P.T@Q@P)

        return P, cost

    def get_constraints(self,T):
        n = self.len - 1
        o = self.order

        A = np.zeros((self.order*n, self.order*n))
        B = np.zeros((self.order*n, self.dim))

        B[:n,:] = self.waypoints[ :-1, : ]
        B[n:2*n,:] = self.waypoints[1: , : ]

        #waypoints contraints
        for i in range(n):
            A[i, o*i : o*(i+1)] = polyder(0, order = self.order)
            A[i + n, o*i : o*(i+1)] = polyder(T[i], order = self.order)

        #continuity contraints
        for i in range(n-1):
            A[2*n + 4*i: 2*n + 4*(i+1), o*i : o*(i+1)] = -polyder(T[i],'all',order = self.order)
            A[2*n + 4*i: 2*n + 4*(i+1), o*(i+1) : o*(i+2)] = polyder(0,'all',order = self.order)

        #start and end at rest
        A[6*n - 4 : 6*n, : o] = polyder(0,'all',order = self.order)
        A[6*n : 6*n + 4, -o : ] = polyder(T[-1],'all',order = self.order)

        #free variables
        for i in range(1,n):
            A[6*n + 4*i : 6*n + 4*(i+1), o*i : o*(i+1)] = polyder(0,'all',order=self.order)

        return A,B

    def get_yaw(self,vel):
        prev_heading = self.heading
        curr_heading = vel/LA.norm(vel)
        cosine = max(-1,min(np.dot(prev_heading, curr_heading),1))
        dyaw = np.arccos(cosine)
        norm_v = np.cross(prev_heading,curr_heading)
        self.yaw += np.sign(norm_v)*dyaw

        if self.yaw > np.pi: self.yaw -= 2*np.pi
        if self.yaw < -np.pi: self.yaw += 2*np.pi

        self.heading = curr_heading
        return self.yaw,dyaw

    def get_des_state(self,t):

        if t > self.TS[-1]: t = self.TS[-1] - 0.001

        i = np.where(t >= self.TS)[0][-1] #Segment selection, assume we have 1 segment!

        t = t - self.TS[i] #For each segment at start t = 0, bu satır bunu saglıyor.
        coeff = (self.coeffs.T)[:,self.order*i:self.order*(i+1)] #Give coefficient
        pos  = coeff@polyder(t,order = self.order)   #Gives pos value at segment time t! not t+dt!
        vel  = coeff@polyder(t,1,order = self.order) #Gives vel value at segment time t! not t+dt!
        accl = coeff@polyder(t,2,order = self.order) #Gives accl value at segment time t! not t+dt!
        jerk = coeff@polyder(t,3,order = self.order) #Gives Jerk value at segment time t! not t+dt! ---> Result: Trajectory'i yanlıs isliyoruz!

        thrust = accl + np.array([0, 0, 9.81]) #Thrust calculation from many paper
        z_body = normalize(thrust) #Drone Body z_body unit vector!
        jerk_orth_zbody = jerk - (np.dot(jerk, z_body) * z_body) #This calculation from paper of Mellinger and Kumar
        h_w = jerk_orth_zbody / np.linalg.norm(thrust) #This calculation from paper of Mellinger and Kumar, pls refer paper and ask question if you want!

        #set yaw in the direction of velocity
        yaw,dyaw = self.get_yaw(vel[:2]) #Get yaw value at segment time t! We can add the yaw controller, yaw---> yaw_rate!

        x_world = np.array([np.cos(yaw), np.sin(yaw), 0])
        y_body = normalize(np.cross(z_body, x_world))
        x_body = np.cross(y_body, z_body)
        omega = np.array([-np.dot(h_w, y_body), np.dot(h_w, x_body), z_body[2] * dyaw]) #In the WORLD FRAME, not body frame. This equation comes from, Mellinger Kumar Paper. Model....
        #Bu omega'nın z'sini body'e cevirebiliriz! Bunun body-z'si + yaw--->yawrate PID olmalı! duzgun kontrol olmazsa! Ama calısması gerek. Position icin de aynı

        return DesiredTrajectoryState(pos, vel, accl, yaw, omega)
  
class TrajectoryExecuter:
    def __init__(self,des_state,Tmax,
                 pos = None,
                 control_frequency = 62):

        self.initial_step_time = 0 #Used for trajectory time calculation elhamdulillah
        self.t = 0
        self.Tmax = Tmax
        self.dt = 1/control_frequency #YANLIS her bir .step() fonksiyonu cagırıldıgında 1/56sn sonraki traj state donuyor. Buraya da bir kontrol mekanizması konulabilir! nerede olduğuna gore!
                                      # Ve bu boyle her step bir sonraki hedef degeri verir ? Belki de initial veriyo.
        self.des_state = des_state
        if pos is None: pos = self.des_state(0).desired_position #initial Position #NOT USED
        end_state = self.des_state(self.Tmax-0.000001) ### ????? Tmax'ta çalışmıyor
        self.end_position = end_state.desired_position
        self.end_yaw = end_state.desired_yaw
        self.traj_completed = False

    #Rahman ve Rahim Olan Allah'ın Adıyla!
    def step(self):
        if self.t == 0:
            self.initial_step_time = time.time() #Inıtıalize time
        
        self.t = time.time()- self.initial_step_time
        print("Passed Time T: ",self.t)
        desired_state = self.des_state(self.t)
        #desired_state.desired_velocity[2] += 0.125 #BUNU MELLINGER KONTROLCU KENDISI EKLIYOR GEREK YOK
        if self.t >= self.Tmax:
            self.traj_completed = True
            return DesiredTrajectoryState(self.end_position,np.array([0,0,0]),np.zeros(3),self.end_yaw,np.zeros(3)),self.traj_completed ### En son gitmesi gereken pozisyonda Hover
        return desired_state,self.traj_completed
