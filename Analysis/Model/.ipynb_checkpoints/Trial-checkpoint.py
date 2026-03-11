# Source - https://stackoverflow.com/q/71773771
# Posted by whatcaitcodes, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-09, License - CC BY-SA 4.0

import time
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print("Current Time: ",current_time)
hour = time.strftime("%H")
minute = time.strftime("%M")
print ("Number of minutes since midnight: ",int(hour)*60+int(minute))
print(hour)

# current_time = time.strftime("%H:%M:%S", t)
# hour = time.strftime("%H")
# minute = time.strftime("%M")
# msm = int(hour)*60+int(minute)

