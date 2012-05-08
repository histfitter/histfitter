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
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic
from math import sqrt

from ROOT import gROOT
gROOT.LoadMacro("./macros/AtlasStyle.C")
import ROOT
ROOT.SetAtlasStyle()


#---------------------------------------
# Flags to control which fit is executed
#---------------------------------------
useStat=True
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
configMgr.analysisName = "MyHistFitterExample"

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
    bgdFiles.append("root://eosatlas//eos/atlas/atlascerngroupdisk/phys-susy/histfitter/stronglepton/SusyFitterTree_OneSoftEle_BG_v3.root")
    bgdFiles.append("root://eosatlas//eos/atlas/atlascerngroupdisk/phys-susy/histfitter/stronglepton/SusyFitterTree_OneSoftMuo_BG_v3.root")
    if doExclusion:
        # 1-step simplified model
        sigFiles.append("root://eosatlas//eos/atlas/atlascerngroupdisk/phys-susy/histfitter/stronglepton/SusyFitterTree_p832_GG-One-Step_soft_v1.root")
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
jes = Systematic("JC","_NoSys","_JESup","_JESdown","tree","shapeSys")

configMgr.nomName = "_NoSys"

# List of samples and their plotting colours
topSample = Sample("Top",kGreen-9)
topSample.setNormFactor("mu_Top",1.,0.,5.)
topSample.setStatConfig(useStat)
wzSample = Sample("WZ",kAzure+1)
wzSample.setNormFactor("mu_WZ",1.,0.,5.)
wzSample.setStatConfig(useStat)
bgSample = Sample("BG",kYellow-3)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
bgSample.setStatConfig(useStat)
qcdSample = Sample("QCD",kGray+1)
qcdSample.setQCD(True,"histoSys")
qcdSample.setStatConfig(useStat)
dataSample = Sample("Data",kBlack)
dataSample.setData()

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

bkt = configMgr.addTopLevelXML("BkgOnly")
if useStat:
    bkt.statErrThreshold=0.05 
else:
    bkt.statErrThreshold=None
bkt.addSamples([topSample,wzSample,qcdSample,bgSample,dataSample])

# Systematics to a applied globally within this topLevel
bkt.getSample("Top").addSystematic(topKtScale)
bkt.getSample("WZ").addSystematic(wzKtScale)

meas=bkt.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.039)
meas.addPOI("mu_SIG")
meas.addParamSetting("mu_BG",True,1)

#-------------------------------------------------
# Constraining regions - statistically independent
#-------------------------------------------------

# WR using nJet
nJetWS = bkt.addChannel("nJet",["SLWR"],nJetBinHighWR-nJetBinLowSoft,nJetBinLowSoft,nJetBinHighWR)
nJetWS.hasB = True
nJetWS.hasBQCD = False
nJetWS.useOverflowBin = False
nJetWS.addSystematic(jes)
[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetWS.getSystematic(jes.name)]

# TR using nJet
nJetTS = bkt.addChannel("nJet",["SLTR"],nJetBinHighTR-nJetBinLowSoft,nJetBinLowSoft,nJetBinHighTR)
nJetTS.hasB = True
nJetTS.hasBQCD = True
nJetTS.useOverflowBin = False    
nJetTS.addSystematic(jes)
[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetTS.getSystematic(jes.name)]

bkt.setBkgConstrainChannels([nJetWS,nJetTS])

#--------------------------------------------------------------
# Validation regions - not necessarily statistically independent
#--------------------------------------------------------------

if doValidation:
    # s1l2jT
    srs1l2jTChannel = bkt.addChannel("cuts",["SR1sl2j"],srNBins,srBinLow,srBinHigh)
    srs1l2jTChannel.addSystematic(jes)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in srs1l2jTChannel.getSystematic(jes.name)]

    # additional VRs if using soft lep CRs
    nJetSLVR2 = bkt.addChannel("nJet",["SLVR2"],nJetBinHighTR-nJetBinLowSoft,nJetBinLowSoft,nJetBinHighTR)
    nJetSLVR2.addSystematic(jes)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetSLVR2.getSystematic(jes.name)]

    nBJetSLVR2 = bkt.addChannel("nBJet",["SLVR2"],nBJetBinHigh-nBJetBinLow,nBJetBinLow,nBJetBinHigh)
    nBJetSLVR2.addSystematic(jes)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nBJetSLVR2.getSystematic(jes.name)]
        
    meffSLVR2 = bkt.addChannel("meffInc",["SLVR2"],meffNBins,meffBinLow,meffBinHigh)
    meffSLVR2.addSystematic(jes)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meffSLVR2.getSystematic(jes.name)]

    metmeffSLVR2 = bkt.addChannel("met/meff2Jet",["SLVR2"],6,0.1,0.7)
    metmeffSLVR2.addSystematic(jes)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in metmeffSLVR2.getSystematic(jes.name)]

    metSLVR2 = bkt.addChannel("met",["SLVR2"],7,180,250)
    metSLVR2.addSystematic(jes)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in metSLVR2.getSystematic(jes.name)]

    #signal region treated as validation region for this case
    mm2J = bkt.addChannel("met/meff2Jet",["SS"],6,0.1,0.7)
    mm2J.useOverflowBin=True
    mm2J.addSystematic(jes)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in mm2J.getSystematic(jes.name)]
 
    bkt.setValidationChannels([nJetSLVR2,metSLVR2,meffSLVR2,nBJetSLVR2,metmeffSLVR2,mm2J,srs1l2jTChannel])
        



#**************
# Discovery fit
#**************

if doDiscovery:
    discovery = configMgr.addTopLevelXMLClone(bkt,"Discovery")
    
    # s1l2jT
    ssChannel = discovery.addChannel("cuts",["SS"],srNBins,srBinLow,srBinHigh)
    ssChannel.addSystematic(jes)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in ssChannel.getSystematic(jes.name)]
    ssChannel.addDiscoverySamples(["SS"],[1.],[0.],[100.],[kMagenta])
    discovery.setSignalChannels([ssChannel])


#-----------------------------
# Exclusion fits (1-step simplified model in this case)
#-----------------------------
if doExclusion:
    sigSamples=["SM_GG_onestepCC_425_385_345"]
                        
    for sig in sigSamples:
        myTopLvl = configMgr.addTopLevelXMLClone(bkt,"Sig_%s"%sig)

        sigSample = Sample(sig,kPink)
        sigSample.setFileList(sigFiles)
        sigSample.setNormByTheory()
        sigSample.setStatConfig(useStat)
        sigSample.setNormFactor("mu_SIG",1.,0.,5.)                    
        myTopLvl.addSamples(sigSample)
        myTopLvl.setSignalSample(sigSample)
    
        # Reassign merging for shapeSys
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["SLWR"]).getSystematic(jes.name)]
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["SLTR"]).getSystematic(jes.name)]

        # s1l2j using met/meff
        if doValidation:
            mm2J = myTopLvl.getChannel("met/meff2Jet",["SS"])
            iPop=myTopLvl.validationChannels.index("SS_metmeff2Jet")
            myTopLvl.validationChannels.pop(iPop)
        else:
            mm2J = myTopLvl.addChannel("met/meff2Jet",["SS"],5,0.2,0.7)
            mm2J.useOverflowBin=True
            mm2J.addSystematic(jes)
            [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in mm2J.getSystematic(jes.name)]
            pass
        myTopLvl.setSignalChannels([mm2J])
