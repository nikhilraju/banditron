__author__ = 'nikhilraju'

import matplotlib.pyplot as plt
import os
from pymongo import MongoClient
from math import log

coll = MongoClient('localhost',27017)['aml']['plots']
x = coll.find()[0]['rounds']
y = coll.find()[0]['error_rate']

log_x = [log(i) for i in x]
log_y = [log(i) for i in y]


filename = 'ErrorRatePlot'

plt.clf()
plt.grid()
plt.ylim([0, 1.0])
# plt.xlim([1, 10])
plt.plot(x, y, 'ko--', label='error', color='green')
plt.xlabel('Rounds')
plt.ylabel('Error Rate')
plt.title('Error Rate v/s Rounds -- ' + filename)
plt.legend(loc='lower right')
savepath = os.path.join(filename + ".jpeg")
plt.savefig(savepath)





