import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os
import urllib.request
import random


def date2num(date_str): # Renamed 'date' to 'date_str' to avoid confusion with the datetime.date object
    # 26 # first conver the xxxx-xx-xx format to date(xxxx, xx, xx)

    # You can skip splitting the string and go directly to parsing:
    date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # 29 # return the day of the year (%j) as an integer
    # The strftime method returns a string, so we convert it to an integer.
    return int(date_object.strftime('%j'))


year = input('Enter last 2 digits of the year: ')
StartDay = int(input('Starting Day: '))
EndDay = int(input('Ending Day: '))

day_range =  np.arange(StartDay, EndDay + 1)
day_range = ['{0:03d}'.format(i) for i in day_range]
print(day_range)
    
all_data_101 = []
all_data_103 = []
for i in day_range:
    try:
        file101 = pd.read_csv(f"DataFolder/spo_dev101_{year}_{i}.csv")
        file103 = pd.read_csv(f"DataFolder/spo_dev103_{year}_{i}.csv")
    except FileNotFoundError:
        print(f"File for day {i} not found. Skipping this day.")
        continue
    file101.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True)
    file103.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True)
    date_101 = file101['Date']
    NumberDate = date_101.apply(date2num)
    mask_to_keep =  NumberDate <= int(i)
    file101 = file101[mask_to_keep]

    date_103 = file103['Date']
    NumberDate = date_103.apply(date2num)
    mask_to_keep = NumberDate <= int(i)
    file103 = file103[mask_to_keep]

    all_data_101.append(file101)
    all_data_103.append(file103)
#convert list of dataframes to a single dataframe
combined_101 = pd.concat(all_data_101, ignore_index=True)
combined_103 = pd.concat(all_data_103, ignore_index=True)
print(combined_101[:-10])
#plot for different days
time_101 = combined_101['Time']
voltage_101 = combined_101['V'] 
current_101 = combined_101['A']

time_103 = combined_103['Time']
voltage_103 = combined_103['V'] 
current_103 = combined_103['A']

power_101 = voltage_101 * current_101
power_103 = voltage_103 * current_103

dates_101 = combined_101['Date']
dates_103 = combined_103['Date']
#combine date and time to a single datetime object
datetime_101 = [datetime.strptime(d + ' ' + t, '%Y-%m-%d %H:%M:%S') for d, t in zip(dates_101, time_101)]
datetime_103 = [datetime.strptime(d + ' ' + t, '%Y-%m-%d %H:%M:%S') for d, t in zip(dates_103, time_103)]

# Make hourl
power_101_hourly = power_101.groupby(power_101.index//120).mean()
power_103_hourly = power_103.groupby(power_103.index//120).mean()

datetime_101_hourly = datetime_101[::120]
datetime_103_hourly = datetime_103[::120]

#date in x-axis in format mm-dd HH:MM
plt.figure(figsize=(15, 6))
plt.scatter(datetime_101_hourly, power_101_hourly, label='Device 101 Power (W)', color='blue', s=12)
plt.scatter(datetime_103_hourly, power_103_hourly, label='Device 103 Power (W)', color='green', s=12)
plt.plot(datetime_101_hourly, power_101_hourly, label='Device 101 Power (W)', color='blue')
plt.plot(datetime_103_hourly, power_103_hourly, label='Device 103 Power (W)', color='green')
plt.grid('on')
plt.xlabel('Date')
plt.ylabel('Power (W)')
plt.title(f'Power vs Time from Day {StartDay} to Day {EndDay} of 20{year}')
plt.legend(markerscale=1)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"MultiDayPlotsFolder/MultiDayHourly/MultipledayPlots_Hourly_20{year}_{StartDay}_to_{EndDay}.png")
plt.show()
'''
Days_101 = []
Days_103 = []
for i in range(DayRange):
    file_101 = pd.read_csv(f"DataFolder/spo_dev101_{year}_{i + StartDay}.csv")
    file_103 = pd.read_csv(f"DataFolder/spo_dev103_{year}_{i + StartDay}.csv")

    file_101.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True)
    file_103.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True)

    date = file_101['Date']
    NumberDate = date.apply(date2num)
    mask_to_keep =  NumberDate <= int(i)
    file_101 = file_101[mask_to_keep]
    # print(f'DEBUG: {mask_to_keep}')
    # print(f'DEBUG: {NumberDate}')
    
    date = file_103['Date']
    NumberDate = date.apply(date2num)
    mask_to_keep = NumberDate <= int(i)
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
    
    Device_101_Dict = {'time': time_101, 'voltage': voltage_101, 'current': current_101, 'power': power_101}
    Device_103_Dict = {'time': time_103, 'voltage': voltage_103, 'current': current_103, 'power': power_103}

    Days_101.append(Device_101_Dict)
    Days_103.append(Device_103_Dict)


plt.figure()
for i in range(DayRange):

    PowerData = Device_101_dict[i]['power']
    TimeData = Device_101_dict[i]['time']
        
    plt.plot(TimeData, PowerData)
plt.savefig(f"MultiDayPlotsFolder/MultipledayPlots")
'''
