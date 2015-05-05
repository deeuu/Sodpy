from Tkinter import *
import tkFileDialog, tkMessageBox
import sys, os
from audiolab import wavread, play
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../src/'))
import OnsetExtractorFunc, BatchOnsetExtractorFunc
import csv

class OnsetsGUI:
  
    def __init__(self, parent):  
             
        self.parent = parent        
        self.initUI()

    def initUI(self):

        rowIdx = 0
        chooseLabel = "Input file (.wav, mono):"
        Label(self.parent, text=chooseLabel).grid(row=rowIdx, column=0, sticky=W,
                padx=5, pady=(10,2))
        rowIdx += 1

        #TEXTBOX TO PRINT PATH OF THE SOUND FILE
        self.fileLocation = Entry(self.parent)
        self.fileLocation.focus_set()
        self.fileLocation["width"] = 25
        self.fileLocation.grid(row=rowIdx,column=0, sticky=W, padx=10)
        self.fileLocation.delete(0, END)
        self.filename = '../sounds/piano_C3Major.wav'
        self.fileLocation.insert(0, self.filename)

        #BUTTON TO BROWSE SOUND FILE
        self.openFile = Button(self.parent, text="Browse...", command=self.browse_file) #see: def browse_file(self)
        self.openFile.grid(row=rowIdx, column=0, sticky=W, padx=(220, 6)) #put it beside the fileLocation textbox

        #BUTTON TO PREVIEW SOUND FILE
        self.preview = Button(self.parent, text=">", command=self.previewSound, bg="gray30", fg="white")
        self.preview.grid(row=rowIdx, column=0, sticky=W, padx=(306,6))
        rowIdx += 1

        #DETECTOR TYPE
        detectorLabel = "Detector:"
        Label(self.parent, text=detectorLabel).grid(row=rowIdx, column=0, sticky=W,
                padx=5)
        self.detector = StringVar()
        self.detector.set("EnergydB'") # initial value
        windowOption = OptionMenu(self.parent, self.detector,
                "Energy","Energy'","EnergydB","EnergydB'","HFC", "HFC'",
                "HFCdB", "HFCdB'", "MasriHFC", "SpectralFlux", "SpectralFluxdB",
                "PhaseDeviation", "ComplexDomain")
        windowOption.grid(row=rowIdx, column=0, sticky=W, padx=80)
        rowIdx += 1

	#ANALYSIS WINDOW TYPE
        windowTypeLabel = "Window:"
        Label(self.parent, text=windowTypeLabel).grid(row=rowIdx, column=0, sticky=W,
                padx=5)
        self.window = StringVar()
        self.window.set("blackman") # initial value
        windowOption = OptionMenu(self.parent, self.window, "rectangular",
                "hanning", "hamming", "blackman", "blackmanharris")
        windowOption.grid(row=rowIdx, column=0, sticky=W, padx=80)
        rowIdx += 1

        #TIME TO START ANALYSIS
        startTimeLabel = "Analysis start time (s):"
        Label(self.parent, text=startTimeLabel).grid(row=rowIdx, column=0, sticky=W,
                padx=5)
        self.startTime = Entry(self.parent, justify=CENTER)
        self.startTime["width"] = 5
        self.startTime.grid(row=rowIdx)
        self.startTime.delete(0, END)
        self.startTime.insert(0, "0.0")
        rowIdx += 1
        
        #TIME TO END ANALYSIS
        endTimeLabel = "Analysis end time (s):"
        Label(self.parent, text=endTimeLabel).grid(row=rowIdx, column=0, sticky=W,
                padx=5)
        self.endTime = Entry(self.parent, justify=CENTER)
        self.endTime["width"] = 5
        self.endTime.grid(row=rowIdx)
        self.endTime.delete(0, END)
        self.endTime.insert(0, "*")
        rowIdx += 1

        #WINDOW SIZE
        mSizeLabel = "Window size:"
        Label(self.parent, text=mSizeLabel).grid(row=rowIdx, column=0, sticky=W, padx=5)
        self.mSize = Entry(self.parent, justify=CENTER)
        self.mSize["width"] = 5
        self.mSize.grid(row=rowIdx)
        self.mSize.delete(0, END)
        self.mSize.insert(0, "1023")
        rowIdx += 1

        #FFT SIZE
        nSizeLabel = "FFT size (power of 2):"
        Label(self.parent, text=nSizeLabel).grid(row=rowIdx, column=0, sticky=W, padx=5)
        self.nSize = Entry(self.parent, justify=CENTER)
        self.nSize["width"] = 5
        self.nSize.grid(row=rowIdx)
        self.nSize.delete(0, END)
        self.nSize.insert(0, "1024")
        rowIdx += 1

        #HOP SIZE
        hSizeLabel = "Hop size:"
        Label(self.parent, text=hSizeLabel).grid(row=rowIdx, column=0, sticky=W, padx=5)
        self.hSize = Entry(self.parent, justify=CENTER)
        self.hSize["width"] = 5
        self.hSize.grid(row=rowIdx)
        self.hSize.delete(0, END)
        self.hSize.insert(0, "512")
        rowIdx += 1

        #LEVEL THRESHOLD
        binThreshLabel = "Bin threshold (dB):"
        Label(self.parent,
                text=binThreshLabel).grid(row=rowIdx,column=0,sticky=W,padx=5)
        self.levelThreshold = Entry(self.parent, justify=CENTER)
        self.levelThreshold["width"] = 5
        self.levelThreshold.grid(row=rowIdx)
        self.levelThreshold.delete(0,END)
        self.levelThreshold.insert(0,"-100")
        rowIdx += 1

        #Bandpass filter
        fLoLabel = "Band-pass low freq:"
        Label(self.parent, text=fLoLabel).grid(row=rowIdx, column=0, sticky=W,
                padx=5)
        self.fLo = Entry(self.parent, justify=CENTER)
        self.fLo["width"] = 5
        self.fLo.grid(row=rowIdx)
        self.fLo.delete(0, END)
        self.fLo.insert(0, "50")
        rowIdx += 1

        fHiLabel = "Band-pass high freq:"
        Label(self.parent, text=fHiLabel).grid(row=rowIdx, column=0, sticky=W,
                padx=5)
        self.fHi = Entry(self.parent, justify=CENTER)
        self.fHi["width"] = 5
        self.fHi.grid(row=rowIdx)
        self.fHi.delete(0, END)
        self.fHi.insert(0, "10000")
        rowIdx += 1

        #TIME CONSTANT
        tauLabel = "ODF time constant (s):"
        Label(self.parent, text=tauLabel).grid(row=rowIdx, sticky=W, padx=5)
        self.tau = Entry(self.parent, justify=CENTER)
        self.tau["width"] = 5
        self.tau.grid(row=rowIdx)
        self.tau.delete(0,END)
        self.tau.insert(0,"0.005")
        rowIdx += 1

        #Threshold filter size
        medianFilterSizeLabel = "Threshold filter size:"
        Label(self.parent, text=medianFilterSizeLabel).grid(row=rowIdx, sticky=W, padx=5)
        self.medianFilterSize= Entry(self.parent, justify=CENTER)
        self.medianFilterSize["width"] = 5
        self.medianFilterSize.grid(row=rowIdx)
        self.medianFilterSize.delete(0,END)
        self.medianFilterSize.insert(0,"5")
        rowIdx += 1

        #Threshold offset
        threshOffsetLabel = "Threshold offset:"
        Label(self.parent, text=threshOffsetLabel).grid(row=rowIdx, sticky=W, padx=5)
        self.threshOffset = Entry(self.parent, justify=CENTER)
        self.threshOffset["width"] = 5
        self.threshOffset.grid(row=rowIdx)
        self.threshOffset.delete(0,END)
        self.threshOffset.insert(0,"0.01")
        rowIdx += 1

        #Threshold scaling
        threshFactorLabel = "Threshold factor:"
        Label(self.parent, text=threshFactorLabel).grid(row=rowIdx, sticky=W, padx=5)
        self.threshFactor = Entry(self.parent, justify=CENTER)
        self.threshFactor["width"] = 5
        self.threshFactor.grid(row=rowIdx)
        self.threshFactor.delete(0,END)
        self.threshFactor.insert(0,"1.0")
        rowIdx += 1

        #MIN INTER-ONSET INTERVAL
        minIOILabel = "Min inter-onset Interval (s):"
        Label(self.parent, text=minIOILabel).grid(row=rowIdx, sticky=W, padx=5)
        self.minIOI = Entry(self.parent, justify=CENTER)
        self.minIOI["width"] = 5
        self.minIOI.grid(row=rowIdx)
        self.minIOI.delete(0,END)
        self.minIOI.insert(0,"0.5")
        rowIdx += 1

        #BUTTON FOR LOADING AND SAVING PARAMS
        self.loadButton = Button(self.parent, text="Load",
                command=self.loadParams, bg="gray30", fg="white")
        self.loadButton.grid(row=rowIdx, column=0, sticky=W, padx=5, pady=10)
        self.saveButton = Button(self.parent, text="Save",
                command=self.saveParams, bg="gray30", fg="white")
        self.saveButton.grid(row=rowIdx, column=0, sticky=W, padx=80) 
        rowIdx+=1

        #BUTTON TO COMPUTE EVERYTHING
        self.compute = Button(self.parent, text="Process", command=self.process, bg="dark red", fg="white")
        self.compute.grid(row=rowIdx, column=0, padx=5, pady=10, sticky=W)

        #BUTTON TO PREVIEW OUTPUT SOUND FILE
        self.preview = Button(self.parent, text=">", command=self.preview_output, bg="gray30", fg="white")
        self.preview.grid(row=rowIdx, column=0, sticky=W, padx=80)

        #PLOT OPTION
        self.plotState = BooleanVar()
        self.plotState.set(True)
        self.plotButton = Checkbutton(self.parent, text="Plot", variable=self.plotState)
        self.plotButton.grid(row=rowIdx, column=0, padx=160, pady=10, sticky=W)
        rowIdx += 1
        
        #SEPERATION LINE
        Frame(self.parent, height=1, width=50, bg="black").grid(row=rowIdx,
                sticky=W+E)
        rowIdx += 1

        #Batch processing label
        folderLabel = "Directory for batch processing (contains .wav files):"
        Label(self.parent, text=folderLabel).grid(row=rowIdx, column=0, sticky=W,
                padx=5, pady=(10,2))
        rowIdx += 1

        #TEXTBOX TO PRINT PATH OF THE SOUND FILE
        self.directory = Entry(self.parent)
        self.directory.focus_set()
        self.directory["width"] = 25
        self.directory.grid(row=rowIdx,column=0, sticky=W, padx=10)
        self.directory.delete(0, END)
        self.directoryName = '../sounds/'
        self.directory.insert(0, self.directoryName)

        #BUTTON TO BROWSE SOUND FILE
        self.openFolder = Button(self.parent, text="Browse...",
                command=self.browseFolder)
        self.openFolder.grid(row=rowIdx, column=0, sticky=W, padx=220)
        rowIdx += 1

        #BUTTON TO BATCH PROCESS AUDIO
        self.batchButton = Button(self.parent, text="Batch Process",
                command=self.batchProcess, bg="dark red", fg="white")
        self.batchButton.grid(row=rowIdx, column=0, padx=5, pady=10, sticky=W)

        # define options for opening file
        self.fileOpt = options = {}
        options['defaultextension'] = '.wav'
        options['filetypes'] = [('All files', '.*'), ('Wav files', '.wav')]
        options['initialdir'] = '../sounds/'
        options['title'] = 'Open a mono audio file (.wav)'

        # define options for opening file
        self.fileParamsOpt = options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('csv files', '.csv')]
        options['initialdir'] = '../sounds/'
        options['title'] = 'Open a parameter file (.csv)'

    def browse_file(self):
        self.filename = tkFileDialog.askopenfilename(**self.fileOpt)
        self.fileLocation.delete(0, END)
        self.fileLocation.insert(0,self.filename)

    def browseFolder(self):
        self.directoryName = tkFileDialog.askdirectory()
        self.directory.delete(0,END)
        self.directory.insert(0, self.directoryName)

    def previewSound(self):
        signal, fs, enc = wavread(self.filename)
        startIdx = int(float(self.startTime.get())* fs)
        if(self.endTime.get() == '*'):
            endIdx = None
        else:
            endIdx = int(float(self.endTime.get())*fs)
        play(signal[startIdx:endIdx], fs)

    def preview_output(self):
        outputFile = 'outputSounds/' +\
                os.path.basename(self.fileLocation.get())[:-4] + "_onsets.wav"
        signal, fs, enc = wavread(outputFile)
        play(signal, fs)

    def loadParams(self):
        filename = tkFileDialog.askopenfilename(**self.fileParamsOpt)
        inFile = open(filename, 'r')
        params = tuple([i for i in csv.reader(inFile) ][0])
        inFile.close()
        self.setParams(*params)

    def saveParams(self):
        filename = self.fileLocation.get()[:-4] + "_params.csv"
        print "Saved to: " + filename
        outFile = open(filename, 'w')
        writer = csv.writer(outFile)
        writer.writerow(self.getParams())
        outFile.close()

    def process(self):
        print "Processing..."
        if(OnsetExtractorFunc.main(*self.getAllParams(False))):
            print "Complete"
        else:
            print "Error"

    def batchProcess(self):
        print "Processing audio files..."
        BatchOnsetExtractorFunc.main(*self.getAllParams(True))
        print "Complete"

    def getAllParams(self, batch=False):

        if(batch):
            inputFile = self.directory.get()
        else:
            inputFile = self.fileLocation.get()
        startTime = float(self.startTime.get())
        if(self.endTime.get() == '*'):
            endTime = None
        else:
            endTime = float(self.endTime.get())
        window = self.window.get()
        detector = self.detector.get()
        m = int(self.mSize.get())
        n = int(self.nSize.get())
        h = int(self.hSize.get())
        levelThreshold = float(self.levelThreshold.get())
        filterSize = int(self.medianFilterSize.get())
        offset = float(self.threshOffset.get())
        factor = float(self.threshFactor.get())
        tau = float(self.tau.get())
        fLo = float(self.fLo.get())
        fHi = float(self.fHi.get())
        minIOI = float(self.minIOI.get())
        allowPlot = self.plotState.get()

        return (inputFile, startTime, endTime, window, m, n, h,
                detector,levelThreshold, fLo, fHi, tau, filterSize, offset,
                factor, minIOI, allowPlot)

    def getParams(self):
        params = self.getAllParams()[1:]
        return params

    def setParams(self, startTime, endTime, window, M, N, H, detector,
            levelThreshold, fLo, fHi, tau, filterSize, offset, factor,
            interval, allowPlot):

        self.startTime.delete(0, END)
        self.startTime.insert(0, startTime)
        self.endTime.delete(0, END)
        if endTime is None:
            endTime = '*'
        self.endTime.insert(0, '*')
        self.window.set(window)
        self.detector.set(detector)
        self.mSize.delete(0,END)
        self.mSize.insert(0,M)
        self.nSize.delete(0,END)
        self.nSize.insert(0,N)
        self.hSize.delete(0,END)
        self.hSize.insert(0,H)
        self.levelThreshold.delete(0,END)
        self.levelThreshold.insert(0,levelThreshold)
        self.fLo.delete(0,END)
        self.fLo.insert(0,fLo)
        self.fHi.delete(0,END)
        self.fHi.insert(0,fHi)
        self.medianFilterSize.delete(0,END)
        self.medianFilterSize.insert(0,filterSize)
        self.threshOffset.delete(0,END)
        self.threshOffset.insert(0,offset)
        self.threshFactor.delete(0,END)
        self.threshFactor.insert(0,factor)
        self.tau.delete(0,END)
        self.tau.insert(0,tau)
        self.minIOI.delete(0,END)
        self.minIOI.insert(0,interval)
        self.plotState.set(allowPlot == 'True')

def main():
    root = Tk()
    root.geometry("350x610+0+0")
    root.title("Onset Extractor")
    app = OnsetsGUI(root)
    root.mainloop()  

if __name__ == '__main__':
    main() 
