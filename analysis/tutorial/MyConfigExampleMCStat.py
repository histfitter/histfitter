"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 *                                                                                *
 * Description:                                                                   *
 *      Simple example configuration with seperate MC stat errors                 *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

## MB: This config file is similar to MyConfigExample.py, but the usual summed-up MC statistical errors for W and top 
## are replaced by individual MC stat errors per sample


################################################################
## In principle all you have to setup is defined in this file ##
################################################################

## This configuration performs a simplified version of the "soft lepton" fits documented in ATLAS-CONF-2012-041.
## Only two systematics are considered:
##   -JES (Tree-based) conservatively treated like an MC stat error
##   -Alpgen Kt scale (weight-based)
##
## For the real complete implementation, see: python/MyOneLeptonKtScaleFit_mergerSoftLep.py

from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange,kDashed,kSolid,kDotted
from configWriter import fitConfig,Measurement,Channel,Sample
from systematic import Systematic
from math import sqrt

from ROOT import gROOT, TLegend, TLegendEntry, TCanvas
#gROOT.LoadMacro("./macros/AtlasStyle.C")
import ROOT
#ROOT.SetAtlasStyle()

#---------------------------------------------------------------------------------------------
# Some flags for overridding normal execution and telling ROOT to shut up... use with caution!
#---------------------------------------------------------------------------------------------
#gROOT.ProcessLine("gErrorIgnoreLevel=10001;")
#configMgr.plotHistos = True

#---------------------------------------
# Flags to control which fit is executed
#---------------------------------------
useStat=False ## usual summed-up MC statistical errors replaces by individual MC stat errors per sample
doValidation=True
doDiscovery=False
doExclusion=False

#-------------------------------
# Parameters for hypothesis test
#-------------------------------
#configMgr.doHypoTest=False
#configMgr.nTOYs=1000
configMgr.calculatorType=2
configMgr.testStatType=3
configMgr.nPoints=20
#--------------------------------
# Now we start to build the model
#--------------------------------

# First define HistFactory attributes
configMgr.analysisName = "MyConfigExampleMCStat"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 0.001 # Luminosity of input TTree after weighting
configMgr.outputLumi = 4.713 # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

configMgr.histCacheFile = "data/"+configMgr.analysisName+".root"

configMgr.outputFileName = "results/"+configMgr.analysisName+"_Output.root"

# Set the files to read from
bgdFiles = []
sigFiles = []
if configMgr.readFromTree:
    bgdFiles.append("samples/tutorial/SusyFitterTree_OneSoftEle_BG_v3.root")
    bgdFiles.append("samples/tutorial/SusyFitterTree_OneSoftMuo_BG_v3.root")
    if doExclusion:
        # 1-step simplified model
        sigFiles.append("samples/tutorial/SusyFitterTree_p832_GG-One-Step_soft_v1.root")
else:
    bgdFiles = ["data/"+configMgr.analysisName+".root"]

# Dictionnary of cuts for Tree->hist
#CR
configMgr.cutsDict["SLWR"] = "(lep1Pt < 20 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet==0 && jet1Pt>130 && jet2Pt>25  && AnalysisType==7) || (lep1Pt < 25 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet==0 && jet1Pt>130 && jet2Pt>25  && AnalysisType==6)"
configMgr.cutsDict["SLTR"] = "(lep1Pt < 25 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet>0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6) || (lep1Pt < 20 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet>0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7)"
#VR
configMgr.cutsDict["SLVR2"] = "(lep1Pt < 25 && lep2Pt<10 && met>180 && met<250 && mt>80 && mt<100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6) || (lep1Pt < 20 && lep2Pt<10 && met>180 && met<250 && mt>80 && mt<100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7)"
#SR
configMgr.cutsDict["SS"] = "((lep1Pt < 20 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7) || (lep1Pt < 25 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6))"
configMgr.cutsDict["SR1sl2j"] = configMgr.cutsDict["SS"]+"&& met/meff2Jet>0.3"


