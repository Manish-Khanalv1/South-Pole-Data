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

# Global Variables
Area = 2.0 #m**2
baseurl = 'https://gml.noaa.gov/aftp/data/radiation/baseline/spo'
InputPath = '../DataFolder'
OutputPath = 'PlotsFolder/'

# import panel data function
def Import_Panel_Data(year, day):
    
    input_1 = year
    input_2 = day
    # # --------REAL PANEL DATA-------------
    
    # file_101 = pd.read_csv(f"{InputPath}/spo_dev101_{input_1}_{input_2}.csv",delimiter=',')
    # file_103 = pd.read_csv(f"{InputPath}/spo_dev103_{input_1}_{input_2}.csv",delimiter=',')
    
    # # Rename the Device ID column to voltage and Voltage to Current
    # file_101.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True)
    # file_103.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True) # There is a mismatch in the file so voltage column contains current and Device ID contains voltage
    
    # # Each file has the data for more than just the day it is. We want to remove these extra dataS
    
    # def date2num(date_str): # Renamed 'date' to 'date_str' to avoid confusion with the datetime.date object
    #     # 26 # first conver the xxxx-xx-xx format to date(xxxx, xx, xx)
    
    #     # You can skip splitting the string and go directly to parsing:
    #     date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
        
    #     # 29 # return the day of the year (%j) as an integer
    #     # The strftime method returns a string, so we convert it to an integer.
    #     return int(date_object.strftime('%j'))
    # # print(f'DEBUG: {input_2}')
    # date = file_101['Date']
    # NumberDate = date.apply(date2num)
    # mask_to_keep =  NumberDate <= int(input_2)
    # file_101 = file_101[mask_to_keep]
    # # print(f'DEBUG: {mask_to_keep}')
    # # print(f'DEBUG: {NumberDate}')
    
    # date = file_103['Date']
    # NumberDate = date.apply(date2num)
    # mask_to_keep = NumberDate <= int(input_2)
    # file_103 = file_103[mask_to_keep]
    
    # #Extract time, voltage and current data
    
    # time_101 = file_101['Time']
    # voltage_101 = file_101['V'] 
    # current_101 = file_101['A'] 
    
    # time_103 = file_103['Time']
    # voltage_103 = file_103['V'] 
    # current_103 = file_103['A'] 
    
    # power_101 = voltage_101 * current_101
    # power_103 = voltage_103 * current_103



    def date2num(date_str): # Renamed 'date' to 'date_str' to avoid confusion with the datetime.date object
        # 26 # first conver the xxxx-xx-xx format to date(xxxx, xx, xx)
    
        # You can skip splitting the string and go directly to parsing:
        date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 29 # return the day of the year (%j) as an integer
        # The strftime method returns a string, so we convert it to an integer.
        return int(date_object.strftime('%j'))
    
    try:
        file_101 = pd.read_csv(f"{InputPath}/spo_dev101_{input_1}_{input_2}.csv",delimiter=',')
        # Rename the Device ID column to voltage and Voltage to Current
        file_101.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True)
        date = file_101['Date']
        NumberDate = date.apply(date2num)
        mask_to_keep =  NumberDate <= int(input_2)
        file_101 = file_101[mask_to_keep]
        #Extract time, voltage and current data
        time_101 = np.array(file_101['Time'])
        voltage_101 = np.array(file_101['V']) 
        current_101 = np.array(file_101['A']) 
        power_101 = np.array(voltage_101 * current_101)
    except FileNotFoundError:
        time_101 = [np.nan]
        voltage_101 = [np.nan]
        current_101 = [np.nan]
        power_101 = [np.nan]

        
    try:
        file_103 = pd.read_csv(f"{InputPath}/spo_dev103_{input_1}_{input_2}.csv",delimiter=',')
        # Rename the Device ID column to voltage and Voltage to Current
        file_103.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True)
        date = file_103['Date']
        NumberDate = date.apply(date2num)
        mask_to_keep =  NumberDate <= int(input_2)
        file_103 = file_103[mask_to_keep]
        #Extract time, voltage and current data
        time_103 = np.array(file_103['Time'])
        voltage_103 = np.array(file_103['V']) 
        current_103 = np.array(file_103['A']) 
        power_103 = np.array(voltage_103 * current_103)
    except FileNotFoundError:
        time_103 = [np.nan]
        voltage_103 = [np.nan]
        current_103 = [np.nan]
        power_103 = [np.nan]
    
    
    
    # -----------------------------

    # print(f'len(power_101) = {len(power_101)}')
    return  date, time_101, time_103, voltage_101, voltage_103, current_101, current_103, power_101, power_103


