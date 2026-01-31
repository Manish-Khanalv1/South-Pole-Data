import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os
import urllib.request
import random
from numpy import trapezoid

def date2num(date_str): # Renamed 'date' to 'date_str' to avoid confusion with the datetime.date object
    # 26 # first conver the xxxx-xx-xx format to date(xxxx, xx, xx)

    # You can skip splitting the string and go directly to parsing:
    date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # 29 # return the day of the year (%j) as an integer
    # The strftime method returns a string, so we convert it to an integer.
    return int(date_object.strftime('%j'))
def num2date(day_num, year):
    """
    Converts a day number (1 to 365/366) and year into a date object.

    Args:
        day_num (int): The day number of the year (1-indexed).
        year (int): The year.

    Returns:
        datetime.date: The corresponding date object.
    """
    # Start date is January 1st of the given year
    start_date = datetime(int(year), 1, 1)
    
    # Calculate the offset (day_num - 1 because the start date is day 1)
    offset = timedelta(days=int(day_num) - 1)
    
    # Add the offset to the start date
    result_date = start_date + offset
    
    return result_date


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
# take mean
print(np.mean(power_101))
print(dates_101)
print(dates_103)

MeanPower_101 = np.zeros(len(day_range))
i = 0
for day in all_data_101:
    MeanPower_101[i]=np.mean(day['V']*day['A'])
    i += 1
MeanPower_103 = np.zeros(len(day_range))
i = 0
for day in all_data_103:
    MeanPower_103[i]=np.mean(day['V']*day['A'])
    i += 1

IntegratedPower_101 = np.zeros(len(day_range))
i = 0
for day in all_data_101:
    IntegratedPower_101[i]=trapezoid(day['V'].dropna()*day['A'].dropna(),dx=30)
    i += 1
IntegratedPower_103 = np.zeros(len(day_range))
i = 0
for day in all_data_103:
    IntegratedPower_103[i]=trapezoid(day['V'].dropna()*day['A'].dropna(),dx=30)
    i += 1
IntegratedPower_101 = IntegratedPower_101/(1000*60**2)
IntegratedPower_103 = IntegratedPower_103/(1000*60**2)

# convert day_range into calendar dates for the display
CalendarDate = np.zeros(len(day_range))
for i, day in enumerate(day_range):
    CalendarDate[i]=num2date(day, year)
    
plt.figure(figsize=(15, 6))
plt.scatter(CalendarDate, MeanPower_101, label='Device 101 Power (W)', color='blue', s=50)
plt.plot(CalendarDate, MeanPower_101, color = 'blue')
plt.scatter(CalendarDate, MeanPower_103, label='Device 103 Power (W)', color='green', s=50)
plt.plot(CalendarDate, MeanPower_103, color = 'green')
plt.grid('on')
plt.xlabel('Date')
plt.ylabel('Mean Power (W)')
plt.title(f'Power vs Time from Day {StartDay} to Day {EndDay} of 20{year}')
plt.legend(markerscale=1)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"MultiDayPlotsFolder/MeanPower_20{year}_{StartDay}_to_{EndDay}.png")
plt.show()

plt.figure(figsize=(15, 6))
plt.scatter(CalendarDate, IntegratedPower_101, label='Device 101 Power (W)', color='blue', s=50)
plt.plot(CalendarDate, IntegratedPower_101, color = 'blue')
plt.scatter(CalendarDate, IntegratedPower_103, label='Device 103 Power (W)', color='green', s=50)
plt.plot(CalendarDate, IntegratedPower_103, color = 'green')
plt.grid('on')
plt.xlabel('Date')
plt.ylabel('Total Energy [kwh]')
plt.title(f'Power vs Time from Day {StartDay} to Day {EndDay} of 20{year}')
plt.legend(markerscale=1)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"MultiDayPlotsFolder/IntegratedPower_20{year}_{StartDay}_to_{EndDay}.png")
plt.show()
    
# # for i in range(day_range):
# print(power_101)
# print(type(power_101))
# #date in x-axis in format mm-dd HH:MM
# plt.figure(figsize=(15, 6))
# plt.scatter(datetime_101, power_101, label='Device 101 Power (W)', color='blue', s=2)
# plt.scatter(datetime_103, power_103, label='Device 103 Power (W)', color='green', s=2)
# plt.grid('on')
# plt.xlabel('Date')
# plt.ylabel('Power (W)')
# plt.title(f'Power vs Time from Day {StartDay} to Day {EndDay} of 20{year}')
# plt.legend(markerscale=6)
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.savefig(f"MultiDayPlotsFolder/IntegratedPower_20{year}_{StartDay}_to_{EndDay}.png")
# plt.show()

