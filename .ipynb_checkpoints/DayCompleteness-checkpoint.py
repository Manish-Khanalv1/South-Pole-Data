import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta


n1 = 334
n1 = 365
DayRange25 = list(range(n1, n2))
DayRange26 = list(range(0, 26))
# DayRange = np.concatitnate(DayRange25, DayRange26)

Year = input('Enter last 2 digits of year: ')
if Year == 25:
    DayRange = DayRange25
if Year = 26:
    DayRange = DayRange26


for day in DayRange25: 

file_103 = pd.read_csv(f"{'DataFolder'}/spo_dev103_{25}_{345}.csv",delimiter=',')
file_101 = pd.read_csv(f"{'DataFolder'}/spo_dev101_{25}_{345}.csv",delimiter=',')

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
date = file_101['Date']
NumberDate = date.apply(date2num)
mask_to_keep =  NumberDate <= int(345)
file_101 = file_101[mask_to_keep]
# print(f'DEBUG: {mask_to_keep}')
# print(f'DEBUG: {NumberDate}')

date = file_103['Date']
NumberDate = date.apply(date2num)
mask_to_keep = NumberDate <= int(345)
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

# print(f'power_101: {power_101}')
# print(f'power_103: {power_103}')
# print(f'len(power_101): {len(power_101)}')
# print(f'len(power_103): {len(power_103)}')




