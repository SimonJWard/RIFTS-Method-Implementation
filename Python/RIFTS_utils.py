import numpy as np
from scipy.fftpack import fft
from scipy import interpolate
import matplotlib.pyplot as plt
from PyAstronomy import pyasl
import os, fnmatch
from scipy.signal import find_peaks
    
## Input Variabless

# wavelength range, for VIS 500nm-800nm, for IR 905nm-1440nm
UpperWavelengthLimit = 800
LowerWavelengthLimit = 500
# increments used when converting spectrum from units of wavelength to wavenumber
WavenumberIncrement = 0.0002
# controls number of points in the fast Fourier transform ie. frequency
# resolution through zero padding
ZeroPaddingConstant = 1024
# high and low frequency cutoffs, removing region where no mesasurable thin
# film fringes will be present, just noise
HighFreqCutoff = 150000
LowFreqCutoff = 3500
# number of points either side of the maximum FFT value to locally fit with a
# parabola
NumPointsParabolFit = 3


def ffts(data):
    """ Preprocess specrum data, apply the fast fourier transform (FFT),
    and idenfity the frequency (2nL) of dominant peak"""
    
    # read and transpose reflectance and wavelength data from .txt file
    Wavelength=(data.T)[0] 
    Reflectance=(data.T)[1]

    ## Visualize raw unprocessed spectrum

    # plt.figure()
    # plt.plot(Wavelength, Reflectance)
    
    ## Invert wavelength to wavenumber
    
    # reverses wavelength elements, and takes the reciprical*1000, to get
    # k (wavenumber) in units of inverse um
    k=np.flipud(1000/Wavelength)
    # reverses reflectance elements
    Reflectance=np.flipud(Reflectance)
    # zero mean
    Reflectance = Reflectance - np.mean(Reflectance)

    ## Interpolate because points are regularly spaced in wavelength but not wavenumber
    
    # calculate B-spline, or smoothed function, representing Reflectance points
    # as a function of k
    BSpline = interpolate.splrep(k, Reflectance, s=0)
    # desired wavenumber increments
    EquallySpacedk = np.arange(1000/UpperWavelengthLimit
                               , 1000/LowerWavelengthLimit, WavenumberIncrement)
    # evaluate B-spline calculated above at desired wavenumber increments
    InterpolatedR = interpolate.splev(EquallySpacedk, BSpline, der=0)
    # zero the mean of interpolated reflectance
    InterpolatedR = InterpolatedR - np.mean(InterpolatedR)

    ## Apply hanning window function (reduces ripple in FFT spectrum)
    
    # number of increments in EquallySpacedk, and points in interpolated reflectance
    # spectrum
    NumPointsInterpR = len(InterpolatedR)
    #apply hanning window function (reduces ripple in FFT spectrum)
    InterpolatedR = InterpolatedR*np.hanning(NumPointsInterpR)

    ## Apply FFT to preprocessed spectrum

    # number of points from the data to run the FFT on, returns first
    # power of 2 bigger than NumPointsInterpR, multipled by a constant which
    # controls the amount of zero padding
    NumPointsFFT=nextpow2(NumPointsInterpR)*ZeroPaddingConstant
    # the bigger NFFT is, the more zero padding (just adds 0's to the end of 
    # InterpolatedR)
    FFT = fft(InterpolatedR,NumPointsFFT)/NumPointsInterpR
    # frequency is limited to positive values (from 0 to NumPointsFFT/2 with 
    # no remainder), and is spaced out in increments of 1/2*1000/WavenumberIncrement 
    Frequency = np.linspace(0.0, 1000.0/(2.0*WavenumberIncrement), NumPointsFFT//2)
    # takes the absolute value of the FFT for positive frequencies
    # (up to NumPointsFFT/2 with no remainder)
    AbsFFT = 2.0 * np.abs(FFT[:NumPointsFFT//2])
    # removing region where no mesasurable thin film fringes will be present
    Frequency = Frequency[:HighFreqCutoff]
    AbsFFT = AbsFFT[:HighFreqCutoff]
    
    # plt.figure()
    # plt.plot(Frequency[LowFreqCutoff:], AbsFFT[LowFreqCutoff:], marker = ".")

    ## Primary method calculating peak position, by fitting a local parabola

    #find position of peak using parabola fit
    Peak, PeakIndex = pyasl.quadExtreme(Frequency[LowFreqCutoff:]
                                        , AbsFFT[LowFreqCutoff:]
                                        , dp=(NumPointsParabolFit, NumPointsParabolFit))
    
    ## Alternative, less accurate method of calculating peak position
    
    # find peaks with no interpolation, but minimum distance between peaks is
    # set to the length of the Fourier transform, so it will only return
    # one peak (the highest)
    PeakIndex = find_peaks(AbsFFT, distance = NumPointsFFT)[0]
   
    # return Frequency[PeakIndex]
    return Peak


def nextpow2(n):
    """ Function to calculate next power of 2, returns 2^n"""
    x=1
    while x<n:
        x=x*2
    return x


def LocateMaxima(A):
    """ Function to identify location of peak of maxima in FFT,
    returns max index"""
    max_position=0
    lA=len(A)
    b=A[0]
    for a in range(lA-1):
        if A[a+1]>b:
            b=A[a+1]
            max_position=a+1
    return max_position


def find(pattern, path):
    """ Function to find all files in a given path,
    with filename containing given pattern"""
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))    
    return result