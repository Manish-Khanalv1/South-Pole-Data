import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates

#Take user input for year and day of year
input_1  = input("Enter the last two digit of the year: ")
input_2  = input("Enter the day of year in format (DDD): ")

#Read the CSV files based on user input
file_101 = pd.read_csv(f"spo_dev101_{input_1}_{input_2}.csv",delimiter=',')
file_103 = pd.read_csv(f"spo_dev103_{input_1}_{input_2}.csv",delimiter=',')

#Extract time, voltage and current data

time_101 = file_101['Time']
voltage_101 = file_101['Device ID'] # There is a mismatch in the file so 
                                    #'Device ID' column contains voltage data
current_101 = file_101['Voltage'] # There is a mismatch in the file so voltage column contains current

time_103 = file_103['Time']
voltage_103 = file_103['Device ID'] # There is a mismatch in the file so 
                                     #'Device ID' column contains voltage data
current_103 = file_103['Voltage'] # There is a mismatch in the file so voltage 
                                #column contains current

#Create a figure and axis objects
plt.figure(figsize=(12, 6))
plt.title(f"Device 101 and 103 Voltage and Current on Day {input_2} of 20{input_1}")
plt.plot(time_101, voltage_101, label='Device 101 Voltage (V)', color='blue')
plt.plot(time_101, current_101, label='Device 101 Current (A)', color='red')
plt.plot(time_103, voltage_103, label='Device 103 Voltage (V)', color='blue', linestyle='--')
plt.plot(time_103, current_103, label='Device 103 Current (A)', color='red', linestyle='--')
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
plt.savefig(f"spo_dev101_103_{input_1}_{input_2}_plot.png", bbox_inches='tight', dpi=300,facecolor='white')
plt.show()



