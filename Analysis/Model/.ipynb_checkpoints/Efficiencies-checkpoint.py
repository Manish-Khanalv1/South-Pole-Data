#impoting necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os
import urllib.request
import random

# where you want the data to be taken from and where you want to plots to go
InputPath = '../../DataFolder'
OutputPath = 'PlotsFolder/'

#Take input for year(YY) and day of year(DDD)
input_1  = input("Enter the last two digit of the year: ")
input_2  = input("Enter the day of year in format (DDD): ")

baseurl = 'https://gml.noaa.gov/aftp/data/radiation/baseline/spo'
year = input_1 # last two digits of the year (from input_1)

Area = 2.0 #m**2


# -----------------NOAA-----------------------------------
NOAA = [] #list to hold dataframes
for i in [ int(input_2) - 1, int(input_2)]: #previous day and current day to match the NZDT time and GMT time
    iid = '{0:03d}'.format(i) #format day of year to 3 digits (if Jan 1st, it should be 001, and so on)
    filename = f'{baseurl}/20{int(year)}/spo{int(year)}{iid}.dat' #construct the full filename
    print(filename) #print the filename being accessed

    try:
        file = urllib.request.urlopen(filename)
        data = file.read().decode('utf-8').split('\n') #read the file and split into lines
        #convert data to dataframe
        df = pd.DataFrame([row.split() for row in data[2:]])
        # print(dt)
        NOAA.append(df) #append dataframe to list
    except urllib.error.HTTPError:
        print(f"{filename} file not found") #print error if file not found

# print('dir Irradiance data time correction')
'''Direct Irradiance'''
#define the direct irradiance and diffuse irradiance data with time correction for NZDT
NOAAdir_ir_1 = NOAA[0][12]
NOAAdir_ir_2 = NOAA[1][12]
NOAAtemp = NOAA[0][38]
# NOAAtemp = np.where(NOAAtemp == -9999.9, 0, 1)
# print(f'NOAAtemp: {NOAAtemp}')
# print(f'NOAAtemp sum: {np.sum(NOAAtemp)}')
# concatenate the two days data with time correction
NZDTdir_ir= pd.concat([NOAAdir_ir_1.iloc[660:1440], NOAAdir_ir_2.iloc[0:660]], axis = 0)
#convert this to float
NZDTdir_ir = NZDTdir_ir.astype(float)
#remove nan values from NZDTdir_ir 
NZDTdir_ir[NZDTdir_ir == -9999.9] = np.nan
# NZDTdir_ir = np.array([random.randint(950, 1000) for _ in range(1440)]) # Generate a random integer between 950 and 1050
# NZDTdir_ir = NZDTdir_ir.astype(float)
# print(len(NZDTdir_ir))

# print(NZDTdir_ir)

# print('diff Irradiance data time correction')
''' Diffuse irradiance'''
#diffuse irradiance
NOAAdiff_ir_1 = NOAA[0][14]
NOAAdiff_ir_2 = NOAA[1][14]

# concatenate the two days data with time correction
NZDTdiff_ir= pd.concat([NOAAdiff_ir_1.iloc[660:1440], NOAAdiff_ir_2.iloc[0:660]], axis = 0)
NZDTdiff_ir = NZDTdiff_ir.astype(float) #convert this to float

#remove nan values from NZDTdiff_ir 
NZDTdiff_ir[NZDTdiff_ir == -9999.9] = np.nan #remove nan values
# NZDTdiff_ir = np.array([random.randint(250, 350) for _ in range(1440)]) # Generate a random integer between 250 and 400
# NZDTdiff_ir = NZDTdiff_ir.astype(float) #convert this to float

''' Upwelling irradiance'''
#upwelling irradiance
NOAAup_ir_1 = NOAA[0][10] 
NOAAup_ir_2 = NOAA[1][10]
NZDTup_ir= pd.concat([NOAAup_ir_1.iloc[660:1440], NOAAup_ir_2.iloc[0:660]], axis = 0) # concatenate the two days data with time correction
NZDTup_ir = NZDTup_ir.astype(float)
#remove nan values from NZDTup_ir 
NZDTup_ir[NZDTup_ir == -9999.9] = np.nan
# NZDTup_ir = np.array([random.randint(500, 600) for _ in range(1440)]) # Generate a random integer between 50 and 150
# NZDTup_ir = NZDTup_ir.astype(float)

'''Time List'''
# print(NZDTdiff_ir)
# Create a range of timestamps with a frequency of 1 minute ('min')
times_list = pd.date_range("00:00:00", periods=1440, freq="min")

# Format as HH:MM:SS strings
NOAA_time = times_list.strftime("%H:%M:%S").tolist()    
NOAA_time = pd.to_timedelta(pd.Series(NOAA_time))
NOAA_time = NOAA_time.astype(str).str.split().str[-1]

#time list for the device data
times_list_device = pd.date_range("00:00:00", periods=2880, freq="min")

# Format as HH:MM:SS strings
device_time = times_list_device.strftime("%H:%M:%S").tolist()    
device_time = pd.to_timedelta(pd.Series(device_time))
device_time = device_time.astype(str).str.split().str[-1]

# print(NOAA_time[:10],file_103['Time'][:10])
#Calculate the solar angle for the given day of the year, this is from the solar angle formula

'''This can be shortened, need to verify the formula first'''
solar_angle =  [np.cos(np.radians(-23.44*np.cos(np.radians(360*((x/1440)+182+int(input_2))+10)/365)))
             *np.cos(((((x / 1440) + 182+int(input_2))%1)*2*np.pi)) for x in range(1440)] 

