import numpy as np
import math
from scipy.signal import butter, filtfilt, lfilter

eps = np.finfo(float).eps

def noiseBurst(fs):
    burst = np.ones(0.001*fs)
    noise = np.random.randn(burst.size)
    noise /= np.max(noise)
    return burst * noise

def normalise(env):
    env -= env.min()
    env /= env.max()

def lpf(signal, order=2, cutOff=10, fs=44100, bidirectional=False):
    b,a = butter(order, cutOff / (0.5*fs), 'lowpass')
    if bidirectional:
        return filtfilt(b, a, signal)
    else:
        return lfilter(b,a,signal)

def hpf(signal, order=2, cutOff=10, fs=44100, bidirectional=False):
    b,a = butter(order, cutOff / (0.5*fs), 'highpass')
    if bidirectional:
        return filtfilt(b, a, signal)
    else:
        return lfilter(b,a,signal)

def onePole(signal, fs, tau, bidirectional=True):
    alpha = np.exp(-1 / (float(fs)*tau))
    if bidirectional:
        return filtfilt([1-alpha], [1.0, -alpha], signal)
    else:
        return lfilter([1-alpha], [1.0, -alpha], signal)

def getEnvelope(signal, fs, rectify=True, tau = 0.1, useOnepole=True, bi = False,
        normaliseEnvelope=False):
    if rectify:
        x = np.abs(signal)
    else:
        x = signal * signal
    if useOnepole:
        env = onePole(x, fs, tau, bi)
    else:
        fc = tau
        env = lpf(x, 2, fc, fs, bi)
    if normaliseEnvelope:
        normalise(env)
    return env
        
def percentileGate(signal, perc=75):
    thresh = np.percentile(signal[signal>0], perc)
    signal[signal<thresh] = 0

def medianFilter(odf, H=11, alpha=0, beta=1, filterType = "Bello"):
    '''
    Median filter according to Equation 20 in Bello et al. (2004).
    Alpha is the offset (default 0).
    Beta is the proportion of the median (default 1) for "Bello" and mean for
    "Brossier"
    For symmetric window, H should be odd.
    '''
    leftHalf = int((H-1)/2)
    rightHalf = H-1-leftHalf
    x = np.hstack((leftHalf, odf, rightHalf))
    out = np.zeros(odf.size)
    for i in xrange(odf.size):
        frame = x[i:i+H]
        if(filterType == "Bello"):
            out[i] = alpha + beta * np.median(frame)
        elif(filterType == "Brossier"):
            out[i] = alpha + np.median(frame) * beta * np.mean(frame)
    return out

def princarg(phase):
    return np.mod(phase +  np.pi, -2*np.pi) + np.pi
