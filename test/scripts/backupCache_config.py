"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 *                                                                                *
 * Description:                                                                   *
 *      Minimal example configuration to read histograms from a root file.        * 
 *      Based on arXiV: [1809.11105].                                             *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

from configManager import configMgr
from configWriter import fitConfig,Measurement,Channel,Sample
from systematic import Systematic
from logger import Logger,INFO

import ROOT

analysis_name = "BackupCacheExample"

log = Logger(analysis_name)
log.setLevel(INFO)

configMgr.calculatorType=2
configMgr.testStatType=3
configMgr.writeXML = True

configMgr.analysisName = analysis_name
configMgr.histCacheFile = "data/"+analysis_name+".root"
configMgr.outputFileName = "results/"+analysis_name+"_Output.root"

configMgr.useCacheToTreeFallback = False
configMgr.useHistBackupCacheFile = True
configMgr.histBackupCacheFile =  "data/backupCache_example.root"

configMgr.inputLumi = 36.07456
configMgr.outputLumi = 36.07456
configMgr.setLumiUnits("fb-1")

# Dictionnary of cuts defining channels/regions (for Tree->hist)
configMgr.cutsDict["SSZCRee"] = "1."
configMgr.cutsDict["SSZCRmm"] = "1."
configMgr.cutsDict["SSZSRmm"] = "1."

# Define weights - dummy here
configMgr.weights = "1."

#-------------------------------------------
# List of samples and their plotting colours
#-------------------------------------------

topSample = Sample("top_physics",ROOT.kGreen-9)
topSample.setNormByTheory() #scales with lumi
topSample.setStatConfig(True)

zSample = Sample("SherpaDY221",ROOT.kAzure+1)
zSample.setNormByTheory()
zSample.setStatConfig(True)
zSample.setNormFactor("mu_ZSS",1.,0.,5000.)
zSample.setNormRegions([("SSZCRee","Mjj")])

dbSample = Sample("dibosonSherpa",ROOT.kYellow-3)
dbSample.setNormByTheory()
dbSample.setStatConfig(True)
dbSample.setNormFactor("mu_DB",1.,0.,5000.)
dbSample.setNormRegions([("SSZCRmm","Mjj")])

fakesSample = Sample("fakes",ROOT.kGray+1) 
fakesSample.setStatConfig(True)

# Signal sample
sigSample = Sample("WR1000_NR1400_Sig",ROOT.kViolet)
sigSample.legName = "HN signal"
sigSample.setNormByTheory()
sigSample.setStatConfig(True)       
sigSample.setNormFactor("mu_SIG",1.,0.,500.)

#data
dataSample = Sample("Data",ROOT.kBlack)
dataSample.setData()

#**************
# fit
#**************

## samples
commonSamples  = [dataSample,sigSample,fakesSample,topSample,dbSample,zSample]

## Parameters of the Measurement
measName = "NormalMeasurement"
measLumi = 1.
measLumiError = 0.021 # 2015+16

bkgOnly = configMgr.addFitConfig("Template_BkgOnly")
bkgOnly.statErrThreshold=0.05 #values above this will be considered in the fit
bkgOnly.addSamples(commonSamples)
bkgOnly.setSignalSample(sigSample)
meas = bkgOnly.addMeasurement(measName,measLumi,measLumiError)
meas.addPOI("mu_SIG")

CRs = []
SRs = []

## same-sign
channelSSZCRee = bkgOnly.addChannel("Mjj",["SSZCRee"],8,30,900)
channelSSZCRee.removeSample("WR1000_NR1400_Sig")
CRs += [channelSSZCRee]

channelSSZCRmm = bkgOnly.addChannel("Mjj",["SSZCRmm"],4,10,1629.0)
channelSSZCRmm.removeSample("SherpaDY221")
channelSSZCRmm.removeSample("WR1000_NR1400_Sig")
CRs += [channelSSZCRmm]

channelSSZSRmm = bkgOnly.addChannel("HT",["SSZSRmm"],8,400,4000)
channelSSZSRmm.removeSample("SherpaDY221")
channelSSZSRmm.removeSample("WR1000_NR1400_Sig")
SRs += [channelSSZSRmm]

## CRs:
bkgOnly.addBkgConstrainChannels(CRs)
## SRs:
bkgOnly.addSignalChannels(SRs)
