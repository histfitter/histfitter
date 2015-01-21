################################################################
## In principle all you have to setup is defined in this file ##
################################################################
from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import fitConfig,Measurement,Channel,Sample
from systematic import Systematic
from math import sqrt

import os

# Setup for ATLAS plotting
from ROOT import gROOT
#gROOT.LoadMacro("./macros/AtlasStyle.C")
import ROOT
#ROOT.SetAtlasStyle()

##########################

# Set observed and expected number of events in counting experiment
ndata     =  7. 	# Number of events observed in data
nbkg      =  5.	 	# Number of predicted bkg events
nsig      =  1.  	# Number of predicted signal events
nbkgErr   =  1.  	# (Absolute) Statistical error on bkg estimate *from limited MC statistics*
nsigErr   =  2.  	# (Absolute) Statistical error on signal estimate *from limited MC statistics*
lumiError = 0.039 	# Relative luminosity uncertainty

# Set uncorrelated systematics for bkg and signal (1 +- relative uncertainties)
ucb = Systematic("uncorrl_bkg", configMgr.weights, 1.2,0.8, "user","userOverallSys")  # 20% error up and down


# correlated systematic between background and signal (1 +- relative uncertainties)



##########################

# Setting the parameters of the hypothesis test
configMgr.doExclusion=True # True=exclusion, False=discovery
#configMgr.nTOYs=5000
configMgr.calculatorType=2 # 2=asymptotic calculator, 0=frequentist calculator
configMgr.testStatType=3   # 3=one-sided profile likelihood test statistic (LHC default)
configMgr.nPoints=20       # number of values scanned of signal-strength for upper-limit determination of signal strength.

configMgr.writeXML = True

##########################

# Give the analysis a name
configMgr.analysisName = "MyUpperLimitAnalysis_SS"
configMgr.outputFileName = "results/%s_Output.root"%configMgr.analysisName

# Define cuts
configMgr.cutsDict["UserRegion"] = "1."

# Define weights
configMgr.weights = "1."

# Define samples
bkgSample = Sample("Bkg",kGreen-9)
bkgSample.setStatConfig(True)
bkgSample.buildHisto([nbkg],"UserRegion","cuts",0.5)


bkgSample.addSystematic(ucb)

sigSample = Sample("Sig",kPink)
sigSample.setNormFactor("mu_SS",1.,0.,10.)
#sigSample.setStatConfig(True)
sigSample.setNormByTheory()
sigSample.buildHisto([nsig],"UserRegion","cuts",0.5)




dataSample = Sample("Data",kBlack)
dataSample.setData()
dataSample.buildHisto([ndata],"UserRegion","cuts",0.5)

# Define top-level
ana = configMgr.addFitConfig("SPlusB")
ana.addSamples([bkgSample,sigSample,dataSample])
ana.setSignalSample(sigSample)

# Define measurement
meas = ana.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=lumiError)
meas.addPOI("mu_SS")
meas.addParamSetting("Lumi",True)

# Add the channel
chan = ana.addChannel("cuts",["UserRegion"],1,0.5,1.5)
ana.setSignalChannels([chan])

# These lines are needed for the user analysis to run
# Make sure file is re-made when executing HistFactory
if configMgr.executeHistFactory:
    if os.path.isfile("data/%s.root"%configMgr.analysisName):
        os.remove("data/%s.root"%configMgr.analysisName) 

