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
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

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





# # By guess and check found the shift in the solar angle to match the data
# k1 = 899-25
# solar_angle101_rolled = np.roll(solar_angle101,-k1)
# # circular shift solar_angle101
# k3 =120
# solar_angle103_rolled = np.roll(solar_angle103,-k3)



# SimPower = simulated_power(solar_angle101_rolled, NZDTdir_ir, NZDTdir_ir, NZDTup_ir)

# SimPower = np.repeat(np.array(SimPower),2)
# SimPower = SimPower[:-1]
# print(len(np.arange(0,2879,1)))
# print(len(SimPower))
# print(len(power_101))
# plt.scatter(np.arange(0,2879,1),SimPower, s = 2)
# plt.scatter(np.arange(0,2879,1),power_101, s = 2)
# # plt.scatter(np.arange(0,2879,1),solar_angle101_rolled, s = 2)
# print(len(solar_angle101_rolled))
# plt.show()



# # Get simulated power variables
# sim_power101 = simulated_power(solar_angle101_rolled, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir)
# sim_power103 = simulated_power(solar_angle103_rolled, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir)

# # Solve for the efficiencies

# TestTimeHour = str(input('Hour = '))
# TestTimeMin = str(input('Min = '))
# TestIndex1 = 60*int(TestTimeHour) + int(TestTimeMin)
# TestIndex2 = TestIndex1-10
# TestIndex3 = TestIndex1+10

# # How much the output is attenuated by the angle of the sun WRT the solar panel
# solar_angle =  [np.cos(np.radians(-23.44*np.cos(np.radians(360*((x/1440)+182+int(input_2))+10)/365)))
#              *np.cos(((((x / 1440) + 182+int(input_2))%1)*2*np.pi)) for x in range(1440)] 
# solar_angle = np.array(solar_angle) #convert to numpy array
# solar_angle101 = np.abs(np.concatenate((solar_angle[720:1440],solar_angle[0:720])))









# # for a given time, and the data around that time.. (for device 101)
# # 1. make vector of power outputs
# PowerOutputs = np.array([power_101_rolled[(TestIndex2)*2],power_101_rolled[TestIndex1*2],power_101_rolled[(TestIndex3)*2]])
# # 2. Make irradiance matrix

# NZDTdir_ir_angled1 = NZDTdir_ir[TestIndex1]*solar_angle101_rolled[TestIndex1]
# NZDTdir_ir_angled2 = NZDTdir_ir[TestIndex2]*solar_angle101_rolled[TestIndex2]
# NZDTdir_ir_angled3 = NZDTdir_ir[TestIndex3]*solar_angle101_rolled[TestIndex3]
# print()
# print(f'NZDTdir_ir[TestIndex1]: {NZDTdir_ir[TestIndex1]}')
# print(f'solar_angle_rolled[TestIndex1]: {solar_angle101_rolled[TestIndex1]}')
# print()
# print()
# print(f'NZDTdir_ir[TestIndex2]: {NZDTdir_ir[TestIndex2]}')
# print(f'solar_angle_rolled[TestIndex2]: {solar_angle101_rolled[TestIndex2]}')
# print()
# print(f'NZDTdir_ir[TestIndex3]: {NZDTdir_ir[TestIndex3]}')
# print(f'solar_angle_rolled[TestIndex3]: {solar_angle101_rolled[TestIndex3]}')
# print()
# NOAA_irr = [[NZDTdir_ir_angled2,NZDTdir_ir_angled1,NZDTdir_ir_angled3],
# [NZDTdiff_ir[TestIndex2],NZDTdiff_ir[TestIndex1],NZDTdiff_ir[TestIndex3]],
# [NZDTup_ir[TestIndex2],NZDTup_ir[TestIndex1],NZDTup_ir[TestIndex3]]]
# # 3. do linear algebra (dir,diff,up)
# print(f'solar_angle: {solar_angle}')
# print(f'NOAA_irr: {NOAA_irr}')

