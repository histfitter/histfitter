"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 *                                                                                *
 * Description:                                                                   *
 *      Minimal example configuration with two different uncertainties            * 
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

################################################################
## In principle all you have to setup is defined in this file ##
################################################################
from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kBlue,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
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
ndataA     =  10. 	# Number of events observed in region A
ndataB     =  20. 	# Number of events observed in region B
ndataC     =  50. 	# Number of events observed in region C
ndataD     = 100. 	# Number of events observed in region D
EffB     =  15. 	# Ratio  of events expected in region B compared to A - Taken from MC/ calculated in back of envelope way?
EffC     =  8. 	# Ratio  of events expected in region C compared to A - Taken from MC/ calculated in back of envelope way?


lumiError = 0.03 	# Relative luminosity uncertainty

# Set predicted number of events in the different regions coming from non QCD background (these would be evaluated using MC/ other DD 
nbkgA=8
nbkgB=5
nbkgC=42
nbkgD=30

##########################

# Setting the parameters of the hypothesis test
#configMgr.doExclusion=False # True=exclusion, False=discovery
configMgr.nTOYs=5000
configMgr.calculatorType=2 # 2=asymptotic calculator, 0=frequentist calculator
configMgr.testStatType=3   # 3=one-sided profile likelihood test statistic (LHC default)
configMgr.nPoints=20       # number of values scanned of signal-strength for upper-limit determination of signal strength.

configMgr.statErrThreshold = 0.05
configMgr.statErrorType = "Poisson"
configMgr.writeXML = True
configMgr.blindSR = False
configMgr.blindCR = False

##########################

# Give the analysis a name
configMgr.analysisName = "MyUABCDExample"
configMgr.outputFileName = "results/%s_Output.root"%configMgr.analysisName

# Define cuts
configMgr.cutsDict["A"] = "1."
configMgr.cutsDict["B"] = "1."
configMgr.cutsDict["C"] = "1."
configMgr.cutsDict["D"] = "1."

# Define weights
configMgr.weights = "1."

# Define top-level
ana = configMgr.addFitConfig("ABCD")
# Define measurement
meas = ana.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=lumiError)
meas.addPOI("mu_A")

"""
meas.addParamSetting("mu_dummy_D",True,1)
meas.addParamSetting("mu_dummy_B",True,1)
meas.addParamSetting("mu_dummy_C",True,1)
"""
#meas.addParamSetting("Lumi",True,1)

#create test data
dataSample = Sample("Data",kBlack)
dataSample.setData()
dataSample.buildHisto([ndataA],"A","cuts",0.5)
dataSample.buildHisto([ndataB],"B","cuts",0.5)
dataSample.buildHisto([ndataC],"C","cuts",0.5)
dataSample.buildHisto([ndataD],"D","cuts",0.5)

backgroundSample = Sample("NonQCDBackground",kBlack)
backgroundSample.buildHisto([nbkgA],"A","cuts",0.5)
backgroundSample.buildHisto([nbkgB],"B","cuts",0.5)
backgroundSample.buildHisto([nbkgC],"C","cuts",0.5)
backgroundSample.buildHisto([nbkgD],"D","cuts",0.5)


ana.addSamples([dataSample,backgroundSample])


#make dummy samples
bkgSampleA = Sample("dummy_BkgA",kBlue)
bkgSampleA.buildHisto([1],"A","cuts",0.5)
#mu_A become the estimated Bkg events in SR
bkgSampleA.addNormFactor("mu_A",1.0, 100,0,False)

bkgSampleB = Sample("dummy_BkgB",kBlue)
bkgSampleB.buildHisto([1],"B","cuts",0.5)
bkgSampleB.addNormFactor("mu_A",1.0, 100,0,False)
bkgSampleB.addNormFactor("eff_B",EffB,2.*EffB,0,False)

bkgSampleC = Sample("dummy_BkgC",kBlue)
bkgSampleC.buildHisto([1],"C","cuts",0.5)
bkgSampleC.addNormFactor("mu_A",1.0, 100,0,False)
bkgSampleC.addNormFactor("eff_C",EffC,2.*EffC,0,False) 


#in region D eff_B* eff_C become the eff_D, because we assume we can use ABCD method
bkgSampleD = Sample("dummy_BkgD",kBlue)
bkgSampleD.buildHisto([1],"D","cuts",0.5)
bkgSampleD.addNormFactor("mu_A",1.0, 100,0,False)
bkgSampleD.addNormFactor("eff_B",EffB,2.*EffB,0,False)
bkgSampleD.addNormFactor("eff_C",EffC,2.*EffC,0,False)


# Add the channel
chanA = ana.addChannel("cuts",["A"],1,0.5,1.5)
chanA.addSample(bkgSampleA)
ana.setSignalChannels([chanA])
##region B
chanB = ana.addChannel("cuts",["B"],1,0.5,1.5)
chanB.addSample(bkgSampleB)
#region C
chanC = ana.addChannel("cuts",["C"],1,0.5,1.5)
chanC.addSample(bkgSampleC)
#region D
chanD = ana.addChannel("cuts",["D"],1,0.5,1.5)
chanD.addSample(bkgSampleD)
ana.setBkgConstrainChannels([chanB,chanC,chanD])


# These lines are needed for the user analysis to run
# Make sure file is re-made when executing HistFactory
if configMgr.executeHistFactory:
    if os.path.isfile("data/%s.root"%configMgr.analysisName):
        os.remove("data/%s.root"%configMgr.analysisName) 
