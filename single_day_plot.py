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
print(f'DEBUG: {input_2}')
date = file_101['Date']
NumberDate = date.apply(date2num)
mask_to_keep =  NumberDate <= int(input_2)
file_101 = file_101[mask_to_keep]
print(f'DEBUG: {mask_to_keep}')
print(f'DEBUG: {NumberDate}')

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

#Create a figure and axis objects
plt.figure(figsize=(12, 6))
plt.plot(time_101, voltage_101, label='Device 101 Voltage (V)', color='blue')
plt.plot(time_101, current_101, label='Device 101 Current (A)', color='red')
plt.plot(time_103, voltage_103, label='Device 103 Voltage (V)', color='blue', linestyle='--')
plt.plot(time_103, current_103, label='Device 103 Current (A)', color='red', linestyle='--')
plt.title(f'Panels Voltage and Current on Day {input_2} of 20{input_1}')
plt.xlabel('Time of the Day')
plt.ylabel('Voltage (V) and Current (A)')
plt.legend(loc = 'best')
plt.grid(True)
ax = plt.gca()
start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
# Select 15 evenly spaced integers across the range
ax.set_xticks(np.linspace(0, int(end), 17).astype(int))
#rotate the x axis labels by 45 degrees
plt.xticks(rotation=45)
plt.savefig(f"{OutputPath}/spo_dev101_103_{input_1}_{input_2}_plot.png", bbox_inches='tight', dpi=300,facecolor='white')
plt.show()



