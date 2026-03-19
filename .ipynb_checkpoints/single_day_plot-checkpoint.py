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
InputPath = 'DataFolder'
OutputPath = 'PlotsFolder/Test'

#Take input for year(YY) and day of year(DDD)
input_1  = input("Enter the last two digit of the year: ")
input_2  = input("Enter the day of year in format (DDD): ")

'''NOAA Solar Radiation Data Download and Processing
Construct the base URL for NOAA data'''


baseurl = 'https://gml.noaa.gov/aftp/data/radiation/baseline/spo'
year = input_1 # last two digits of the year (from input_1)


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
print(f'NOAAtemp: {NOAAtemp}')
print(f'NOAAtemp sum: {np.sum(NOAAtemp)}')
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

'''Simulated Power Calculation
A simple model to simulate power based on solar angle and irradiance
This need to be verified and improved, I have made some assumptions here about efficiency, and the formula is very basic'''
def simulated_power(angle,dir, diff, up):
     
     eff_dir = 0.25  # Assume 15% efficiency
     eff_diff = 0.05  # Assume 5% efficiency for diffuse
     eff_upwelling = 0.08   # Assume 8% efficiency for upwelling
     eff_back = 0.70  # Assume 70% efficiency for back side
     area = 2.0  # Assume 2 square meter panel
     
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


# print(simulated_power(solar_angle, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir))
# plt.plot(NOAA_time,simulated_power(solar_angle, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir), label='Simulated Power', color='purple')
# plt.show()
# '''
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

sim_power101 = simulated_power(solar_angle101, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir)
sim_power103 = simulated_power(solar_angle103, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir)

#print to only 2 decimal places
# print('--- Actual Power Statistics ---')
# print(f"Average Power 101: {np.mean(power_101):.2f} W")
# print(f"Average Power 103: {np.mean(power_103):.2f} W")
# print(f"Max Power 101: {np.max(power_101):.2f} W, min: {np.min(power_101):.2f} W")
# print(f"Max Power 103: {np.max(power_103):.2f} W, min: {np.min(power_103):.2f} W")
# print('--- Simulated Power Statistics ---')
# print(f"Average Simulated Power 101: {np.nanmean(sim_power101):.2f} W")
# print(f"Average Simulated Power 103: {np.nanmean(sim_power103):.2f} W")
# print(f"Max Simulated Power 101: {np.nanmax(sim_power101):.2f} W, min: {np.nanmin(sim_power101):.2f} W")
# print(f"Max Simulated Power 103: {np.nanmax(sim_power103):.2f} W, min: {np.nanmin(sim_power103):.2f} W")

# The format should be:
# Device | Avg | Min | Max |
# 101 | ... | ...| ...|
# 103 | ...| ...| ... |
print()
print()
print(f'   DAY: {input_2}')
print()
print('   OBSERVED                     [WATTS]')
print('   ------------------------------------')
print(f'   Device |   Avg  |   Min  |   Max  |')
print(f'     101  | {np.mean(power_101):.2f} |  {np.min(power_101):.2f} | {np.max(power_101):.2f} |')
print(f'     103  | {np.mean(power_103):.2f} |  {np.min(power_103):.2f} | {np.max(power_103):.2f} |')
print('   ------------------------------------')
print('   MODEL                        [WATTS]')
print('   ------------------------------------')
print(f'   Device |   Avg  |   Min   |   Max  |')
print(f'     101  | {np.nanmean(sim_power101):.2f} |  {np.nanmin(sim_power101):.2f} | {np.nanmax(sim_power101):.2f} |')
print(f'     103  | {np.nanmean(sim_power103):.2f} |  {np.nanmin(sim_power103):.2f} | {np.nanmax(sim_power103):.2f} |')
print('   ------------------------------------')
print()
print()



#Create a figure and axis objects
kwargs_101 = {'marker' : 'o', 's' : 3}
kwargs_103 = {'marker' : '^', 's' : 3}

