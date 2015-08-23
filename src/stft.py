import numpy as np
import math
from scipy.fftpack import fft, ifft

'''
Adapted from sms-tools:
https://github.com/MTG/sms-tools
'''

class STFT(object):

    def __init__(self, x, w, N, H, energyNorm=False):

        if (H <= 0):
            raise ValueError("Hop size (H) smaller or equal to 0")

        if (w.size > N):
            raise ValueError("Window size (M) is greater than FFT size (N)")

        #window size
        self.M = w.size                                      

        #half window for odd and even business
        #for even hM1 = hM2
        #for odd hM2 = hM1-1
        self.hM1 = int(math.floor((self.M+1)/2))             
        self.hM2 = int(math.floor(self.M/2))#centre

        #FFT size
        self.N = N

        #number of positive bins
        self.numBins = int(1+self.N/2)

        #Hop size
        self.H = H

        #unnormalised window
        if energyNorm:
            self.w = w * np.sqrt(1.0/(N*w.size*np.mean(w*w)))
        else:
            self.w = w / np.sum(w)
        
        #Total number of frames with windows centred at time 0
        self.numFrames = int(np.ceil(x.size / float(self.H)))

        #pad start and end so window can be centred at start and end
        self.x = np.hstack((np.zeros(self.hM2), x, np.zeros(self.hM1)))

        #frame index 
        self.frame = 0

    def reset(self):
        self.frame = 0

    def process(self):
        '''
        Adapted from sms-tools.
        Returns the one-sided magnitude and phase spectrum (mX, pX).
        All bins except DC and nyquist (if present) are scaled by 2.
        '''
        hN = (self.N/2)+1 #includes DC
        mX, pX = np.zeros((2, hN))
        notNyqIdx = hN # excludes Nyquist when indexing array
        if (hN % 2) > 0:
            notNyqIdx = hN - 1
        if(self.frame < self.numFrames):
            start = self.frame*self.H
            x1 = self.x[start:start+self.M]
            fftbuffer = np.zeros(self.N)
            xw = x1*self.w
            fftbuffer[:self.hM1] = xw[self.hM2:]
            fftbuffer[-self.hM2:] = xw[:self.hM2]        
            X = fft(fftbuffer)
            mX = abs(X[:hN])
            mX[1:notNyqIdx] *= 2
            pX = np.unwrap(np.angle(X[:hN]))   
            self.frame += 1
        return mX, pX
