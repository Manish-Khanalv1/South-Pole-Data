import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# January 2026
TempArrayJan = pd.read_csv('TempJanuary2026.csv')
TempJan = TempArrayJan['Column 1']

MaximumJan = pd.to_numeric(TempJan)
numpy_maxJan = MaximumJan[0:-2]

MinimumJan = pd.to_numeric(TempJan)
numpy_minJan = MinimumJan[0:-2]

AverageJan = pd.to_numeric(TempJan)
numpy_avgJan = AverageJan[0:-2]

print(numpy_avgJan)
print(np.sum(numpy_avgJan))
print(type(numpy_avgJan[3]))

dayJan = np.linspace(0,31,31)
# plt.plot(dayJan, numpy_avgJan)
# plt.show()


# December 2025
TempArrayDec = pd.read_csv('TempDecember2025.csv')
TempDec = TempArrayDec['Column 1']

MaximumDec = pd.to_numeric(TempDec)
numpy_maxDec = MaximumDec[0:-2]

MinimumDec = pd.to_numeric(TempDec)
numpy_minDec = MinimumDec[0:-2]

AverageDec = pd.to_numeric(TempDec)
numpy_avgDec = AverageDec[0:-2]

print(numpy_avgDec)
print(np.sum(numpy_avgDec))
print(type(numpy_avgDec[3]))

dayDec = np.linspace(0,31,31)
# plt.plot(dayDec, numpy_avgDec)
# plt.show()


# November 2024
TempArrayNov = pd.read_csv('TempNovember2025.csv')
TempNov = TempArrayNov['Column 1']

MaximumNov = pd.to_numeric(TempNov)
numpy_maxNov = MaximumNov[0:-2]

MinimumNov = pd.to_numeric(TempNov)
numpy_minNov = MinimumNov[0:-2]

AverageNov = pd.to_numeric(TempNov)
numpy_avgNov = AverageNov[0:-2]

print(len(numpy_maxNov))
print(len(numpy_minNov))
print(len(numpy_avgNov))


dayNov = np.linspace(0,30,30)
# plt.plot(dayNov, numpy_avgNov)
# plt.show()


FullDayRange = np.concat((np.arange(365-31-30+1, 366, 1),np.arange(1,31+1,1)))
# print(FullDayRange)
print(len(FullDayRange))

NovDecJanAvg = np.concatenate([numpy_avgNov, numpy_avgDec, numpy_avgJan], axis = 0)
NovDecJanMin = np.concatenate([numpy_minNov,numpy_minDec,numpy_minJan], axis = 0)
NovDecJanMax = np.concatenate([numpy_maxNov,numpy_maxDec,numpy_maxJan], axis = 0)


# plt.plot(np.arange(0,len(NovDecJanAvg),1), NovDecJanAvg)
# plt.xlabel('Days Since November 1st')
# plt.ylabel('Temperature [°c]')
# plt.title('South Pole temperature data')
# plt.show()


plt.plot(np.arange(0,len(NovDecJanAvg),1), NovDecJanAvg, label = 'Average')
plt.plot(np.arange(0,len(NovDecJanMin),1), NovDecJanMin, label = 'Minimum')
plt.plot(np.arange(0,len(NovDecJanMax),1), NovDecJanMax, label = 'Maximum')
plt.legend()
plt.xlabel('Days Since November 1st')
plt.ylabel('Temperature [°c]')
plt.title('South Pole Temperature Data')
plt.show()