# plt.figure(figsize=(12, 6))
# plt.scatter(time_101, voltage_101, label='Device 101 Voltage (V)', color='blue', **kwargs_101)
# plt.scatter(time_101, current_101, label='Device 101 Current (A)', color='red', **kwargs_101)
# plt.scatter(time_103, voltage_103, label='Device 103 Voltage (V)', color='green', **kwargs_103)
# plt.scatter(time_103, current_103, label='Device 103 Current (A)', color='orange', **kwargs_103)
# # print(f"DEBUG: Length of timestamp 101: {len(time_101)}")
# # print(f"DEBUG: Length of timestamp 103: {len(time_103)}")
# plt.title(f'Panels Voltage and Current on Day {input_2} of 20{input_1}')
# plt.xlabel('Time of the Day')
# plt.ylabel('Voltage (V) and Current (A)')
# plt.legend(loc = 'best',markerscale=5)
# plt.grid(True)
# ax = plt.gca()
# start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
# # Select 15 evenly spaced integers across the range
# ax.set_xticks(np.linspace(0, int(end), 12).astype(int))
# #rotate the x axis labels by 45 degrees
# plt.xticks(rotation=45)
# plt.savefig(f"{OutputPath}/spo_dev101_103_{input_1}_{input_2}_plot.png", bbox_inches='tight', dpi=100,facecolor='white')
# plt.show()

'''Multi-panel Plot: Irradiance and Power
Creating a multi-panel plot with irradiance on the top and power on the bottom
'''
# --- Top Panel: Irradiance ---

plt.rcParams['figure.figsize'] = [12, 14]

plt.figure(figsize=(12, 10))
ax1 = plt.subplot(2, 1, 1)
plt.plot(NOAA_time, NZDTdir_ir, label='Direct', color='red',linestyle='--')
plt.plot(NOAA_time, NZDTdiff_ir, label='Diffuse', color='orange')
plt.plot(NOAA_time, NZDTup_ir, label='Upwelling', color='black',linestyle='-.')

# ax2 = ax1.twiny()
# ax2.set_ylabel('Temperature (c)')
print(f'type(NOAA_time): {type(NOAA_time)}')
print(f'type(NOAA_time[30]): {type(NOAA_time[30])})')
print(f'type(NOAAtemp): {type(NOAAtemp)}')
print(f'type(NOAAtemp[30]): {type(NOAAtemp[30])}')
print(f'NOAAtemp[30]: {NOAAtemp[300]}')
# ax2.plot(NOAA_time, NOAAtemp, label='Temp', color='green',linestyle='-.')


# plt.title(f'Solar Irradiance and Panel Power on Day {input_2} of $20{input_1}$', fontsize=30)
plt.title(f'Day {input_2} of $20{input_1}$', fontsize=30)

plt.ylabel('Irradiance W/m^$2$',fontsize=25)
ax = plt.gca()
start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
# Select 15 evenly spaced integers across the range
ax.set_xticks(np.linspace(0, int(end), 12).astype(int))
#rotate the x axis labels by 45 degrees
# plt.xticks(rotation=45)
plt.ylim(0, 1100)
plt.yticks(np.arange(0, 1100, 80))
plt.legend(loc='best', markerscale=2)
plt.grid(True)
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

# --- Bottom Left: Actual Power ---
#set the figure size
ax_left = plt.subplot(2, 2, 3)
plt.scatter(time_101, power_101, label='Device 101', color='blue', **kwargs_101)
plt.scatter(time_103, power_103, label='Device 103', color='green', **kwargs_103)
plt.xlabel('Time of the Day', fontsize = 25)
plt.ylabel('Power [W]', fontsize=25)
# plt.text('02:00:00', 465, 'Observed', horizontalalignment='center', verticalalignment='top', fontsize=15, color='red')
ax = plt.gca()
start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
# Select 15 evenly spaced integers across the range
ax.set_xticks(np.linspace(0, int(end), 12).astype(int))
#rotate the x axis labels by 45 degrees
plt.xticks(rotation=45)
plt.legend(loc='best', markerscale=2)
plt.ylim(0, 480)
plt.yticks(np.arange(0, 481, 40))
plt.grid(True)
plt.xticks(rotation=45,fontsize=10)
plt.yticks(fontsize=10)
# --- Bottom Right: Simulated Power ---
ax_right = plt.subplot(2, 2, 4, sharey=ax_left)
# sim_results = simulated_power(solar_angle, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir)
plt.plot(NOAA_time, sim_power101, label='Simulated 101', color='blue', linestyle='--')
plt.plot(NOAA_time, sim_power103, label='Simulated 103', color='green')
plt.xlabel('Time of the Day')
ax = plt.gca()
start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
# Select 15 evenly spaced integers across the range
ax.set_xticks(np.linspace(0, int(end), 12).astype(int))