# Tuples of nominal weights without and with b-jet selection
configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2Jet")

ktScaleWHighWeights = ("genWeight","eventWeight","ktfacUpWeightW","bTagWeight2Jet")
ktScaleWLowWeights = ("genWeight","eventWeight","ktfacDownWeightW","bTagWeight2Jet")

ktScaleTopHighWeights = ("genWeight","eventWeight","ktfacUpWeightTop","bTagWeight2Jet")
ktScaleTopLowWeights = ("genWeight","eventWeight","ktfacDownWeightTop","bTagWeight2Jet")
    
# QCD weights without and with b-jet selection
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

#--------------------
# List of systematics
#--------------------

# KtScale uncertainty as histoSys - two-sided, no additional normalization
topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")
wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleWLowWeights,"weight","normHistoSys")


# JES uncertainty as shapeSys - one systematic per region (combine WR and TR), merge samples
jes = Systematic("JES","_NoSys","_JESup","_JESdown","tree","normHistoSys")
mcstat = Systematic("mcstat", "_NoSys", "_NoSys", "_NoSys", "tree", "shapeStat")

# name of nominal histogram for systematics
configMgr.nomName = "_NoSys"

# List of samples and their plotting colours
topSample = Sample("Top",kGreen-9)
topSample.setNormFactor("mu_Top",1.,0.,5.)
topSample.setStatConfig(useStat)
topSample.setNormRegions([("SLWR","nJet"),("SLTR","nJet")])
wzSample = Sample("WZ",kAzure+1)
wzSample.setNormFactor("mu_WZ",1.,0.,5.)
wzSample.setStatConfig(useStat)
wzSample.setNormRegions([("SLWR","nJet"),("SLTR","nJet")])
bgSample = Sample("BG",kYellow-3)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
bgSample.setStatConfig(useStat)
bgSample.setNormRegions([("SLWR","nJet"),("SLTR","nJet")])
qcdSample = Sample("QCD",kGray+1)
qcdSample.setQCD(True,"histoSys")
qcdSample.setStatConfig(useStat)
dataSample = Sample("Data",kBlack)
dataSample.setData()
dataSample.buildHisto([86.,66.,62.,35.,11.,7.,2.,0.],"SLTR","nJet",2)
dataSample.buildHisto([1092.,426.,170.,65.,27.,9.,4.,1.],"SLWR","nJet",2)

# set the file from which the samples should be taken
for sam in [topSample, wzSample, bgSample, qcdSample, dataSample]:
        sam.setFileList(bgdFiles)

#Binnings
nJetBinLowHard = 3
nJetBinLowSoft = 2
nJetBinHighTR = 10
nJetBinHighWR = 10


nBJetBinLow = 0
nBJetBinHigh = 4

meffNBins = 6
meffBinLow = 400.
meffBinHigh = 1600.

meffNBinsSR4 = 4
meffBinLowSR4 = 800.
meffBinHighSR4 = 1600.

lepPtNBins = 6
lepPtLow = 20.
lepPtHigh = 600.

srNBins = 1
srBinLow = 0.5
srBinHigh = 1.5

#************
#Bkg only fit
#************

bkt = configMgr.addFitConfig("BkgOnly")
bkt.statErrThreshold=0.05 

#if useStat:
#    bkt.statErrThreshold=0.05 
#else:
#    bkt.statErrThreshold=None

bkt.addSamples([topSample,wzSample,qcdSample,bgSample,dataSample])

# Systematics to be applied globally within this topLevel
bkt.getSample("Top").addSystematic(topKtScale)
bkt.getSample("WZ").addSystematic(wzKtScale)

meas=bkt.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.039)
meas.addPOI("mu_SIG")
meas.addParamSetting("mu_BG",True,1)

#meas.addParamSetting("gamma_shapestat_SLTR_top_bin_5",True,1)
#meas.addParamSetting("gamma_shapestat_SLTR_top_bin_6",True,1)
#meas.addParamSetting("gamma_shapestat_SLTR_top_bin_7",True,1)
#meas.addParamSetting("gamma_shapestat_SLWR_top_bin_7",True,1)

