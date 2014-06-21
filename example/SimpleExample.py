# An example HistFitter configuration with inputs set through variables

from configManager import configMgr
from configWriter import fitConfig,Measurement,Channel,Sample
from systematic import Systematic
from math import sqrt

import os

##########################

# Set observed and expected number of events in counting experiment
ndata     =  7. 	# Number of events observed in data
nbkg      =  5.	 	# Number of predicted bkg events
nsig      =  5.  	# Number of predicted signal events
nbkgErr   =  1.  	# (Absolute) Statistical error on bkg estimate
nsigErr   =  2.  	# (Absolute) Statistical error on signal estimate
lumiError = 0.039 	# Relative luminosity uncertainty

# Set uncorrelated systematics for bkg and signal (1 +- relative uncertainties)
ucb = Systematic("ucb", configMgr.weights, 1.2,0.8, "user","userOverallSys")
ucs = Systematic("ucs", configMgr.weights, 1.1,0.9, "user","userOverallSys")

# correlated systematic between background and signal (1 +- relative uncertainties)
corb = Systematic("cor",configMgr.weights, [1.1],[0.9], "user","userHistoSys")
cors = Systematic("cor",configMgr.weights, [1.15],[0.85], "user","userHistoSys")

##########################

# Setting the parameters of the hypothesis test
configMgr.calculatorType = 2 # 2=asymptotic calculator, 0=frequentist calculator
configMgr.nTOYs = 5000       # number of toys used in the frequentist calculator
configMgr.testStatType = 3   # 3=one-sided profile likelihood test statistic (LHC default)
configMgr.nPoints = 20       # number of values scanned of signal-strength for upper-limit determination of signal strength.

##########################

# Give the analysis a name
configMgr.analysisName = "MyUserAnalysis"
configMgr.outputFileName = "results/%s_Output.root"%configMgr.analysisName

# Define cuts
configMgr.cutsDict["UserRegion"] = "1."

# Define weights
configMgr.weights = "1."

# Define samples
bkgSample = Sample("Bkg", ROOT.kGreen-9)
bkgSample.setStatConfig(True)
bkgSample.buildHisto([nbkg], "UserRegion", "cuts")
bkgSample.buildStatErrors([nbkgErr], "UserRegion", "cuts")
bkgSample.addSystematic(corb)
bkgSample.addSystematic(ucb)

sigSample = Sample("Sig", ROOT.kPink)
sigSample.setNormFactor("mu_Sig", 1., 0., 100.)
sigSample.setStatConfig(True)
sigSample.setNormByTheory()
sigSample.buildHisto([nsig], "UserRegion", "cuts")
sigSample.buildStatErrors([nsigErr], "UserRegion", "cuts")
sigSample.addSystematic(cors)
sigSample.addSystematic(ucs)

dataSample = Sample("Data", ROOT.kBlack)
dataSample.setData()
dataSample.buildHisto([ndata], "UserRegion", "cuts")

# Define top-level
ana = configMgr.addFitConfig("SPlusB")
ana.addSamples([bkgSample, sigSample, dataSample])
ana.setSignalSample(sigSample)

# Define measurement
meas = ana.addMeasurement(name="NormalMeasurement", lumi=1.0, lumiErr=lumiError)
meas.addPOI("mu_Sig")
#meas.addParamSetting("Lumi", True, 1)

# Add the channel
chan = ana.addChannel("cuts", ["UserRegion"], 1, 0., 1.)
ana.setSignalChannels([chan])

# Make sure file is re-made when executing HistFactory
if configMgr.executeHistFactory:
    if os.path.isfile("data/%s.root" % configMgr.analysisName):
        os.remove("data/%s.root" % configMgr.analysisName) 