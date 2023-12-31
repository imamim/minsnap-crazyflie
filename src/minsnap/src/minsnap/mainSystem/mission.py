#!/usr/bin/env python3
#Rahman ve Rahim Olan Allah'ın Adıyla!!! 
#Hamd Alemlerin Rabb'i Allah'a Mahsustur!!# Muvaffakiyetimiz Yalnızca Alemlerin Rabb'i Allah'a AITTIR!


from enums import MISSIONMODES
from Modes import *
from Parameters import *
from State import *
import rospy
import time

#Sıgnal Shutdown icin reason
def reason():
    print("BITTI")

modeList = [
            #TODO Simulation does not work with 1 agent, this mainSystem can work 1 drone but we have problem at simulation. Can't render drone.
            #For information of parameters pls look at Parameters.py
            {MISSIONMODES.initialize  :      InitializerParams(simulation_enabled = True,real_enabled = False, area_dimension = [(-1.6, 1.6), (-1.9, 1.9), (0, 1.5)])},
            
            {MISSIONMODES.take_off    :      TakeoffParams(takeoff_height = 1.0 ,threshold = 0.08)} , 
            {MISSIONMODES.loiter      :      LoiterParams(loiter_time = 5)} ,
            
            #False for Real Flight! True for Simulation
            {MISSIONMODES.navigation  :      NavigationParams(correct_error_with_pid = True ,agressiveness_kt = 50 ,max_velocity = 3, navigation_waypoints = [Position(1,1,1)], threshold = 0.08)},
            {MISSIONMODES.loiter      :      LoiterParams(loiter_time = 3)},
        
            {MISSIONMODES.landing     :      LandingParams(threshold = 0.07)},

            {MISSIONMODES.completed   :      True}
            
            ]

#Initialize ModesClass
start_time = time.time()

#Generate main Modes Class and execute Modes using ModeList
ModeClass = Modes(modeList)
freq = rospy.Rate(60)


while not rospy.is_shutdown():

    #print("MODE",ModeClass.mode)
    time.sleep(0.0001)
    
    if ModeClass.mode == MISSIONMODES.take_off:
        ModeClass.takeOffStep(ModeClass.modeList[ModeClass.modeListIndex].get(ModeClass.mode))

    if ModeClass.mode == MISSIONMODES.loiter:
        ModeClass.loiterStep(ModeClass.modeList[ModeClass.modeListIndex].get(ModeClass.mode))

    if ModeClass.mode == MISSIONMODES.navigation:
        if ModeClass.modeList[ModeClass.modeListIndex].get(ModeClass.mode).correct_error_with_pid == True:
            ModeClass.correctedNavigationStep(ModeClass.modeList[ModeClass.modeListIndex].get(ModeClass.mode))

        elif ModeClass.modeList[ModeClass.modeListIndex].get(ModeClass.mode).correct_error_with_pid == False:
            ModeClass.simpleNavigationStep(ModeClass.modeList[ModeClass.modeListIndex].get(ModeClass.mode))

    if ModeClass.mode == MISSIONMODES.landing:
        ModeClass.landingStep(ModeClass.modeList[ModeClass.modeListIndex].get(ModeClass.mode))

    if ModeClass.mode == MISSIONMODES.completed:
        print("BITTI")
        time.sleep(2)
        rospy.signal_shutdown(reason)

    freq.sleep()
    