#rotate the x axis labels by 45 degrees
plt.xticks(rotation=45)
plt.legend(loc='best')
plt.ylim(0, 550)
plt.grid(True)
plt.xticks(rotation=45)
plt.setp(ax_right.get_yticklabels(), visible=False)
plt.text('02:00:00', 465, 'Simulated', horizontalalignment='center', verticalalignment='top', fontsize=15, color='red')
# plt.text('23:30:00', 490, f'Avg 101: {np.nanmean(sim_power101):.2f} Avg 103: {np.nanmean(sim_power103):.2f}', horizontalalignment='right', 
#          verticalalignment='bottom', fontsize=10, color='black')
ax_right.set_ylabel('')
# Global layout adjustments
plt.tight_layout()
plt.subplots_adjust(wspace=0)





# plt.savefig(f"{OutputPath}/irradiance_power_only_{input_1}_{input_2}_plot.png", 
#             bbox_inches='tight', 
#             dpi=100, 
#             facecolor='white')

plt.savefig(f"{OutputPath}/irradiance_power_and_device_{input_1}_{input_2}_plot.png", 
            bbox_inches='tight', 
            dpi=100, 
            facecolor='white')

# plt.show()


'''
Nothing below this is needed, kept for reference
'''
# Save the multi-panel figure
# plt.savefig(f"{OutputPath}/power_irradiance_combined_{input_1}_{input_2}_plot.png", 
#             bbox_inches='tight', 
#             dpi=100, 
#             facecolor='white')
# plt.scatter(NOAA_time, NZDTdir_ir, label='NOAA Direct Irradiance', color='red', **kwargs_101)
# ax = plt.gca()
# start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
# # Select 15 evenly spaced integers across the range
# ax.set_xticks(np.linspace(0, int(end), 17).astype(int))
# ax.set_yticks(np.arange(0, 1100, 50))
# #rotate the x axis labels by 45 degrees
# plt.xticks(rotation=45)
# plt.show()
# '''

'''
plt.figure(figsize=(12, 6))
plt.scatter(time_101, power_101, label='Device 101 Power', color='blue', **kwargs_101)
plt.scatter(time_103, power_103, label='Device 103 Power', color='green', **kwargs_103)
# plt.scatter(NOAA_time, NZDTdir_ir, label='NOAA Direct Irradiance', color='red', **kwargs_101)
# plt.scatter(NOAA_time, NZDTdiff_ir, label='NOAA Diffuse Irradiance', color='orange', **kwargs_101)
plt.plot(NOAA_time, simulated_power(solar_angle, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir)[0], label='Simulated Power 101', color='purple',linestyle='--')
plt.plot(NOAA_time, simulated_power(solar_angle, NZDTdir_ir, NZDTdiff_ir, NZDTup_ir)[1], label='Simulated Power 103', color='brown')
# print(f"DEBUG: Length of timestamp 101: {len(time_101)}")
# print(f"DEBUG: Length of timestamp 103: {len(time_103)}")
plt.title(f'Panels Power on Day {input_2} of 20{input_1}')
plt.xlabel('Time of the Day')
plt.ylabel('Power [W]')
plt.legend(loc = 'best',markerscale=5)
# plt.ylim(0,480)
#y ticks every 50 W
# plt.yticks(np.arange(0, 481, 50))
plt.grid(True)
ax = plt.gca()
start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
# Select 15 evenly spaced integers across the range
ax.set_xticks(np.linspace(0, int(end), 17).astype(int))
#rotate the x axis labels by 45 degrees
plt.xticks(rotation=45)
plt.savefig(f"{OutputPath}/power_spo_dev101_103_{input_1}_{input_2}_plot.png", bbox_inches='tight', dpi=100,facecolor='white')
plt.show()

'''