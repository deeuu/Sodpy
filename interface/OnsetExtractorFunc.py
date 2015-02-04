import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../src/'))
from scipy.signal import get_window
from audiolab import wavread, wavwrite
from UtilFuncs import noiseBurst, getEnvelope
from Stft import STFT
from OnsetPeakPicking import PeakPicker
from OnsetDetectors import getDetector

def main(inputFile, startTime, endTime, windowType, M, N, H, detectorType,
        levelThreshold, fcLo, fcHi, tau, filterSize, offset, factor, interval,
        allowPlot):

    #load sound file and segment
    signal, fs, enc = wavread(inputFile)
    startIdx = int(startTime* fs)
    endIdx = endTime
    endIdx = None
    if endTime is not None:
        endIdx = int(endTime*fs)
    signal = signal[startIdx:endIdx]

    #peak normalise
    signal /= np.max(signal)

    #get analysis window
    w = get_window(windowType, M)

    #initialise stft object
    stft = STFT(signal, w, N, H)

    #Get onset detector
    detector = getDetector(detectorType, N)
    detector.configureBPF(N, fs, fcLo, fcHi)
    detector.levelThreshold = levelThreshold
    
    #Do frame processing
    numFrames = stft.numFrames
    odf = np.zeros(numFrames)
    if allowPlot:
        mXstore = np.zeros((numFrames, stft.numBins))
    for frame in range(numFrames):
        mX, pX = stft.process()
        odf[frame] = detector.process(mX, pX)
        if allowPlot:
            mXstore[frame] = mX+1e-5

    #initialise peak picking
    picker = PeakPicker(fs, H)
    picker.medianFilterType = "Bello"
    if(filterSize <= 0):
        filterSize = 1
    picker.medianFilterSize = filterSize
    picker.medianFilterOffset = offset
    picker.medianFilterFactor = factor
    picker.tau = tau
    picker.minInterval = interval

    #process
    onsetTimes = picker.process(odf)

    #save
    if onsetTimes is not None:
        outputFile = inputFile[:-4] + "_onsetTimes.csv"
        np.savetxt(outputFile, onsetTimes, delimiter=",")
    else:
        print "Warning: no onsets detected."

    #plots
    if allowPlot and onsetTimes is not None:
        #extract normalised envelope for plot
        envelope = getEnvelope(signal, fs, True, 0.01, True, True, False)
        #output/plot variables
        #frmTime is centre of window
        frmTime = H*np.arange(numFrames)/float(fs)
        #offset by half hop size such that display frame centre is aligned with
        #window centre
        alignDisplayFrame = True
        pcolormeshOffset = 0
        if alignDisplayFrame:
            pcolormeshOffset -= (H-1)*0.5 / float(fs)
        totalLength = signal.size / float(fs)
        time = np.arange(signal.size) / float(fs)
        binFreq = np.arange(1 + N/2)*float(fs)/N  
        envelopeTimes = np.array(onsetTimes * fs, dtype='int')

        #output sound
        try:
            trigger = noiseBurst(fs)*0.7 #~ -3dB
            signal2 = np.hstack((signal*0.3, np.zeros(trigger.size))) #~ -10dB
            for onset in onsetTimes:
                idx = int(onset * fs)
                signal2[idx:idx+trigger.size] += trigger
            outputFile = './outputSounds/' + os.path.basename(inputFile)[:-4] +\
            '_onsets.wav'   
            wavwrite(signal2, outputFile, fs)
        except:
            print "Warning: Could not write audio onset file"

        #the plot
        f, (ax1, ax2, ax3) = plt.subplots(3,1,sharex=True, sharey=False)
        ax1.set_title("Spectrogram (dB)")
        ax1.pcolormesh(pcolormeshOffset+frmTime, binFreq, np.transpose(20*np.log10(mXstore)))
        ax1.axis([0, totalLength, 20, 10000])
        ax1.set_ylabel('Frequency, Hz')

        ax2.set_title("Signal, envelope and onsets")
        ax2.plot(time, signal)
        ax2.plot(time, envelope, 'r--')
        ax2.plot(onsetTimes, envelope[envelopeTimes], 'o', color='cyan')
        ax2.axis([0, totalLength, -1, 1])
        ax2.set_ylabel("Amplitude")

        ax3.set_title("ODF, smoothed ODF, threshold and onsets")
        ax3.plot(frmTime, picker.odf, 'k')
        ax3.plot(frmTime, picker.smoothODF, 'g')
        ax3.plot(frmTime, picker.adaptThresh, 'r--')
        ax3.plot(onsetTimes, picker.onsetValues, 'o', color='cyan')
        ax3.axis([0, totalLength, 0, 1])
        ax3.set_ylabel("Normalised units")
        plt.xlabel('Time, s')

        plt.tight_layout()
        plt.show(block=False)

    return True
