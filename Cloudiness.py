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
import scipy
from scipy.ndimage import generic_filter

    

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
    return MeanDirIr, StdevDirIr, NZDTdir_ir, NOAA_time


def cloudiness(InputYear, InputDay, output):
    
        
    MeanDir345, StdevDir345, dir_ir345, NOAA_time = ImportNOAA(25,345)
    # print(MeanDir345)
    # print(StdevDir345)
    
    # Now try another day
    
    YearToTry = InputYear
    DayToTry = InputDay
    
    MeanDirTry, StdevDirTry, Dir_irTry, NOAA_time = ImportNOAA(YearToTry, DayToTry)
    CloudinessMetric = np.zeros(len(Dir_irTry))  # this metric will be a list of 0 for if that part is cloudy, and 1 if it is not
    
    # Defining cloudiness from the power value deviation
    for i, val in enumerate(Dir_irTry):
        if val < MeanDir345 - 5*StdevDir345:
            CloudinessMetric[i] = 0
        else:
            CloudinessMetric[i] = 1
    
    
    if output == True:
        plt.figure()
        plt.figure(figsize=(12, 10))
        ax = plt.gca()
        plt.plot(NOAA_time, CloudinessMetric)
        # plt.plot(range(len(CloudinessMetric)), CloudinessMetric)
        plt.xlabel('time')
        plt.ylabel('Metric')
        plt.title(f'Power difference method day {DayToTry}, year {YearToTry}')
        start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
        # Select 15 evenly spaced integers across the range
        ax.set_xticks(np.linspace(0, int(end), 12).astype(int))
        plt.savefig('Cloudiness/CloudinessPlot.pdf')
    
    # defining cloudiness from smoothing the first method
    # kernal = [1,0,1]
    # SmoothedCloudinessMetric = np.convolve(CloudinessMetric, kernal)
    # SmoothedCouldinessMetric = np.where(SmoothedCloudinessMetric < 1.9, 0, 1)
    
    # plt.figure()
    # plt.plot(range(len(SmoothedCloudinessMetric)), SmoothedCloudinessMetric)
    # plt.savefig('Cloudiness/SmoothedCloudinessPlot.pdf')
    
    
    
    
    # defining cloudiness from the standard deviation of some data
    # This function takes a given array and window size and returns an array that has been convolved with a kernel that takes the standard deviation of the data that it covers
    StdevOfTry = generic_filter(Dir_irTry, np.std, size=3)

    # this metic looks if things are far from the mean
    StdevCloudinessMetric = np.zeros(len(Dir_irTry))
    for i, val in enumerate(StdevOfTry):
        if val > 1:
            StdevCloudinessMetric[i]= 0
        else:
            StdevCloudinessMetric[i]=1
    # find the % of the day that is coverd in clouds
    if output == True:
        # plotting
        plt.figure()
        plt.figure(figsize=(12, 10))
        # plt.plot(range(len(StdevOfTry)), StdevOfTry)
        plt.plot(NOAA_time, StdevOfTry)
        ax = plt.gca()
        start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
        # Select 15 evenly spaced integers across the range
        ax.set_xticks(np.linspace(0, int(end), 12).astype(int))
        plt.title(f'Cloudiness (Standard Deviation method) {DayToTry}, year {YearToTry}')
        plt.ylabel('Standard Deviation [Watts]')
        plt.xlabel('time')
        plt.savefig('Cloudiness/StdevMethodPlot.pdf')
    
        plt.figure()
        plt.figure(figsize=(12, 10))
        # plt.plot(range(len(StdevOfTry)), StdevCloudinessMetric)
        plt.plot(NOAA_time, StdevCloudinessMetric)
        ax = plt.gca()
        start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
        # Select 15 evenly spaced integers across the range
        ax.set_xticks(np.linspace(0, int(end), 12).astype(int))
        plt.title(f'Cloudiness (Standard Deviation method) {DayToTry}, year {YearToTry}')
        plt.ylabel('Metric [Watts]')
        plt.xlabel('time')
        plt.savefig('Cloudiness/StdevMethodCloudinessPlot.pdf')
    
    




    # combine methods

    CombinedMetric = np.where(CloudinessMetric + StdevCloudinessMetric<2, 0, 1)
    if output == True:
        plt.figure(figsize=(12,10))
        # plt.plot(range(len(StdevOfTry)), CombinedMetric)
        plt.plot(NOAA_time, CombinedMetric)
        ax = plt.gca()
        start, end = ax.get_xlim() # Get the range of the x-axis (e.g., 0 to N)
        # Select 15 evenly spaced integers across the range
        ax.set_xticks(np.linspace(0, int(end), 12).astype(int))
        plt.title(f'Cloudiness (Val + Stev method) {DayToTry}, year {YearToTry}')
        plt.ylabel('Metric[Watts]')
        plt.xlabel('time')
        plt.savefig('Cloudiness/CombinedMethod.pdf')

    # creat a % for the day of how cloudy it is based on the CombinedMetric
    ClearAmount = np.sum(CombinedMetric)/len(CombinedMetric)

    if output == True:
        print(f'Clear percent: {np.round(ClearAmount*100, 2)}%') 

    # # make a average of the direct irradiance every half hour
    # HalfHourMed = np.zeros(int(len(Dir_irTry)/30))
    # HalfHourMean = np.zeros(int(len(Dir_irTry)/30))
    
  
    block = 30 # block size in minutes
    n_HalfHourAvg = len(Dir_irTry)//block #number of data points taking half hour blocks
    n_Block = block   #number of data points in each block
    BlockedDir_irTry = np.reshape(Dir_irTry, (n_HalfHourAvg,n_Block))
    BlockMean = np.nanmean(BlockedDir_irTry, axis = 1)
    BlockMed = np.nanmedian(BlockedDir_irTry, axis = 1)
    print()
    print(f"BlockMean: {BlockMean}")
    print()
    print(f"BlockMed: {BlockMed}")
    print()
    print(f"BlockMean - BlockMed: {BlockMean - BlockMed}")
    

    # plot it
    plt.figure()
    plt.figure(figsize=(12, 10))
    plt.plot(range(n_HalfHourAvg), BlockMean, label = 'Mean')
    plt.plot(range(n_HalfHourAvg), BlockMed, label = 'Med')
    plt.scatter(range(n_HalfHourAvg), BlockMean, label = 'Mean')
    plt.scatter(range(n_HalfHourAvg), BlockMed, label = 'Med')
    plt.legend()
    plt.title(f'Half Hour Averages {DayToTry}, year {YearToTry}')
    plt.ylabel('Average [W]')
    plt.xlabel('time [30 min]')
    plt.savefig('Cloudiness/HalfHourAverage.pdf')
    
    # Do this same thing but for the precentege drop from the max
    max345 = np.max(dir_ir345)
    # print()
    # print(f"{max345}")
    # print()
    PercentDropMean = 100*BlockMean/max345
    PercentDropMed = 100*BlockMed/max345
    # Give the amount of the day that is cloudy based on this system
    ClearAmmount_PercDrop = np.where(PercentDropMean > 80, 1, 0)
    ClearAmmount_PercDrop = np.sum(ClearAmmount_PercDrop)/len(ClearAmmount_PercDrop)
    # plot it
    plt.figure()
    plt.figure(figsize=(12, 10))
    plt.plot(range(n_HalfHourAvg), PercentDropMean, label = 'Mean')
    plt.plot(range(n_HalfHourAvg), PercentDropMed, label = 'Med')
    plt.scatter(range(n_HalfHourAvg), PercentDropMean, label = 'Mean')
    plt.scatter(range(n_HalfHourAvg), PercentDropMed, label = 'Med')
    plt.legend()
    plt.title(f'Half Hour Averages Percent Drop from Maximum Power {DayToTry}, year {YearToTry}')
    plt.ylabel(' Percent Drop')
    plt.xlabel('time [30 min]')
    plt.savefig('Cloudiness/HalfHourPercentFromMax.pdf')

    # print(NOAA_time)

    ClearFraction = ClearAmmount_PercDrop
    return ClearFraction
year2try = input('Enter the Year to try: ')
day2try = input('Enter the day to try: ')
ClearFraction = cloudiness(year2try, day2try, output = True)
print(f"{np.round(ClearFraction*100, 2)}% of the day is clear")