#meas.addParamSetting("gamma_shapestat_SLTR_wz_bin_5",True,1)
#meas.addParamSetting("gamma_shapestat_SLTR_wz_bin_6",True,1)
#meas.addParamSetting("gamma_shapestat_SLTR_wz_bin_7",True,1)
#meas.addParamSetting("gamma_shapestat_SLWR_wz_bin_7",True,1)

#meas.addParamSetting("gamma_shapestat_SLWR_top_bin_0",True,1)
#meas.addParamSetting("gamma_shapestat_SLWR_top_bin_1",True,1)
#meas.addParamSetting("gamma_shapestat_SLWR_top_bin_2",True,1)

#meas.addParamSetting("gamma_shapestat_SLWR_wz_bin_0",True,1)
#meas.addParamSetting("gamma_shapestat_SLWR_wz_bin_1",True,1)
#meas.addParamSetting("gamma_shapestat_SLWR_wz_bin_2",True,1)


#-------------------------------------------------
# Constraining regions - statistically independent
#-------------------------------------------------

# WR using nJet
nJetWS = bkt.addChannel("nJet",["SLWR"],nJetBinHighWR-nJetBinLowSoft,nJetBinLowSoft,nJetBinHighWR)
nJetWS.hasB = True
nJetWS.hasBQCD = False
nJetWS.useOverflowBin = False
nJetWS.addSystematic(jes)
nJetWS.addSystematic(mcstat)

# TR using nJet
nJetTS = bkt.addChannel("nJet",["SLTR"],nJetBinHighTR-nJetBinLowSoft,nJetBinLowSoft,nJetBinHighTR)
nJetTS.hasB = True
nJetTS.hasBQCD = True
nJetTS.useOverflowBin = False    
nJetTS.addSystematic(jes)
nJetTS.addSystematic(mcstat)

bkt.setBkgConstrainChannels([nJetWS,nJetTS])

###################
#                                               #
#    Example new cosmetics     #
#                                               #
###################

# Set global plotting colors/styles
bkt.dataColor = dataSample.color
bkt.totalPdfColor = kBlue
bkt.errorFillColor = kBlue-5
bkt.errorFillStyle = 3004
bkt.errorLineStyle = kDashed
bkt.errorLineColor = kBlue-5

# Set Channel titleX, titleY, minY, maxY, logY
nJetWS.minY = 0.5
nJetWS.maxY = 5000
nJetWS.titleX = "n jets"
nJetWS.titleY = "Entries"
nJetWS.logY = True
nJetWS.ATLASLabelX = 0.25
nJetWS.ATLASLabelY = 0.85
nJetWS.ATLASLabelText = "Work in progress"


# Create TLegend (AK: TCanvas is needed for that, but it gets deleted afterwards)
c = TCanvas()
compFillStyle = 1001 # see ROOT for Fill styles
leg = TLegend(0.6,0.475,0.9,0.925,"")
leg.SetFillStyle(0)
leg.SetFillColor(0)
leg.SetBorderSize(0)
#
entry = TLegendEntry()
entry = leg.AddEntry("","Data 2011 (#sqrt{s}=7 TeV)","p") 
entry.SetMarkerColor(bkt.dataColor)
entry.SetMarkerStyle(20)
#
entry = leg.AddEntry("","Total pdf","lf") 
entry.SetLineColor(bkt.totalPdfColor)
entry.SetLineWidth(2)
entry.SetFillColor(bkt.errorFillColor)
entry.SetFillStyle(bkt.errorFillStyle)
#
entry = leg.AddEntry("","t#bar{t}","lf") 
entry.SetLineColor(topSample.color)
entry.SetFillColor(topSample.color)
entry.SetFillStyle(compFillStyle)
#
entry = leg.AddEntry("","WZ","lf") 
entry.SetLineColor(wzSample.color)
entry.SetFillColor(wzSample.color)
entry.SetFillStyle(compFillStyle)
#
entry = leg.AddEntry("","multijets (data estimate)","lf") 
entry.SetLineColor(qcdSample.color)
entry.SetFillColor(qcdSample.color)
entry.SetFillStyle(compFillStyle)
#
entry = leg.AddEntry("","single top & diboson","lf") 
entry.SetLineColor(bgSample.color)
entry.SetFillColor(bgSample.color)
entry.SetFillStyle(compFillStyle)