solar_angle = np.array(solar_angle) #convert to numpy array
solar_angle101 = np.concatenate((solar_angle[720:1440],solar_angle[0:720]))
solar_angle103  = np.concatenate((solar_angle[360:1440],solar_angle[0:360]))
# ---------------------------------------------------------------


# ------SIMULATED-POWER------------------------
def simulated_power(angle,dir, diff, up):
     
     eff_dir = 0.15  # Assume 15% efficiency
     eff_diff = 0.05  # Assume 5% efficiency for diffuse
     eff_upwelling = 0.08   # Assume 8% efficiency for upwelling
     eff_back = 0.70  # Assume 70% efficiency for back side
     area = 2.0  # Assume 2 square meter panel

    # eff_dir = efficiencies['dir']
    # eff_diff = efficiencies['diff']
    # eff_upwelling = efficiencies['upwelling']
    

    
     eff_ir_towards = (abs(angle)*eff_dir*dir + diff*eff_diff + up*eff_upwelling)*area
     eff_ir_away = (diff*eff_diff + up*eff_upwelling)*area
     
     power = []
     
     #  zip() to loop through the pre-calculated arrays step-by-step
     for a, ir_towards, ir_away in zip(angle, eff_ir_towards, eff_ir_away):
        if a < 0:
            # Sun hits BACK side.
            # Back gets the ir_towards and scaled by eff_back
            p_instant = np.clip((ir_towards * eff_back),0,262) + np.clip((ir_away),0,145)
        else:
            # Sun hits FRONT side.
            # Front gets ir_towards
            p_instant = np.clip((ir_towards),0,375) + np.clip((ir_away * eff_back),0,112)
            
        power.append(p_instant)
        
     return power
# --------------------------------------------

# --------REAL PANEL DATA-------------
#Read the CSV files based on user input
file_101 = pd.read_csv(f"{InputPath}/spo_dev101_{input_1}_{input_2}.csv",delimiter=',')
file_103 = pd.read_csv(f"{InputPath}/spo_dev103_{input_1}_{input_2}.csv",delimiter=',')

# Rename the Device ID column to voltage and Voltage to Current
file_101.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True)
file_103.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True) # There is a mismatch in the file so voltage column contains current and Device ID contains voltage

# Each file has the data for more than just the day it is. We want to remove this extra dataS

def date2num(date_str): # Renamed 'date' to 'date_str' to avoid confusion with the datetime.date object
    # 26 # first conver the xxxx-xx-xx format to date(xxxx, xx, xx)

    # You can skip splitting the string and go directly to parsing:
    date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # 29 # return the day of the year (%j) as an integer
    # The strftime method returns a string, so we convert it to an integer.
    return int(date_object.strftime('%j'))
# print(f'DEBUG: {input_2}')
date = file_101['Date']
NumberDate = date.apply(date2num)
mask_to_keep =  NumberDate <= int(input_2)
file_101 = file_101[mask_to_keep]
# print(f'DEBUG: {mask_to_keep}')
# print(f'DEBUG: {NumberDate}')

date = file_103['Date']
NumberDate = date.apply(date2num)
mask_to_keep = NumberDate <= int(input_2)
file_103 = file_103[mask_to_keep]

#Extract time, voltage and current data

time_101 = file_101['Time']
voltage_101 = file_101['V'] 
current_101 = file_101['A'] 

time_103 = file_103['Time']
voltage_103 = file_103['V'] 
current_103 = file_103['A'] 

power_101 = voltage_101 * current_101
power_103 = voltage_103 * current_103
# -----------------------------




# Get simulated power variables
sim_power101 = simulated_power(solar_angle101, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir)
sim_power103 = simulated_power(solar_angle103, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir)

# Solve for the efficiencies

TestTimeHour = str(input('Hour = '))
TestTimeMin = str(input('Min = '))
TestIndex = 60*int(TestTimeHour) + int(TestTimeMin)


# for a given time, and the data around that time.. (for device 101)
# 1. make vector of power outputs
PowerOutputs = np.array([power_101[(TestIndex-30)*2],power_101[TestIndex*2],power_101[(TestIndex+30)*2]])
# 2. Make irradiance matrix
NOAA_irr = np.array([[NZDTdir_ir[TestIndex-30],NZDTdir_ir[TestIndex],NZDTdir_ir[TestIndex+30]],
                    [NZDTdiff_ir[TestIndex-30],NZDTdiff_ir[TestIndex],NZDTdiff_ir[TestIndex+30]],
                    [NZDTup_ir[TestIndex-30],NZDTup_ir[TestIndex],NZDTup_ir[TestIndex+30]]])
# 3. do linear algebra (dir,diff,up)

# How much the output is attenuated by the angle of the sun WRT the solar panel
# solar_angle =  [np.cos(np.radians(-23.44*np.cos(np.radians(360*((x/1440)+182+int(input_2))+10)/365)))
#              *np.cos(((((x / 1440) + 182+int(input_2))%1)*2*np.pi)) for x in range(1440)] 
# solar_angle = np.array(solar_angle) #convert to numpy array
# solar_angle101 = np.concatenate((solar_angle[720:1440],solar_angle[0:720]))


Efficiencies = (((1/Area) * (np.linalg.inv(NOAA_irr) @ PowerOutputs))/solar_angle101[TestIndex])
print(Efficiencies)

plt.figure()
plt.plot(np.linspace(0,1440,1440), solar_angle)
plt.show()
print(solar_angle)
print(NOAA_irr)