# Efficiencies = (((1/Area) * (np.linalg.inv(NOAA_irr) @ PowerOutputs)))
# print()
# print(f'Effs: {Efficiencies}')
# print()
# # Printing


# # plt.figure()
# # plt.plot(np.linspace(0,1440,1440), solar_angle)
# # plt.show()











# def simulated_power_model(time_index, eff_dir, eff_diff, eff_upwelling):
     
#      # InputVariables = (angle,dir, diff, up)
#      # angle = InputVariables[0]
#      # dir = InputVariables[1]
#      # diff = InputVariables[2]
#      # up = InputVariables[3]

     
#      dir = NZDTdir_ir
#      diff = NZDTdiff_ir
#      up = NZDTup_ir
#      # but these are too short, by half because we have higher data taking frequency, so we can repete each vlue
#      # print(f'len(dir) = {len(dir)}')
#      # dir = np.repeat(np.array(dir), 2)
#      # diff = np.repeat(np.array(diff), 2)
#      # up = np.repeat(np.array(up), 2)
#      # print(f'len(dir) = {len(dir)}')
     
     
#      # eff_dir = 0.15  # Assume 15% efficiency
#      # eff_diff = 0.05  # Assume 5% efficiency for diffuse
#      # eff_upwelling = 0.08   # Assume 8% efficiency for upwelling
#      eff_back = 0.70  # Assume 70% efficiency for back side
#      area = 2.0  # Assume 2 square meter panel

#     # eff_dir = efficiencies['dir']
#     # eff_diff = efficiencies['diff']
#     # eff_upwelling = efficiencies['upwelling']
#      solar_angle =  [np.cos(np.radians(-23.44*np.cos(np.radians(360*((x/len(time_index))+182+int(input_2))+10)/365)))
#              *np.cos(((((x / len(time_index)) + 182+int(input_2))%1)*2*np.pi)) for x in time_index] 
#      solar_angle = np.array(solar_angle) #convert to numpy array
#      solar_angle101 = np.abs(np.concatenate((solar_angle[720:1440],solar_angle[0:720])))
#      angle = solar_angle101
#      print(len(angle), len(dir))
#      eff_ir_towards = (abs(angle)*eff_dir*dir + diff*eff_diff + up*eff_upwelling)*area
#      eff_ir_away = (diff*eff_diff + up*eff_upwelling)*area
     
#      power = []
#      # solar_angle_instance = solar_angle[time_index]
#      # eff_ir_towards_instance = eff_ir_towards[time_index]
#      # eff_ir_away_instance = eff_ir_away[time_index]
#      #  zip() to loop through the pre-calculated arrays step-by-step
#      for a, ir_towards, ir_away in zip(angle, eff_ir_towards, eff_ir_away):
#         if a < 0:
#             # Sun hits BACK side.
#             # Back gets the ir_towards and scaled by eff_back
#             p_instant = np.clip((ir_towards * eff_back),0,262) + np.clip((ir_away),0,145)
#         else:
#             # Sun hits FRONT side.
#             # Front gets ir_towards
#             p_instant = np.clip((ir_towards),0,375) + np.clip((ir_away * eff_back),0,112)
            
#         power.append(p_instant)
#      power = np.repeat(np.array(power), 2)   
#      return power






    
# method 2: scipy.optimize curvefit