# Set legend for TopLevelXML
bkt.tLegend = leg
c.Close()



#--------------------------------------------------------------
# Validation regions - not necessarily statistically independent
#--------------------------------------------------------------

if doValidation:
    # s1l2jT
    srs1l2jTChannel = bkt.addChannel("cuts",["SR1sl2j"],srNBins,srBinLow,srBinHigh)
    srs1l2jTChannel.addSystematic(jes)

    # additional VRs if using soft lep CRs
    nJetSLVR2 = bkt.addChannel("nJet",["SLVR2"],nJetBinHighTR-nJetBinLowSoft,nJetBinLowSoft,nJetBinHighTR)
    nJetSLVR2.addSystematic(jes)
    
    #signal region treated as validation region for this case
    mm2J = bkt.addChannel("met/meff2Jet",["SS"],6,0.1,0.7)
    mm2J.useOverflowBin=True
    mm2J.addSystematic(jes)
    mm2J.addSystematic(mcstat)

    #    bkt.setValidationChannels([nJetSLVR2,metSLVR2,meffSLVR2,nBJetSLVR2,metmeffSLVR2,mm2J,srs1l2jTChannel])
    bkt.setValidationChannels([nJetSLVR2,srs1l2jTChannel,mm2J])
     
    dataSample.buildHisto([0.,1.,6.,16.,3.,0.],"SS","metmeff2Jet",0.1,0.1)
    dataSample.buildHisto([25.],"SR1sl2j","cuts",0.5) 
    dataSample.buildHisto([403.,202.,93.,39.,11.,10.,4.,1.],"SLVR2","nJet",2)

#**************
# Discovery fit
#**************

if doDiscovery:
    discovery = configMgr.addTopLevelXMLClone(bkt,"Discovery")
    
    # s1l2jT = signal region/channel
    ssChannel = discovery.addChannel("cuts",["SS"],srNBins,srBinLow,srBinHigh)
    ssChannel.addSystematic(jes)
    ssChannel.addDiscoverySamples(["SS"],[1.],[0.],[100.],[kMagenta])
    discovery.setSignalChannels([ssChannel])
    dataSample.buildHisto([26.],"SS","cuts",0.5)

#-----------------------------
# Exclusion fits (1-step simplified model in this case)
#-----------------------------
if doExclusion:
    sigSamples=["SM_GG_onestepCC_425_385_345"]
    dataSample.buildHisto([1.,6.,16.,3.,0.],"SS","metmeff2Jet",0.2,0.1)   
             
    for sig in sigSamples:
        myTopLvl = configMgr.addTopLevelXMLClone(bkt,"Sig_%s"%sig)

        sigSample = Sample(sig,kPink)
        sigSample.setFileList(sigFiles)
        sigSample.setNormByTheory()
        sigSample.setStatConfig(useStat)
        sigSample.setNormFactor("mu_SIG",1.,0.,5.)                    
        myTopLvl.addSamples(sigSample)
        myTopLvl.setSignalSample(sigSample)
    

        # s1l2j using met/meff
        if doValidation:
            mm2J = myTopLvl.getChannel("met/meff2Jet",["SS"])
            iPop=myTopLvl.validationChannels.index("SS_metmeff2Jet")
            myTopLvl.validationChannels.pop(iPop)
        else:
            mm2J = myTopLvl.addChannel("met/meff2Jet",["SS"],5,0.2,0.7)
            mm2J.useOverflowBin=True
            mm2J.addSystematic(jes)
            pass
        myTopLvl.setSignalChannels([mm2J])
