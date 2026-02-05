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
OutputPath = 'PlotsFolder'

#Take input for year(YY) and day of year(DDD)


'''NOAA Solar Radiation Data Download and Processing
Construct the base URL for NOAA data'''

def ImportNOAA(year, day):
    baseurl = 'https://gml.noaa.gov/aftp/data/radiation/baseline/spo'
    
    
    
    NOAA = [] #list to hold dataframes
    for i in [ int(day) - 1, int(day)]: #previous day and current day to match the NZDT time and GMT time
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
    solar_angle =  [np.cos(np.radians(-23.44*np.cos(np.radians(360*((x/1440)+182+int(day))+10)/365)))
                 *np.cos(((((x / 1440) + 182+int(day))%1)*2*np.pi)) for x in range(1440)] 
    
    solar_angle = np.array(solar_angle) #convert to numpy array
    solar_angle101 = np.concatenate((solar_angle[720:1440],solar_angle[0:720]))
    solar_angle103  = np.concatenate((solar_angle[360:1440],solar_angle[0:360]))
    
    '''Simulated Power Calculation
    A simple model to simulate power based on solar angle and irradiance
    This need to be verified and improved, I have made some assumptions here about efficiency, and the formula is very basic'''
    
    # print(NZDTup_ir)
    # print(NZDTdiff_ir)
    # print(NZDTdir_ir)
    
    
    MeanDirIr = np.mean(NZDTdir_ir)
    StdevDirIr = np.std(NZDTdir_ir)
    return MeanDirIr, StdevDirIr, NZDTdir_ir
MeanDir345, StdevDir345, dir_ir345 = ImportNOAA(25,345)
print(MeanDir345)
print(StdevDir345)

# Now try another day

YearToTry = input('Enter Last 2 digits of year: ')
DayToTry = input('Enter day number: ')

MeanDirTry, StdevDirTry, Dir_irTry = ImportNOAA(YearToTry, DayToTry)
CloudinessMetric = np.zeros(len(Dir_irTry))  # this metric will be a list of 1 for if that part is cloudy, and 0 if it is not
for i, val in enumerate(Dir_irTry):
    if val < MeanDir345 - 5*StdevDir345:
        CloudinessMetric[i] = 0
    else:
        CloudinessMetric[i] = 1
plt.plot(range(len(CloudinessMetric)), CloudinessMetric)
plt.savefig('CoudinessPlot.pdf')

