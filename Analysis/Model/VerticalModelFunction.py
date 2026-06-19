import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os
import urllib.request
import random
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from numpy import trapezoid
from scipy.signal import argrelmin
import seaborn as sns
# Global Variables
Area = 2.0 #m**2
baseurl = 'https://gml.noaa.gov/aftp/data/radiation/baseline/spo'
InputPath = '../../DataFolder'
OutputPath = 'PlotsFolder/'
#                      _______________________ 
#             /|       |- - - - - | - - - - -|
#            //|       |- - - - - | - - - - -|
#           // |       |- - - - - | - - - - -|      ❄️
#          /| /|       |- - - - - | - - - - -|
#         //|//| .     |__________|__________|
#        // |/ /       |                     |
#       |/ /| /|      _|_                   _|_
#       | //|/_|_                              .
#       |// /        .          .                 .
#       |/ /   .          ❄️              .
#       | /           .              ❄️
#       |/  .                 .
#       |        ❄️                       ❄️        .
#      _|_            .             .



def sigmoid(x, sharpness, shift):
    return np.array(1 / (1 + np.exp(-(1/sharpness)*(x + shift))))
    
def model(Direct_Irradiance, Diffuse_Irradiance, Upwelling_Irradiance, effs, sharpness, zenith, panel_angle_negative):
    '''
    This function 
    '''
    eff_direct = effs[0]
    # eff_isotropic = effs[1]
    eff_diffuse = effs[1]
    eff_upwelling = effs[2]
    efficiency_back = .7

    time = np.linspace(0,1440,1440)
    
    # The angle the math uses to calculate is not the angle which makes sens for us to define our panel angle as so I correct for it as such
    angle_panel = 360 - panel_angle_negative
    Change_Time_1 = angle_panel/360*1440
    Change_Time_2 = Change_Time_1 + 1440/2
    Angular_Dependance_Front = np.array(np.cos(np.pi/(Change_Time_2 - Change_Time_1)*(time - (Change_Time_1 + Change_Time_2)/2))*np.cos((90-zenith)*np.pi/180))
    Angular_Dependance_Back = np.array(-Angular_Dependance_Front)
            
    # create front of panel simulation (I did tricky math to get these)
    # Directional components:
    Front = eff_direct*Direct_Irradiance*Angular_Dependance_Front*sigmoid(time, sharpness, -Change_Time_1)*sigmoid(-time, sharpness, Change_Time_2)
    Back  = .7*eff_direct*Direct_Irradiance*Angular_Dependance_Back*sigmoid(time, sharpness, -Change_Time_2)*sigmoid(-time, sharpness, 2*Change_Time_2 - Change_Time_1)
    Secondary_Front = eff_direct*Direct_Irradiance*Angular_Dependance_Front*sigmoid(time, sharpness, Change_Time_1 - 2*Change_Time_2)*sigmoid(-time, sharpness, 3*Change_Time_2 - Change_Time_1)
    Secondary_Back = .7*eff_direct*Direct_Irradiance*Angular_Dependance_Back*sigmoid(time, sharpness, Change_Time_2 - 2*Change_Time_1)*sigmoid(-time, sharpness, Change_Time_1)
    Tertiary_Front = eff_direct*Direct_Irradiance*Angular_Dependance_Front*sigmoid(time, sharpness, -Change_Time_1-2*Change_Time_1+2*Change_Time_2)*sigmoid(-time, sharpness, Change_Time_2-(-2*Change_Time_1+2*Change_Time_2))
    Tertiary_Back = .7*eff_direct*Direct_Irradiance*Angular_Dependance_Back*sigmoid(time, sharpness, -Change_Time_2+4*Change_Time_2-4*Change_Time_1)*sigmoid(-time, sharpness, 2*Change_Time_2 - Change_Time_1-(+4*Change_Time_2-4*Change_Time_1))
    # Total_Directional_Irradiance = Front + Back + Secondary_Front + Secondary_Back
    Total_Directional_Irradiance = Front + Back + Secondary_Front + Secondary_Back + Tertiary_Back + Tertiary_Front
           
        
    # add directional to the isotropic components:
    Total_Irradiance = Total_Directional_Irradiance + eff_diffuse*Diffuse_Irradiance + eff_upwelling*Upwelling_Irradiance
            
    # # Multiply by area to get total power
    Total_Power = Total_Irradiance*Area
            
    # constraint of device resistor:
            
    Max_Power = 420
    Total_Power = np.clip(Total_Power, 0, Max_Power)
    return Total_Power

