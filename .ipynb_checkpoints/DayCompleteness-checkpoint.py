import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
CmpltThrsh = 80 # set the percentage thresh hold that you want the number of data points to be above in order to be marked as complete 
NumOfData = 2880 # This is the number of data points in an ideal day, the data in the other days will be compaired to this number. I think 2880 is the ideal



def date2num(date_str): # Renamed 'date' to 'date_str' to avoid confusion with the datetime.date object
        # 26 # first conver the xxxx-xx-xx format to date(xxxx, xx, xx)
        
        # You can skip splitting the string and go directly to parsing:
        date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 29 # return the day of the year (%j) as an integer
        # The strftime method returns a string, so we convert it to an integer.
        return int(date_object.strftime('%j'))


Successes_101 = 0 # count the number of files that loaded succesfully. 
Successes_103 = 0
n1 = 334
n2 = 365
DayRange25 = list(range(n1, n2))
DayRange26 = list(range(0, 26))
DayRange26_3dig = np.empty(len(DayRange26), dtype='U3')
for i in range(len(DayRange26)):
    DayRange26_3dig[i] = '{0:03d}'.format(int(i))
    
# DayRange = np.concatitnate(DayRange25, DayRange26)

Year = input('Enter last 2 digits of year: ')
if int(Year) == 25:
    DayRange = DayRange25
if int(Year) == 26:
    DayRange = DayRange26_3dig


DayRatioDict = {} # the shape will be day_number : [101ratio, 103ratio]

# loop through all the the days in the year the user wants

print('--------------------------------------')
print(f"               2 0 {Year[0]} {Year[1]}")
print('--------------------------------------')
print(' CHECKING TO SEE IF FILES LOAD  [PASS or FAIL]')
print('--------------------------------------')


for day in DayRange: 
    print()
    # Try device 101 
    try: 
    
        file_101 = pd.read_csv(f"{'DataFolder'}/spo_dev101_{Year}_{day}.csv",delimiter=',')
        
        # Rename the Device ID column to voltage and Voltage to Current
        file_101.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True)
        # There is a mismatch in the file so voltage column contains current and Device ID contains voltage
        
        # Each file has the data for more than just the day it is. We want to remove this extra dataS
        
        
        date = file_101['Date']
        NumberDate = date.apply(date2num)
        mask_to_keep =  NumberDate <= int(day)
        file_101 = file_101[mask_to_keep]
        # print(f'DEBUG: {mask_to_keep}')
        # print(f'DEBUG: {NumberDate}')
        
        
        
        #Extract time, voltage and current data
        
        time_101 = file_101['Time']
        voltage_101 = file_101['V'] 
        current_101 = file_101['A'] 
        
        
        power_101 = voltage_101 * current_101
        print(f"101: {day} PASS")
        Successes_101 += 1
        print()
        
            
    except: 
        power_101 = []
        print(f"101: {day} FAIL")
        print()


 # Try device 103
    try: 
    
        file_103 = pd.read_csv(f"{'DataFolder'}/spo_dev103_{Year}_{day}.csv",delimiter=',')
        
        # Rename the Device ID column to voltage and Voltage to Current
        file_103.rename(columns = {'Device ID': 'V', 'Voltage': 'A'}, inplace=True)
        # There is a mismatch in the file so voltage column contains current and Device ID contains voltage
        
        # Each file has the data for more than just the day it is. We want to remove this extra dataS
        
        
        date = file_103['Date']
        NumberDate = date.apply(date2num)
        mask_to_keep =  NumberDate <= int(day)
        file_103 = file_103[mask_to_keep]
        # print(f'DEBUG: {mask_to_keep}')
        # print(f'DEBUG: {NumberDate}')
        
        
        
        #Extract time, voltage and current data
        
        time_103 = file_103['Time']
        voltage_103 = file_103['V'] 
        current_103 = file_103['A'] 
        
        
        power_103 = voltage_103 * current_103
        print(f"103: {day} PASS")
        Successes_103 += 1
        print()
    except: 
        power_103 = []
        print(f"103: {day} FAIL")
        print()
    # DayRatioDict[day] = [round(len(power_101)/NumOfData, 2), round(len(power_103)/NumOfData*100, 2)]
    DayRatioDict[day] = [len(power_101) / NumOfData * 100,len(power_103) / NumOfData * 100]
print('--------------------------------------')

print()

print(f"101: {Successes_101}/{len(DayRange25)} ")
print()
        
print(f"103: {Successes_103}/{len(DayRange25)} ")
print()
print()
    
print('--------------------------------------')


# Old Table code, kept for security
# print(f"for {Year}")
# print(f"  Day  |  101   |  103   |  Complete  |")
# print(f"-------------------------------------")
# for day in DayRatioDict:
#     DeviceRatio_101 = DayRatioDict[day][0]
#     DeviceRatio_103 = DayRatioDict[day][1]
#     # check if they are both over 80%
#     if DeviceRatio_101 >= 80 and DeviceRatio_103 >= 80:
#         Complete = 'Complete      ✓'
#     else: 
#         Complete = 'InComplete'
        
#     print(f"  {day}    {DayRatioDict[day][0]:.3g}%    {DayRatioDict[day][1]:.2f}%    {Complete}  ")    
# print(f"--------------------------------------")


# ---------------ChatGPT code for a fixed width table-----------------------

print(f"               2 0 {Year[0]} {Year[1]}")
print('--------------------------------------')
print(f"{'Day':>4} | {'101':>7} | {'103':>7} | {'Complete':<10}")
print("-" * 38)

for day in DayRatioDict:
    DeviceRatio_101 = DayRatioDict[day][0]
    DeviceRatio_103 = DayRatioDict[day][1]

    if DeviceRatio_101 >= CmpltThrsh and DeviceRatio_103 >= CmpltThrsh:
        Complete = "  Complete   ✓"
    else:
        Complete = "InComplete"

    print(
        f"{day:>4} | "
        f"{DeviceRatio_101:>6.2f}% | "
        f"{DeviceRatio_103:>6.2f}% | "
        f"{Complete:<10}"
    )

print("-" * 38)


# --------------------------------------------------------------------------

print(f'* Complete means >= {CmpltThrsh}% of data for day')



