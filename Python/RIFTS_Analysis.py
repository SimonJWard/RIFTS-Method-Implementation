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
files=RIFTS_utils.find('Spectrum__1*.txt', dirpath)
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

# set times relative to first measurement
TimesArray = [(time - TimesArray[0]) for time in TimesArray]

# plot effective optical thickness measured against time spectra were modified
plt.figure(figsize=(10, 8))
plt.plot(TimesArray, PeaksArray,'x')
plt.ylabel("Effective Optical Thickness 2nL (nm*RIU)", fontsize=14)
plt.xlabel("Time (s)", fontsize=14)
plt.show()