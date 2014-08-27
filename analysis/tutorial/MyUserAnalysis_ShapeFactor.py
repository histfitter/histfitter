################################################################
## In principle all you have to setup is defined in this file ##
################################################################
from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import Measurement,Sample
from systematic import Systematic
from math import sqrt

# Setup for ATLAS plotting
from ROOT import gROOT
gROOT.LoadMacro("./macros/AtlasStyle.C")
import ROOT
ROOT.SetAtlasStyle()

##########################

# Set observed and expected number of events in counting experiment
nDataCR   = [75.,35.] 	# Number of events observed in data in CR
nDataSR   = [90.,110.]	# Number of events observed in data in SR
nBkgCR    = [20.,20.]	# Number of predicted bkg events in CR
nBkgSR    = [20.,20.]	# Number of predicted bkg events in SR
nSigSR    = [10.,80.] 	# Number of predicted signal events N.B. signal only in SR
lumiError =  0.039 	# Relative luminosity uncertainty

# Define systematics (1 +/- relative uncertainties)
bg1xsec = Systematic("BG1Xsec",configMgr.weights,1.05,0.95,"user","userOverallSys")
sigxsec = Systematic("SigXsec",configMgr.weights,1.05,0.95,"user","userOverallSys")
xtrap = Systematic("BG2Xtrap",configMgr.weights,1.05,0.95,"user","userOverallSys")

##########################

# Setting the parameters of the hypothesis test
#configMgr.nTOYs=5000
configMgr.calculatorType=2 # 2=asymptotic calculator, 0=frequentist calculator
configMgr.testStatType=3   # 3=one-sided profile likelihood test statistic (LHC default)
configMgr.nPoints=20       # number of values scanned of signal-strength for upper-limit determination of signal strength.

##########################

# Give the analysis a name
configMgr.analysisName = "MyUserAnalysis_ShapeFactor"
configMgr.outputFileName = "results/%s_Output.root"%configMgr.analysisName

# Define cuts
configMgr.cutsDict["CR"] = "1."
configMgr.cutsDict["SR"] = "1."

# Define weights
configMgr.weights = "1."

# Define samples
bkgSample = Sample("Bkg",kGreen-9)
bkgSample.setNormByTheory(True)
bkgSample.buildHisto(nBkgCR,"CR","cuts",0.5)
bkgSample.buildHisto(nBkgSR,"SR","cuts",0.5)
bkgSample.addSystematic(bg1xsec)

ddSample = Sample("DataDriven",kGreen+2)
ddSample.addShapeFactor("DDShape")

sigSample = Sample("Sig",kPink)
sigSample.setNormFactor("mu_Sig",1.,0.2,1.5)
sigSample.buildHisto(nSigSR,"SR","cuts",0.5)
sigSample.setNormByTheory(True)
sigSample.addSystematic(sigxsec)

dataSample = Sample("Data",kBlack)
dataSample.setData()
dataSample.buildHisto(nDataCR,"CR","cuts",0.5)
dataSample.buildHisto(nDataSR,"SR","cuts",0.5)

# Define top-level
ana = configMgr.addFitConfig("SPlusB")
ana.addSamples([bkgSample,ddSample,dataSample])

# Define measurement
meas = ana.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.039)
meas.addPOI("mu_Sig")
meas.addParamSetting("Lumi",True)

# Add the channels
chanCR = ana.addChannel("cuts",["CR"],2,0.5,2.5)

chanSR = ana.addChannel("cuts",["SR"],2,0.5,2.5)
chanSR.addSample(sigSample)
chanSR.getSample("DataDriven").addSystematic(xtrap)

ana.setBkgConstrainChannels([chanCR])
ana.setSignalChannels([chanSR])
ana.setSignalSample(sigSample)

# Make sure that file is re-made when before HistFactory is executed
if configMgr.executeHistFactory:
    if os.path.isfile("data/%s.root"%configMgr.analysisName):
        os.remove("data/%s.root"%configMgr.analysisName)
