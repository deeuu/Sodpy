import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../src/'))
from scipy.signal import get_window
from UtilFuncs import getEnvelope
from Stft import STFT
from OnsetPeakPicking import PeakPicker
from OnsetDetectors import getDetector
from audiolab import wavread, wavwrite


class Extractor(object):

    def __init__(self, filename=''):
        self.filename = filename
        self.detectorType = "EnergydB'"
        self.M = 1023
        self.N = 1024
        self.H = 512
        self.windowType = 'blackman'
        self.fcLo = 20
        self.fcHi = 10000
        self.levelThreshold = -100
        self.filterSize = 10
        self.medianFilterOffset = 0.01
        self.medianFilterFactor = 1.0
        self.tau = 0.005
        self.minInterval = 0.1
        self.complete = False
        self.odf = self.onsetTimes = None
        self.startTime = 0
        self.endTime = None

    def initialise(self):

        #load sound file and segment
        signal, fs, enc = wavread(self.filename)
        startIdx = int(self.startTime*fs)
        if startIdx > signal.size:
            startIdx = signal.size-1
        if self.endTime is not None:
            endIdx = int(self.endTime*fs)
        else:
            endIdx = None
        signal = signal[startIdx:endIdx]

        #peak normalise
        signal /= np.max(signal)

        #get analysis window
        self.w = get_window(self.windowType, self.M)

        #initialise stft object
        self.stft = STFT(signal, self.w, self.N, self.H)

        #Get onset detector
        self.detector = getDetector(self.detectorType, self.N)
        self.detector.configureBPF(self.N, fs, self.fcLo, self.fcHi)
        self.detector.levelThreshold = self.levelThreshold

        #initialise peak picker
        self.picker = PeakPicker(fs, self.H)
        self.picker.medianFilterType = "Bello"
        self.picker.medianFilterSize = self.filterSize
        self.picker.medianFilterOffset = self.medianFilterOffset
        self.picker.medianFilterFactor = self.medianFilterFactor
        self.picker.tau = self.tau
        self.picker.minInterval = self.minInterval
        self.complete = False

    def process(self):

        #Do frame processing
        numFrames = self.stft.numFrames
        self.odf = np.zeros(numFrames)
        for frame in range(numFrames):
            mX, pX = self.stft.process()
            self.odf[frame] = self.detector.process(mX, pX)

        #now peak picking
        self.onsetTimes = self.picker.process(self.odf)

        self.complete = True

        return self.onsetTimes

    def saveOnsetTimes(self, filename=''):
        if self.complete:
            if not filename:
                filename = self.filename[:-4]
            filename += '_onsetTimes.csv'
            np.savetxt(filename, self.onsetTimes, delimiter=',')
