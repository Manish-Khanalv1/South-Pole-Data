import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os

# where you want the data to be taken from and where you want to plots to go
InputPath = 'DataFolder'
OutputPath = 'PlotsFolder'

#Take user input for year and day of year
input_1  = input("Enter the last two digit of the year: ")
input_2  = input("Enter the day of year in format (DDD): ")

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
#print to only 2 decimal places
print
print(f"Average Power 101: {np.mean(power_101):.2f} W")
print(f"Average Power 103: {np.mean(power_103):.2f} W")
print(f"Max Power 101: {np.max(power_101):.2f} W, min: {np.min(power_101):.2f} W")
print(f"Max Power 103: {np.max(power_103):.2f} W, min: {np.min(power_103):.2f} W")
#Create a figure and axis objects
kwargs_101 = {'marker' : 'o', 's' : 3}
kwargs_103 = {'marker' : '^', 's' : 3}

plt.figure(figsize=(12, 6))
plt.scatter(time_101, voltage_101, label='Device 101 Voltage (V)', color='blue', **kwargs_101)
plt.scatter(time_101, current_101, label='Device 101 Current (A)', color='red', **kwargs_101)
plt.scatter(time_103, voltage_103, label='Device 103 Voltage (V)', color='green', **kwargs_103)
plt.scatter(time_103, current_103, label='Device 103 Current (A)', color='orange', **kwargs_103)
# print(f"DEBUG: Length of timestamp 101: {len(time_101)}")
# print(f"DEBUG: Length of timestamp 103: {len(time_103)}")
plt.title(f'Panels Voltage and Current on Day {input_2} of 20{input_1}')
plt.xlabel('Time of the Day')
plt.ylabel('Voltage (V) and Current (A)')
plt.legend(loc = 'best',markerscale=5)
plt.grid(True)
ax = plt.gca()
start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
# Select 15 evenly spaced integers across the range
ax.set_xticks(np.linspace(0, int(end), 17).astype(int))
#rotate the x axis labels by 45 degrees
plt.xticks(rotation=45)
plt.savefig(f"{OutputPath}/spo_dev101_103_{input_1}_{input_2}_plot.png", bbox_inches='tight', dpi=100,facecolor='white')
plt.show()

plt.figure(figsize=(12, 6))
plt.scatter(time_101, power_101, label='Device 101 Power', color='blue', **kwargs_101)
plt.scatter(time_103, power_103, label='Device 103 Power', color='green', **kwargs_103)
# print(f"DEBUG: Length of timestamp 101: {len(time_101)}")
# print(f"DEBUG: Length of timestamp 103: {len(time_103)}")
plt.title(f'Panels Power on Day {input_2} of 20{input_1}')
plt.xlabel('Time of the Day')
plt.ylabel('Power [W]')
plt.legend(loc = 'best',markerscale=5)
plt.ylim(0,480)
#y ticks every 50 W
plt.yticks(np.arange(0, 481, 50))
plt.grid(True)
ax = plt.gca()
start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
# Select 15 evenly spaced integers across the range
ax.set_xticks(np.linspace(0, int(end), 17).astype(int))
#rotate the x axis labels by 45 degrees
plt.xticks(rotation=45)
plt.savefig(f"{OutputPath}/power_spo_dev101_103_{input_1}_{input_2}_plot.png", bbox_inches='tight', dpi=100,facecolor='white')
plt.show()