def simulated_power_eff(angle,dir, diff, up, effs):
     # effs has shape (eff_dir,eff_dif,eff_upwelling)
     eff_dir = effs[0]  # Assume 15% efficiency
     eff_diff = effs[1]  # Assume 5% efficiency for diffuse
     eff_upwelling = effs[2]   # Assume 8% efficiency for upwelling
     eff_back = 0.70  # Assume 70% efficiency for back side
     area = 2.0  # Assume 2 square meter panel

    # eff_dir = efficiencies['dir']
    # eff_diff = efficiencies['diff']
    # eff_upwelling = efficiencies['upwelling']
    
     
     
     eff_ir_towards = (abs(angle)*eff_dir*dir + diff*eff_diff + up*eff_upwelling)*area
     eff_ir_away = (diff*eff_diff + up*eff_upwelling)*area
     
     power = []

     FrontClip = np.max(power_101)
     BackClip = FrontClip

    
     #  zip() to loop through the pre-calculated arrays step-by-step
     for a, ir_towards, ir_away in zip(angle, eff_ir_towards, eff_ir_away):
        if a < 0:
            # Sun hits BACK side.
            # Back gets the ir_towards and scaled by eff_back
            p_instant = np.clip((ir_towards * eff_back),0,BackClip) + np.clip((ir_away),0,145)
        else:
            # Sun hits FRONT side.
            # Front gets ir_towards
            p_instant = np.clip((ir_towards),0,FrontClip) + np.clip((ir_away * eff_back),0,112)
            
        power.append(p_instant)

     # compute for each induvidual power without efficiency
     PowerDir = abs(angle)*dir*area
     PowerDiff = diff*area*2
     PowerUpwelling = up*area*2
     # for a, PowerSepTowards, PowerSepAway in zip(angle, )
        
     return power, (PowerDir,PowerDiff,PowerUpwelling)



def Sim(time, eff_dir,eff_diff, eff_upwelling):
    # eff_diff = .05
    effs = (eff_dir, eff_diff, eff_upwelling)

    # circular shift solar_angle101
    k = 70
    solar_angle101_rolled = np.roll(solar_angle101,-k)

    sim_power101, PowerTuple = simulated_power_eff(solar_angle101_rolled, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir, effs)
    sim_power101 = np.repeat(sim_power101,2)
    # sim_power101 = np.where(sim_power101 = )
    time_range = np.arange(0,2880, 1)
    fit_power = interp1d(time_range, sim_power101, kind = 'nearest')
    # return sim_power101[:-1]
    return fit_power(time)


# Try using lmfit
from lmfit import Model
mod = Model(Sim)

params = mod.make_params([.15,.05,.08])

params['eff_dir'].set(min=0, max=.25)     
params['eff_diff'].set(min=0,max=.25)
params['eff_upwelling'].set(min=0, max=.25) 


x = np.arange(0,2879,1)
y = power_101
result = mod.fit(y, params, time=x, method='nelder', nan_policy = 'omit')

# Print a comprehensive report of the results
print(result.fit_report())

# Access the best-fit values
# print(f"Best Amplitude: {result.params['eff_dir'].value}")


fitted_dir_eff = result.params['eff_dir'].value
fitted_diff_eff = result.params['eff_diff'].value
fitted_upwelling_eff = result.params['eff_upwelling'].value





SimPower = Sim(np.arange(0,2879,1), fitted_dir_eff,fitted_diff_eff, fitted_upwelling_eff)


PowersOnPlots = 1 # Put the 3 different components of power on the plot

if PowersOnPlots:
    # Get the power tuple
    effs = [fitted_dir_eff, fitted_diff_eff, fitted_upwelling_eff]
    # circular shift solar_angle101
    k = 70
    solar_angle101_rolled = np.roll(solar_angle101,-k)
    _______, PowerTuple = simulated_power_eff(solar_angle101_rolled, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir, effs)
    
    # Make the right size for plotting
    DirPower = np.repeat(PowerTuple[0],2)[:-1]
    DiffPower = np.repeat(PowerTuple[1],2)[:-1]
    UpwellingPower = np.repeat(PowerTuple[2],2)[:-1]


