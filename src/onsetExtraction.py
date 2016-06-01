import numpy as np
import matplotlib.pyplot as plt
import sys, os
import pickle
from scipy.signal import get_window
import soundfile as sf
from sodpy.utilFuncs import noiseBurst, getEnvelope
from sodpy.stft import STFT
from sodpy.onsetPeakPicking import PeakPicker
from sodpy.onsetDetectors import getDetector

class Extractor:
    
    def __init__(self):

        self.params = { 'startTime' : 0,
                        'endTime' : None,
                        'windowType' : 'hann',
                        'windowSize' : 1024,
                        'fftSize' : 1024,
                        'hopSize' : 512,
                        'detectorType' : "EnergydB'",
                        'levelThreshold' : -100, 
                        'fLo' : 20,
                        'fHi' : 12e3,
                        'tau' : 0.01,
                        'filterSize' : 11,
                        'offset' : 0.1,
                        'factor' : 0.75,
                        'minInterval' : 0.1}

        self.allowPlot = True
        self.onsetTimes = None

    def initialise(self, inputFile, fs=None):

        if type(inputFile) is str:
            self.inputFile = inputFile

            # Load sound file and segment
            signal, self.fs = sf.read(inputFile)
        else:
            signal = inputFile
            self.fs = fs
        startIdx = int(np.round(self.params['startTime'] * self.fs))
        if self.params['endTime'] is not None:
            endIdx = int(np.round(self.params['endTime'] * self.fs))
        else:
            endIdx = None
        self.signal = signal[startIdx:endIdx]

        # Peak normalise
        self.signal /= np.max(self.signal)

        # Get analysis window
        w = get_window(self.params['windowType'], self.params['windowSize'])

        # STFT
        self.stft = STFT(self.signal, w, self.params['fftSize'], self.params['hopSize'])

        # Onset detector
        self.detector = getDetector(self.params['detectorType'], self.params['fftSize'])
        self.detector.configureBPF(self.params['fftSize'], self.fs, 
                self.params['fLo'], 
                self.params['fHi'])

        self.detector.levelThreshold = self.params['levelThreshold']
        
    def process(self):

        # Do frame processing
        numFrames = self.stft.numFrames
        odf = np.zeros(numFrames)
        if self.allowPlot:
            self.mXstore = np.zeros((numFrames, self.stft.numBins))
        for frame in range(numFrames):
            mX, pX = self.stft.process()
            odf[frame] = self.detector.process(mX, pX)
            if self.allowPlot:
                self.mXstore[frame] = mX+1e-5

        # Peak picker and configuration
        self.picker = PeakPicker(self.fs, self.params['hopSize'])
        self.picker.medianFilterType = "Bello"
         
        if(self.params['filterSize'] <= 0):
            self.params['filterSize'] = 1
        self.picker.medianFilterSize = self.params['filterSize']
        self.picker.medianFilterOffset = self.params['offset']
        self.picker.medianFilterFactor = self.params['factor']
        self.picker.tau = self.params['tau']
        self.picker.minInterval = self.params['minInterval']

        # Process
        self.onsetTimes = self.picker.process(odf)

    def saveOnsetsToCSV(self, outputFile = None):

        if self.onsetTimes is not None:
            if outputFile is None:
                outputFile = self.inputFile[:-4] + "_onsetTimes.csv"
            np.savetxt(outputFile, self.onsetTimes, delimiter=",")
            print 'Saved to ', outputFile
        else:
            print "Warning: no onsets detected."

    def saveParams(self, fileName):
        pickle.dump(self.params, file(fileName, 'wb'))

    def loadParams(self, fileName):
        self.params = pickle.load(open(fileName, 'rb'))

    def plot(self):

        if self.allowPlot and self.onsetTimes is not None:
            # Extract normalised envelope for plot
            envelope = getEnvelope(self.signal, self.fs, True, 0.01, True, True, False)
            # Output/plot variables
            # frameTime is centre of window
            numFrames = self.picker.odf.size
            frameTime = (self.params['hopSize'] *
                np.arange(numFrames)/float(self.fs))
            #offset by half hop size such that display frame centre is aligned with
            #window centre
            alignDisplayFrame = True
            pcolormeshOffset = 0
            if alignDisplayFrame:
                pcolormeshOffset -= (self.params['hopSize'] - 1) * 0.5 / float(self.fs)
            totalLength = self.signal.size / float(self.fs)
            time = np.arange(self.signal.size) / float(self.fs)
            binFreq = np.arange(1 + self.params['fftSize'] / 2) * float(self.fs) / self.params['fftSize']
            envelopeTimes = np.array(self.onsetTimes * self.fs, dtype='int')

            #the plot
            f, (ax1, ax2, ax3) = plt.subplots(3,1,sharex=True, sharey=False)
            ax1.set_title("Spectrogram (dB)")
            ax1.pcolormesh(pcolormeshOffset+frameTime, binFreq,
                    np.transpose(20*np.log10(self.mXstore)))
            ax1.axis([0, totalLength, 20, 10000])
            ax1.set_ylabel('Frequency, Hz')

            ax2.set_title("Signal, envelope and onsets")
            ax2.plot(time, self.signal)
            ax2.plot(time, envelope, 'r--')
            ax2.plot(self.onsetTimes, envelope[envelopeTimes], 'o', color='cyan')
            ax2.axis([0, totalLength, -1, 1])
            ax2.set_ylabel("Amplitude")

            ax3.set_title("ODF, smoothed ODF, threshold and onsets")
            ax3.plot(frameTime, self.picker.odf, 'k')
            ax3.plot(frameTime, self.picker.smoothODF, 'g')
            ax3.plot(frameTime, self.picker.adaptThresh, 'r--')
            ax3.plot(self.onsetTimes, self.picker.onsetValues, 'o', color='cyan')
            ax3.axis([0, totalLength, np.min(self.picker.odf), np.max(self.picker.odf)])
            ax3.set_ylabel("Normalised units")
            plt.xlabel('Time, s')

            plt.tight_layout()
            plt.show(block = True)

    def generateMarkedAudio(self):

        try:
            trigger = noiseBurst(self.fs)*0.7 #~ -3dB
            signal2 = np.hstack((self.signal*0.3, np.zeros(trigger.size))) #~ -10dB
            for onset in self.onsetTimes:
                idx = int(onset * self.fs)
                signal2[idx:idx+trigger.size] += trigger

            return signal2, self.fs
        except:
            return None

class BatchExtractor:

    def __init__(self):

        self.extractor = Extractor()
        self.saveOutput = True

    def initialise(self, directory, params = None):

        if type(params) is dict:
            self.extractor = params
        self.files = [x for x in os.listdir(directory) if '.wav' in x]

    def process(self):

        #loop through files and process
        for inputFile in self.files:
            print "Processing file: ", inputFile
            self.extractor.initialise(inputFile)
            extractor.process()
            if self.saveOutput:
                extractor.saveOnsetsToCSV()
