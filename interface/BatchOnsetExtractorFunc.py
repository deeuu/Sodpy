import numpy as np
import matplotlib.pyplot as plt
import sys, os, glob
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../src/'))
from scipy.signal import get_window
from Stft import STFT
from OnsetPeakPicking import PeakPicker
from OnsetDetectors import getDetector
from OnsetExtractor import Extractor
from audiolab import wavread, wavwrite

def main(directory, startTime, endTime, windowType, M, N, H, detectorType,
        levelThreshold, fcLo, fcHi, tau, filterSize, offset, factor, interval,
        allowPlot):

    #instantiate an extractor
    extractor = Extractor()
    extractor.windowType = windowType
    extractor.M = M
    extractor.N = N
    extractor.H = H
    extractor.detectorType = detectorType
    extractor.levelThreshold = levelThreshold
    extractor.fcLo = fcLo
    extractor.fcHi = fcHi
    extractor.tau = tau
    extractor.medianFilterSize = filterSize
    extractor.medianFilterOffset = offset
    extractor.medianFilterFactor = factor
    extractor.minInterval = interval
    extractor.startTime = startTime
    extractor.endTime = endTime

    #change directory
    os.chdir(directory)

    #loop through files and process
    for inputFile in glob.glob("*.wav"):
        print "Processing file: ", inputFile
        extractor.filename = inputFile
        extractor.initialise()
        extractor.process()
        extractor.saveOnsetTimes()
