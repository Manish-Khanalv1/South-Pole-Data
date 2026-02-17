# Source - https://stackoverflow.com/a/16428019
# Posted by moooeeeep, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-13, License - CC BY-SA 3.0

import datetime
import random
import matplotlib.pyplot as plt

# make up some data
x = [datetime.datetime.now() + datetime.timedelta(hours=i) for i in range(2)]
y = [i+random.gauss(0,1) for i,_ in enumerate(x)]

# plot
plt.plot(x,y)
# beautify the x-labels
plt.gcf().autofmt_xdate()

plt.show()