# print(len(SimPower))
# print(len(power_101))
print(time_101)
plt.plot(time_101, SimPower, label = 'Model')
plt.plot(time_101, power_101, label = 'Data')
tick_positions = range(0,len(time_101), 200)
plt.xticks(ticks=tick_positions, labels=[time_101[i] for i in tick_positions], rotation = 45, ha='right', fontsize = 5)
plt.xlabel('Time of Day')
plt.ylabel('Power [Watts]')
plt.title(f'Fit for device 101 on day {input_2}')
plt.legend()
plt.text(1000, 250, f'Direct: {np.round(fitted_dir_eff, 2)}')
plt.text(1000, 225, f'Diffuse: {np.round(fitted_diff_eff, 2)}')
plt.text(1000, 200, f'Upwelling: {np.round(fitted_upwelling_eff, 2)}')
plt.show()


if PowersOnPlots:
    plt.plot(time_101, DirPower, label = 'Direct Power', color = 'black', ls = '-')
    plt.plot(time_101, DiffPower, label = 'Diffuse Power', color = 'black', ls = '--')
    plt.plot(time_101, UpwellingPower, label = 'Upwelling Power', color = 'black', ls = ':')
    tick_positions = range(0,len(time_101), 200)
    plt.xticks(ticks=tick_positions, labels=[time_101[i] for i in tick_positions], rotation = 45, ha='right', fontsize = 5)
    plt.xlabel('Time of Day')
    plt.ylabel('Power [Watts]')
    plt.title(f'Power Components for day {input_2}')
    plt.legend()
    plt.show()












# # effs = (.25, .05, .08)
# # sim_power101 = simulated_power_eff(solar_angle101, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir, effs)
# # sim_power101 = np.repeat(sim_power101,2)
# # time_range = np.linspace(0,2880, 2880)
# # # print(len(time_range))
# # # print(len(sim_power101))
# # fit_linear = interp1d(time_range, sim_power101)
# # plt.plot(time_range, fit_linear(time_range))
# # plt.show()



# # def SimPower(time_index, eff_dir, eff_diff, eff_upwelling):
# #     solar_angle =  [np.cos(np.radians(-23.44*np.cos(np.radians(360*((time_index/2880+182+int(input_2))+10)/365)))
# #              *np.cos(((((time_index / len(time_index)) + 182+int(input_2))%1)*2*np.pi))
# #     dir = NZDTdir_ir
# #     diff = NZDTdiff_ir
# #     up = NZDTup_ir

    

# time_101 = np.array(time_101)
# power_101 = np.array(power_101)

# # time_101 needs to be in the form of number of 30s intervals past midnight: code taken from chatGPT to do this
# def intervals_30s(time_str):
#     h, m, s = map(int, time_str.split(':'))
#     seconds = h*3600 + m*60 + s
#     return seconds // 30   # integer number of 30s intervals

# # time_101_30sPast00 = [intervals_30s(t) for t in time_101]
# time_101_30sPast00 = np.linspace(0,2878, 2879, dtype = int)
# # make time and power len 2880
# # time_101_30sPast00 = np.append(time_101_30sPast00, 2880)
# # power_101 = np.append(power_101, 0)
# print(f'This: {len(time_101_30sPast00)}')
# # curve fit:
# # effs, covs = curve_fit(Sim, time_101_30sPast00, power_101, p0 = [.15,.08], nan_policy = 'omit')

# print(effs)


# # print(len(simulated_power_model(time_101_30sPast00, .1,.1,.1)))
# # print(len(time_101_30sPast00))
# # print(time_101_30sPast00)
# # print(len(power_101))
# # print(power_101)
# # print(len(time_101))

# # print(f'Time len: {len(time_101_30sPast00)}')
# # # print(f'Power len: {len(simulated_power_model(time_101_30sPast00, .15, .05, .08))}')
# # plt.scatter(time_101_30sPast00, simulated_power_model(time_101_30sPast00, .15, .05, .08), s = 2)
# # plt.scatter(time_101_30sPast00, power_101, s = 2)
# # plt.show()
# # plt.scatter(time_101_30sPast00, simulated_power_model(time_101_30sPast00, .1, .1, .1), s = 2)
# # plt.scatter(time_101_30sPast00, power_101, s = 2)
# # plt.show()


# # print(time_101_30sPast00)
