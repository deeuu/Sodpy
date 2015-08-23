import numpy as np
from sodpy.utilFuncs import *

class PeakPicker():

    def __init__(self, fs, H):
        self.fs = fs
        self.H = H
        self.tau = 0.1
        self.thresholdTau = 0.1
        self.minInterval = 0.1
        self.medianFilterOffset = 0.0
        self.medianFilterFactor = 1
        self.medianFilterSize = 5
        self.medianFilterType = "Bello"
        self.takeLargestPeak = True
        self.odf = self.onsetTimes = self.onsetIndices = self.onsetValues = None
        
    def process(self, odf):

        # A.POST PROCESSING
        #get the raw ODF
        self.odf = odf.copy()

        #first normalise the detection function
        self.odf = normalise(self.odf, True)

        #smooth the ODF using a zero-phase low-pass filter
        self.smoothODF = onePole(self.odf, self.fs/float(self.H), self.tau, True)

        # B.THRESHOLD
        self.adaptThresh = medianFilter(self.smoothODF,
                self.medianFilterSize, self.medianFilterOffset,
                self.medianFilterFactor, self.medianFilterType)

        # C. PEAK-PICKING
        #find local maxima (peaks)
        peakIndices = self.detectPeaks()
        #clean up
        if peakIndices is not None:
            return self.computeOnsetTimes(peakIndices)
        else:
            return None

    def detectPeaks(self):
        '''
        Detects peaks from the smooth onset detection function.
        '''
        peakIndices = np.array([], dtype='int')
        for i in range(1, self.smoothODF.size-1):
            #Threshold check
            threshCheck = self.smoothODF[i] > self.adaptThresh[i]
            if threshCheck:
                leftCheck = self.smoothODF[i] > self.smoothODF[i-1]
                rightCheck = self.smoothODF[i] > self.smoothODF[i+1]
                #peak check
                if leftCheck and rightCheck:
                    peakIndices = np.append(peakIndices, i)
        if peakIndices.size == 0:
            return None
        else:
            return peakIndices

    def computeOnsetTimes(self, peakIndices):
        t = peakIndices * self.H / float(self.fs)
        self.onsetTimes = np.array([t[0]])
        self.onsetIndices = np.array([peakIndices[0]])
        self.onsetValues = np.array([self.smoothODF[peakIndices[0]]])
        localTime = t[0]
        for i in range(1, t.size):

            #interval between this peak and the previous
            interval = t[i]-localTime
            #value of current peak
            peakValue = self.smoothODF[peakIndices[i]]

            #allow if peak location exceeds min inter-onset interval
            if interval > self.minInterval:
                self.onsetIndices = np.append(self.onsetIndices, peakIndices[i])
                self.onsetTimes = np.append(self.onsetTimes, t[i])
                self.onsetValues = np.append(self.onsetValues, peakValue)
                localTime = t[i]
            #else if peak is larger, remove previous and use this one
            elif peakValue > self.onsetValues[-1]:
                self.onsetIndices[-1] = peakIndices[i]
                self.onsetTimes[-1] = t[i]
                self.onsetValues[-1] = peakValue
                localTime = t[i]

        return self.onsetTimes
