import numpy as np
import RIFTS_utils
import matplotlib.pyplot as plt
import os, fnmatch

# configure plots to appear in seperate window
try:
	import IPython
	shell = IPython.get_ipython()
	shell.enable_matplotlib(gui='qt')
except:
	pass

# specify path of directory containing spectra files to be analysed
dirpath = "..\Data"

# find all .txt files in the directory specified above
files=RIFTS_utils.find('Spectrum*.txt', dirpath)
# order files based on filename
files = sorted(files, key=lambda x: int(x.split("__")[1].split(".txt")[0]))

# initialize empty lists to hold results
PeaksArray=[]
TimesArray=[]

for FileName in files:

    Data=np.loadtxt(FileName)
    print(FileName)
    
    # get time .txt spetrum file was modified, to order chronologically
    Time=os.path.getmtime(FileName)
    TimesArray.append(Time)
    
    # find location (2nL) of dominant peak in FFT
    Peak = RIFTS_utils.ffts(Data)
    PeaksArray.append(Peak)
    print(Peak)

plt.figure()
plt.plot(TimesArray, PeaksArray,'x')

## manually choose 2nL measurements to save

# print('You will choose the data points that you would like to save')

# plt.waitforbuttonpress()
# print('Select points with mouse, left to add, right to pop out, middle to stop')
# pts = []
# pts = np.asarray(plt.ginput(-1, timeout=-1))
# print(pts)
# pt_time = (pts[:,0]).astype(int)
# ptx=[]
# for t in range(len(pt_time)):
#     ind = (np.abs(Time - pt_time[t])).argmin()      #works out the closest point in time to the location of each click
#     ptx.append(ind)
#     print(ind)

# OPL=Peakx1[ptx]
# print(OPL)