day_range = ['345','346','347','348','349','350','351','352','353','354','355','356','357','358','359','360','361','362','363','364','365','001','002','003','004','005','006','007','008','009','010','011','012','013','014','015','016','017','018','019','020','021','022','023','024','025','026']



all_dates_101 = []
all_times_101 = []
all_voltages_101 = []
all_currents_101 = []
all_powers_101 = []

for day in day_range:
    print()
    print(day)
    print()
    if day[0] == '0':
        year = 26
    else:
        year = 25
    # Direct_Irradiance, Diffuse_Irradiance, Upwelling_Irradiance, NOAA_time = Import_NOAA_Data(year,day)
    date, time_101_og, time_103_og, voltage_101_og, voltage_103_og, current_101_og, current_103_og, power_101_og, power_103_og = Import_Panel_Data(year, day)
    time_101 = np.pad(time_101_og, pad_width = (0, 2880 - len(time_101_og)), constant_values = np.nan)
    time_103 = np.pad(time_103_og, pad_width = (0, 2880 - len(time_103_og)), constant_values = np.nan)
    voltage_101 = np.pad(voltage_101_og, pad_width = (0, 2880 - len(voltage_101_og)), constant_values = np.nan)
    voltage_103 = np.pad(voltage_103_og, pad_width = (0, 2880 - len(voltage_103_og)), constant_values = np.nan)
    current_101 = np.pad(current_101_og, pad_width = (0, 2880 - len(current_101_og)), constant_values = np.nan)
    current_103 = np.pad(current_103_og, pad_width = (0, 2880 - len(current_103_og)), constant_values = np.nan)
    power_101 = np.pad(power_101_og, pad_width = (0, 2880 - len(power_101_og)), constant_values = np.nan)
    power_103_= np.pad(power_103_og, pad_width = (0, 2880 - len(power_103_og)), constant_values = np.nan)
    
    all_dates_101.append(date)
    all_times_101.append(time_101)
    all_voltages_101.append(voltage_101)
    all_currents_101.append(current_101)
    all_powers_101.append(power_101)
    
    
    
    
    
    # power_103 = power_103_og
    # get the time_101 from day 345 because it is complete
    # __,__,time_101,__ = Import_Panel_Data(25,365)
    # print(len(time_101))

    
    # power_101_og = power_101_og.to_numpy()
    # print(f'og: {len(power_101_og)}')
    # # print(len(power_101))
    # # if power_101 is too small, we pad with nan
    # if len(power_101_og) <= 2880:
    #     difference = 2880 - len(power_101_og)
    #     power_101 = power_101_og
    #     for i in np.arange(0,difference,1):
    #         power_101 = np.append(power_101, np.nan)
    # # Same with 103
    # if len(power_103_og) <= 2880:
    #     difference = 2880 - len(power_103_og)
    #     power_103 = power_103_og
    #     for i in np.arange(0,difference,1):
    #         power_103 = np.append(power_103, np.nan)

            
    # print(len(power_101))
    # print(Direct_Irradiance)



data_101 = [all_dates_101, all_times_101, all_voltages_101, all_currents_101, all_powers_101]
print(data_101)
