import numpy as np
from sodpy.utilFuncs import princarg
eps = np.finfo(float).eps

def getDetector(detectorType, N):
    if(detectorType == "Energy"):
        detector = Energy(takeDiff=False)
    if(detectorType == "Energy'"):
        detector = Energy(takeDiff=True)
    if(detectorType == "EnergydB"):
        detector = Energy(useLog=True, takeDiff=False)
    if(detectorType == "EnergydB'"):
        detector = Energy(useLog=True, takeDiff=True)
    if(detectorType == "HFC"):
        detector = Energy(useLog=False, weights=np.arange(1+N/2),takeDiff=False)
    if(detectorType == "HFC'"):
        detector = Energy(useLog=False, weights=np.arange(1+N/2),takeDiff=True)
    if(detectorType == "HFCdB"):
        detector = Energy(useLog=True, weights=np.arange(1+N/2),takeDiff=False)
    if(detectorType == "HFCdB'"):
        detector = Energy(useLog=True, weights=np.arange(1+N/2),takeDiff=True)
    if(detectorType == "MasriHFC"):
        detector = MasriHFC()
    if(detectorType == "SpectralFlux"):
        detector = SpectralFlux()
    if(detectorType == "SpectralFluxdB"):
        detector = SpectralFlux(True)
    if(detectorType == "PhaseDeviation"):
        detector = PhaseDeviation()
    if(detectorType == "ComplexDomain"):
        detector = ComplexDomain()
    return detector

class OnsetDetector(object):

    def __init__(self):
        self.fcLo = None
        self.fcHi = None
        self.filterInitialised = False
        self.levelThreshold = -80

    def process(self, mX, pX):

        self.mX = mX.copy()
        self.pX = pX.copy()
        self.halfN = mX.size

        #if using filter...
        if self.filterInitialised:
            self.filterSpectrum()
        #clip magnitude spectrum...
        self.clipSpectrum()

        return self.processInternal()

    def processInternal(self):
        return True

    def configureBPF(self, N, fs, fcLo = None, fcHi= None):
        self.kLo = np.floor(fcLo  * N / float(fs)) + 1
        self.kHi = np.floor(fcHi  * N / float(fs))
        self.filterInitialised = True
 
    def filterSpectrum(self):
        '''
        Applies a band pass filter according to : lowFC < fc_k <= highFC
        mX: Linear one-sided magnitude spectrum
        pX: Unwrapped one-sided magnitude spectrum
        '''
        if self.kLo and self.kHi:
            self.mX[0:self.kLo] = eps
            self.mX[self.kHi:] = eps
            self.pX[0:self.kLo] = eps
            self.pX[self.kHi:] = eps

    def clipSpectrum(self):
        linThreshold = 10**(self.levelThreshold/20.0)
        self.mX[self.mX < linThreshold] = linThreshold

class Energy(OnsetDetector):
    '''
    Energy-based detectors work well for percussive sounds, but not so well when
    there is large overlap in energy. Following Bello (2005), it is my
    understanding that it is best to use the first difference of log energy,
    which tends to give sharp peaks as the amplitude envelope starts to rise. If
    you want the envelope, set takeDiff=False. Information relating to
    transients are more noticeable at higher frequencies, away from the tonal
    bands. Thus, a vector of weights (numpy array) can be used to weight power
    before computing the energy. So the high frequency content (HFC) function
    proposed by Masri can be obtained by setting weights = np.arange(N/2 + 1).
    Most algorithmis I have inspected do not use the first difference of the HFC
    function, but you can use the derivative by setting takeDiff=True.
    '''
    def __init__(self, useLog=False, weights=1, takeDiff=True):
        super(Energy, self).__init__()
        self.weights = weights
        self.useLog = useLog
        self.takeDiff = takeDiff
        self.reset()

    def reset(self):
        self.prevEnergy = 0.0

    def processInternal(self):
        '''
        Given the linear one-sided magnitude spectrum, this function computes
        the frame energy and returns the half-rectified difference 
        between the current and previous frame. See Bello (2005), comments following
        equation 2.
        '''
        #energy
        energy = np.sum(self.weights * self.mX * self.mX)
        if(self.useLog):
            energy = 10*np.log10(energy)

        #half rectify as only want onsets
        if(self.takeDiff):
            ODF = np.maximum(energy - self.prevEnergy, 0)
            self.prevEnergy= energy
        else:
            ODF = energy
        return ODF

class MasriHFC(OnsetDetector):
    def __init__(self):
        self.prevHFC = 1.0

    def reset(self):
        self.prevHFC = 1.0

    def processInternal(self):
        weights = np.arange(self.halfN)
        energy = np.sum(self.mX * self.mX)
        HFC = np.sum(weights * self.mX * self.mX)

        energy = np.minimum(energy, 1.0)
        ODF = (HFC / self.prevHFC) * (HFC / energy)
        self.prevHFC = np.minimum(HFC, 1.0)

        return ODF

class SpectralFlux(OnsetDetector):
    '''
    Uses the spectral difference (flux) to compute the onset detection function.
    Spectral flux is the magnitude difference between consecutive FFT frames.

    By default, the L1 norm of the spectral flux is used. Set this to false for
    the L2 norm.
    '''

    def __init__(self, useLog=False, l1Norm=True):
        super(SpectralFlux, self).__init__()
        self.l1Norm = l1Norm
        self.reset()
        self.useLog = useLog

    def reset(self):
        self.prevMX = 0

    def processInternal(self):

        if self.useLog:
            self.mX = 20*np.log10(self.mX)
        #rectified flux (onsets only..see Bello (2005))
        flux = np.maximum(self.mX - self.prevMX, 0)
        self.prevMX = self.mX

        if self.l1Norm:
            ODF = np.sum(np.abs(flux))
        else:
            ODF = np.sqrt(np.sum((flux)**2))
        return ODF

class PhaseDeviation(OnsetDetector):
    '''
    Onset detection based on the phase deviation.  Phase based algos are
    alternatives to energy based detectors and are useful for detecting soft
    onsets. Can be problematic when noise is present and are susceptible to
    phase distortion.
    '''
    
    def __init__(self):
        super(PhaseDeviation, self).__init__()
        self.reset()

    def reset(self):
        self.prevPX = 0.0
        self.prev2PX = 0.0
    
    def processInternal(self):
        '''
        Given the unwrapped phase spectrum, computes the phase deviation using
        the second difference of the phase.
        '''
        secondDif = princarg(self.pX - 2*self.prevPX + self.prev2PX)
        ODF = np.mean(np.abs(secondDif))
        self.prev2PX = self.prevPX
        self.prevPX = self.pX
        return ODF

class ComplexDomain(OnsetDetector):

    def __init__(self):
        super(ComplexDomain, self).__init__()
        self.reset()

    def reset(self):
        self.prevPX = 0.0
        self.prev2PX = 0.0
        self.prevMX = 0.0
    
    def processInternal(self):
        '''
        Given the linear magnitude and unwrapped phase one-sided spectrum,
        computes the complex domain onset detection function. This detector
        combines both energy and phase approaches.
        See Bello et al. (2004).
        '''
        secondDif = princarg(self.pX - 2*self.prevPX + self.prev2PX)
        ODF = np.sum(np.sqrt(self.prevMX**2 + self.mX**2 - 2*self.prevMX * self.mX *
            np.cos(secondDif)))
        self.prevMX = self.mX
        self.prev2PX = self.prevPX
        self.prevPX = self.pX
        return ODF
