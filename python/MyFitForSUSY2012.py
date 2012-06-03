################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic
from math import sqrt

from ROOT import gROOT
gROOT.LoadMacro("./macros/AtlasStyle.C")
import ROOT
ROOT.SetAtlasStyle()

#---------------------------------------------------------------------------------------------
# Some flags for overridding normal execution and telling ROOT to shut up... use with caution!
#---------------------------------------------------------------------------------------------
#configMgr.plotHistos = True

#---------------------------------------
# Flags to control which fit is executed
#---------------------------------------
useStat=True

useHardLepCR=True
useDiLepCR=False
useSoftLepCR=False

#doValidationSRLoose=False
#doValidationSRTight=False
doValidationSlope=True
doValidationDilep=False
doValidationDilepZ=False
doValidationSoftLep=False

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
configMgr.analysisName = "OneLeptonFitSUSY12"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 0.001 # Luminosity of input TTree after weighting
configMgr.outputLumi = 1.664-0.114# Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

configMgr.histCacheFile = "data/"+configMgr.analysisName+".root"

configMgr.outputFileName = "results/"+configMgr.analysisName+"_Output.root"

# Set the files to read from
bgdFiles = []
sigFiles = []
if configMgr.readFromTree:
    #h1l
    InputFolderName = "/afs/cern.ch/atlas/groups/susy/1lepton/samples2/SUSY12"
    bgdFiles_e=[InputFolderName+"/tree_OneEle.root"]
    bgdFiles_m=[InputFolderName+"/tree_OneMuo.root"]
    bgdFiles_ee=[InputFolderName+"/tree_TwoEle.root"]
    bgdFiles_mm=[InputFolderName+"/tree_TwoMuo.root"]
    #bgdFiles_em=["../treeMakerForPro4/results/tree_EleMuo.root","../treeMakerForPro4/results/tree_MuoEle.root"]
    #bgdFiles_se=["../treeMakerForPro4/results/tree_SoftEle.root"]
    #bgdFiles_sm=["../treeMakerForPro4/results/tree_SoftMuo.root"]
else:
    bgdFiles = ["data/"+configMgr.analysisName+".root"]
#bgdFiles = bgdFiles_e  + bgdFiles_m \
#         + bgdFiles_ee + bgdFiles_mm + bgdFiles_em \
#         + bgdFiles_se + bgdFiles_sm
#Note: input bgdFiles and sigFiles are now set below

Plateau_ele = " && lep1Pt>26 && met>80"
Plateau_muo = " && lep1Pt>26 && met>100 && jet1Pt>80"
Plateau_met = " && met>200"

configMgr.cutsDict = {}
configMgr.cutsDict["TRee"]="(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && (jet1Pt > 80 || jet4Pt > 50) && nB3Jet > 0 && AnalysisType==3"
configMgr.cutsDict["TRmm"]="(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && (jet1Pt > 80 || jet4Pt > 50) && nB3Jet > 0 && AnalysisType==4"
configMgr.cutsDict["TRem"]="(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && (jet1Pt > 80 || jet4Pt > 50) && nB3Jet > 0 && AnalysisType==5"
configMgr.cutsDict["ZRee"]="mll>80 && mll<100  && met < 50 && jet2Pt > 50 && (jet1Pt > 80 || jet4Pt > 50) && AnalysisType==3"
configMgr.cutsDict["ZRmm"]="mll>80 && mll<100  && met < 50 && jet2Pt > 50 && (jet1Pt > 80 || jet4Pt > 50) && AnalysisType==4"

#configMgr.cutsDict["S2ee"]="met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==3"
#configMgr.cutsDict["S2mm"]="met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==4"
#configMgr.cutsDict["S2em"]="met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==5"
#configMgr.cutsDict["S4ee"]="met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==3"
#configMgr.cutsDict["S4mm"]="met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==4"
#configMgr.cutsDict["S4em"]="met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==5"

configMgr.cutsDict["VR2ee"]="met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && jet1Pt > 80 && AnalysisType==3"
configMgr.cutsDict["VR2em"]="met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && jet1Pt > 80 && AnalysisType==5"
configMgr.cutsDict["VR2mm"]="met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && jet1Pt > 80 && AnalysisType==4"

configMgr.cutsDict["VR3ee"]="met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && jet1Pt > 80 && AnalysisType==3"
configMgr.cutsDict["VR3em"]="met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && jet1Pt > 80 && AnalysisType==5"
configMgr.cutsDict["VR3mm"]="met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && jet1Pt > 80 && AnalysisType==4"

configMgr.cutsDict["VR4ee"]="met < 100 && jet4Pt > 50 && AnalysisType==3"
configMgr.cutsDict["VR4em"]="met < 100 && jet4Pt > 50 && AnalysisType==5"
configMgr.cutsDict["VR4mm"]="met < 100 && jet4Pt > 50 && AnalysisType==4"

configMgr.cutsDict["VZR2ee"]="met > 50 && met < 100 && jet2Pt > 50 && jet1Pt > 80 && nB3Jet == 0 && AnalysisType==3"
configMgr.cutsDict["VZR2em"]="met > 50 && met < 100 && jet2Pt > 50 && jet1Pt > 80 && nB3Jet == 0 && AnalysisType==5"
configMgr.cutsDict["VZR2mm"]="met > 50 && met < 100 && jet2Pt > 50 && jet1Pt > 80 && nB3Jet == 0 && AnalysisType==4"
configMgr.cutsDict["VZR2NoBselem"]="met > 50 && met < 100 && jet2Pt > 50 && jet1Pt > 80 && AnalysisType==5"

configMgr.cutsDict["VZR3ee"]="met > 50 && met < 100 && jet3Pt > 50 && jet1Pt > 80 && nB3Jet == 0 && AnalysisType==3"
configMgr.cutsDict["VZR3em"]="met > 50 && met < 100 && jet3Pt > 50 && jet1Pt > 80 && nB3Jet == 0 && AnalysisType==5"
configMgr.cutsDict["VZR3mm"]="met > 50 && met < 100 && jet3Pt > 50 && jet1Pt > 80 && nB3Jet == 0 && AnalysisType==4"
configMgr.cutsDict["VZR3NoBselem"]="met > 50 && met < 100 && jet3Pt > 50 && jet1Pt > 80 && AnalysisType==5"

configMgr.cutsDict["VZR4ee"]="met > 50 && met < 100 & jet4Pt > 50 && nB3Jet == 0 && AnalysisType==3"
configMgr.cutsDict["VZR4em"]="met > 50 && met < 100 & jet4Pt > 50 && nB3Jet == 0 && AnalysisType==5"
configMgr.cutsDict["VZR4mm"]="met > 50 && met < 100 & jet4Pt > 50 && nB3Jet == 0 && AnalysisType==4"
configMgr.cutsDict["VZR4NoBselem"]="met > 50 && met < 100 & jet4Pt > 50 && AnalysisType==5"

configMgr.cutsDict["HMTVL1El"]="AnalysisType==1 && met>30 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400" + Plateau_ele
configMgr.cutsDict["HMTVL1Mu"]="AnalysisType==2 && met>30 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400" + Plateau_muo
                      
# Slope in Meff is observed (tt : MC11). So, meff cut is not applied to TR for the time being.
configMgr.cutsDict["WREl"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==1" + Plateau_ele
configMgr.cutsDict["TREl"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0  && jet1Pt>80 && jet3Pt>25 && AnalysisType==1" + Plateau_ele
configMgr.cutsDict["WRMu"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==2" + Plateau_muo
configMgr.cutsDict["TRMu"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0  && jet1Pt>80 && jet3Pt>25 && AnalysisType==2" + Plateau_muo

configMgr.cutsDict["TRElVR"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1" + Plateau_ele
configMgr.cutsDict["TRMuVR"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2" + Plateau_muo

configMgr.cutsDict["TRElVR2"]="lep2Pt<10 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1" + Plateau_ele
configMgr.cutsDict["TRMuVR2"]="lep2Pt<10 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2" + Plateau_muo

configMgr.cutsDict["WRElVR"]="lep2Pt<10 && met>50 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==1" + Plateau_ele
configMgr.cutsDict["WRMuVR"]="lep2Pt<10 && met>50 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==2" + Plateau_muo

#configMgr.cutsDict["S3El"]="AnalysisType==1 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80" + Plateau_ele
#configMgr.cutsDict["S4El"]="AnalysisType==1 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80" + Plateau_ele

#configMgr.cutsDict["S3Mu"]="AnalysisType==2 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80" + Plateau_muo
#configMgr.cutsDict["S4Mu"]="AnalysisType==2 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80" + Plateau_muo

#configMgr.cutsDict["SR3jTEl"]="AnalysisType==1 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80 && meffInc>1200" + Plateau_ele
#configMgr.cutsDict["SR4jTEl"]="AnalysisType==1 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80 && meffInc>800" + Plateau_ele

#configMgr.cutsDict["SR3jTMu"]="AnalysisType==2 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80 && meffInc>1200" + Plateau_muo
#configMgr.cutsDict["SR4jTMu"]="AnalysisType==2 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80 && meffInc>800" + Plateau_muo
#configMgr.cutsDict["SR7jTEl"]="AnalysisType==1 && met>180 && mt>120 && jet1Pt>80 && jet7Pt>25 && meffInc>750" + Plateau_ele
#configMgr.cutsDict["SR7jTMu"]="AnalysisType==2 && met>180 && mt>120 && jet1Pt>80 && jet7Pt>25 && meffInc>750" + Plateau_muo

configMgr.cutsDict["SVEl"]="(lep1Pt<25 && lep2Pt<10 && met>180 && met<250 && mt>80 && mt<100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6)" + Plateau_met
configMgr.cutsDict["SVMu"]="(lep1Pt<20 && lep2Pt<10 && met>180 && met<250 && mt>80 && mt<100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7)" + Plateau_met

configMgr.cutsDict["SVWEl"]="lep1Pt<25 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6" + Plateau_met
configMgr.cutsDict["SVTEl"]="lep1Pt<25 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB3Jet>0  && jet1Pt>130 && jet2Pt>25 && AnalysisType==6" + Plateau_met
configMgr.cutsDict["SVWMu"]="lep1Pt<20 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7" + Plateau_met
configMgr.cutsDict["SVTMu"]="lep1Pt<20 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB3Jet>0  && jet1Pt>130 && jet2Pt>25 && AnalysisType==7" + Plateau_met

#configMgr.cutsDict["SSEl"]="lep1Pt < 25 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6" + Plateau_met
#configMgr.cutsDict["SSMu"]="lep1Pt < 20 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7" + Plateau_met

d=configMgr.cutsDict
#configMgr.cutsDict["SSElT"] = d["SSEl"]+"&& met/meff2Jet>0.3"
#configMgr.cutsDict["SSMuT"] = d["SSMu"]+"&& met/meff2Jet>0.3"
#To allow 1-bin and multi-bins channels based on same cuts
#configMgr.cutsDict["S2eeT"] = d["S2ee"] 
#configMgr.cutsDict["S2emT"] = d["S2em"] 
#configMgr.cutsDict["S2mmT"] = d["S2mm"] 
#configMgr.cutsDict["S4eeT"] = d["S4ee"] 
#configMgr.cutsDict["S4emT"] = d["S4em"] 
#configMgr.cutsDict["S4mmT"] = d["S4mm"] 


# Tuples of nominal weights without and with b-jet selection
configMgr.weights = ["genWeight","eventWeight","leptonWeight","triggerWeight","pileupWeight","pdfWeight","bTagWeight3Jet"]

# For weight-based systematics
bTagHighWeights = ["genWeight","eventWeight","leptonWeight","triggerWeight","pileupWeight","pdfWeight","bTagWeight3JetUp"]
bTagLowWeights = ["genWeight","eventWeight","leptonWeight","triggerWeight","pileupWeight","pdfWeight","bTagWeight3JetDown"]
    
# QCD weights without and with b-jet selection
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

#--------------------
# List of systematics
#--------------------

btagChanSyst = [Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")]
btagChanSyst = []

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

#for sam in [topSample, wzSample, bgSample, qcdSample, dataSample]:
#    sam.setFileList(bgdFiles)

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

bkgOnly = configMgr.addTopLevelXML("bkgOnly")
if useStat:
    bkgOnly.statErrThreshold=0.05 #0.03??
else:
    bkgOnly.statErrThreshold=None
bkgOnly.addSamples([topSample,wzSample,qcdSample,bgSample])
bkgOnly.addSamples([dataSample])

meas=bkgOnly.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.039)
meas.addPOI("mu_SIG")
meas.addParamSetting("mu_BG",True,1)

#-------------------------------------------------
# Constraining regions - statistically independent
#-------------------------------------------------
# nJet Binning for Top Control region
nJetTopeeBinLow = 2
nJetTopeeBinHigh = 10

nJetTopeBinLow = 3
nJetTopeBinHigh = 10

nJetTopseBinLow = 2
nJetTopseBinHigh = 8

nJetTopemBinLow = 2
nJetTopemBinHigh = 10

nJetTopmmBinLow = 2
nJetTopmmBinHigh = 10

nJetTopmBinLow = 3
nJetTopmBinHigh = 10

nJetTopsmBinLow = 2
nJetTopsmBinHigh = 8

# nJet Binning for W Control region
nJetZmmRegions = ["ZRmm"]
nJetZmmBinLow = 2
nJetZmmBinHigh = 10

nJetZmRegions = ["WRMu"]
nJetZmBinLow = 3
nJetZmBinHigh = 10

nJetZsmRegions = ["SVWMu"]
nJetZsmBinLow = 2
nJetZsmBinHigh = 8

nJetZeeRegions = ["ZRee"]
nJetZeeBinLow = 2
nJetZeeBinHigh = 10

nJetZeRegions = ["WREl"]
nJetZeBinLow = 3
nJetZeBinHigh = 10

nJetZseRegions = ["SVWEl"]
nJetZseBinLow = 2
nJetZseBinHigh = 8

ZptZmmRegions = ["ZRmm"]
ZptZmmNBins = 40
ZptZmmBinLow = 0
ZptZmmBinHigh = 1000

ZptZeeRegions = ["ZRee"]
ZptZeeNBins = 40
ZptZeeBinLow = 0
ZptZeeBinHigh = 1000

srNBins = 1
srBinLow = 0.5
srBinHigh = 1.5

##### nJet for Top ####
topChannels = []

if useDiLepCR:
    # ele ele
    nJetTopeeChannel=bkgOnly.addChannel("nJet",["TRee"],(nJetTopeeBinHigh-nJetTopeeBinLow),nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetTopeeChannel.setFileList(bgdFiles_ee)
    #  ele mu
    nJetTopemChannel=bkgOnly.addChannel("nJet",["TRem"],(nJetTopemBinHigh-nJetTopemBinLow),nJetTopemBinLow,nJetTopemBinHigh)
    nJetTopemChannel.setFileList(bgdFiles_em)
    # mu mu
    nJetTopmmChannel=bkgOnly.addChannel("nJet",["TRmm"],(nJetTopmmBinHigh-nJetTopmmBinLow),nJetTopmmBinLow,nJetTopmmBinHigh)
    nJetTopmmChannel.setFileList(bgdFiles_mm)
    
    topChannels += [nJetTopeeChannel,nJetTopemChannel,nJetTopmmChannel]

if useHardLepCR:
    #  single ele
    nJetTopeChannel=bkgOnly.addChannel("nJet",["TREl"],(nJetTopeBinHigh-nJetTopeBinLow),nJetTopeBinLow,nJetTopeBinHigh)
    nJetTopeChannel.setFileList(bgdFiles_e)
    # single mu
    nJetTopmChannel=bkgOnly.addChannel("nJet",["TRMu"],(nJetTopmBinHigh-nJetTopmBinLow),nJetTopmBinLow,nJetTopmBinHigh)
    nJetTopmChannel.setFileList(bgdFiles_m)

    topChannels += [nJetTopeChannel,nJetTopmChannel]

if useSoftLepCR:
    #  single soft ele
    nJetTopseChannel=bkgOnly.addChannel("nJet",["SVTEl"],(nJetTopseBinHigh-nJetTopseBinLow),nJetTopseBinLow,nJetTopseBinHigh)
    nJetTopseChannel.setFileList(bgdFiles_se)
    # soft single mu
    nJetTopsmChannel=bkgOnly.addChannel("nJet",["SVTMu"],(nJetTopsmBinHigh-nJetTopsmBinLow),nJetTopsmBinLow,nJetTopsmBinHigh)
    nJetTopsmChannel.setFileList(bgdFiles_sm)

    topChannels += [nJetTopseChannel,nJetTopsmChannel]

# add systematics
for chan in topChannels:
    chan.hasBQCD = True
    chan.useOverflowBin = False
    for syst in btagChanSyst:
        chan.addSystematic(syst)

####### nJet for W/Z  #######
WZChannels = []

if useDiLepCR:
    # ele ele    
    nJetZeeChannel=bkgOnly.addChannel("nJet",nJetZeeRegions,(nJetZeeBinHigh-nJetZeeBinLow),nJetZeeBinLow,nJetZeeBinHigh)
    nJetZeeChannel.setFileList(bgdFiles_ee)
    nJetZeeChannel.hasBQCD = False
    nJetZeeChannel.removeWeight("bTagWeight3Jet")
    # mu mu
    nJetZmmChannel=bkgOnly.addChannel("nJet",nJetZmmRegions,(nJetZmmBinHigh-nJetZmmBinLow),nJetZmmBinLow,nJetZmmBinHigh)
    nJetZmmChannel.setFileList(bgdFiles_mm)
    nJetZmmChannel.hasBQCD = False
    nJetZmmChannel.removeWeight("bTagWeight3Jet")

    WZChannels += [nJetZmmChannel,nJetZeeChannel]
    

if useHardLepCR:
    # single ele
    nJetZeChannel=bkgOnly.addChannel("nJet",nJetZeRegions,(nJetZeBinHigh-nJetZeBinLow),nJetZeBinLow,nJetZeBinHigh)
    nJetZeChannel.setFileList(bgdFiles_e)
    nJetZeChannel.hasBQCD = False
    [nJetZeChannel.addSystematic(syst) for syst in btagChanSyst]
    # single mu
    nJetZmChannel=bkgOnly.addChannel("nJet",nJetZmRegions,(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetZmChannel.setFileList(bgdFiles_m)
    nJetZmChannel.hasBQCD = False
    [nJetZmChannel.addSystematic(syst) for syst in btagChanSyst]

    WZChannels += [nJetZmChannel,nJetZeChannel]


if useSoftLepCR:    
    # single soft mu
    nJetZsmChannel=bkgOnly.addChannel("nJet",nJetZsmRegions,(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh)
    nJetZsmChannel.setFileList(bgdFiles_sm)
    nJetZsmChannel.hasB = True
    nJetZsmChannel.hasBQCD = False
    [nJetZsmChannel.addSystematic(syst) for syst in btagChanSyst]
    # single soft ele
    nJetZseChannel=bkgOnly.addChannel("nJet",nJetZseRegions,(nJetZseBinHigh-nJetZseBinLow),nJetZseBinLow,nJetZseBinHigh)
    nJetZseChannel.setFileList(bgdFiles_se)
    nJetZseChannel.hasB = True
    nJetZseChannel.hasBQCD = False
    [nJetZseChannel.addSystematic(syst) for syst in btagChanSyst]

    WZChannels += [nJetZsmChannel,nJetZseChannel]

# Additional settings
for chan in WZChannels:
    chan.hasBQCD = False    
    chan.useOverflowBin = False
        
bkgOnly.setBkgConstrainChannels(WZChannels+topChannels)

#-------------------------------------------------
# Signal regions - only do this if background only, add as validation regions! 
#-------------------------------------------------

# meffNBins = 1
# #    meffBinLow = 400.
# meffBinLow = 0.
# meffBinHigh = 1600.



meffNBinsTR = 20
meffBinLowTR = 0.
#meffBinLow = 0.
meffBinHighTR = 2000.


metNBinsTR = 40
metBinLowTR = 0.
#meffBinLow = 0.
metBinHighTR = 800.


pt1NBinsTR = 40
pt1BinLowTR = 0.
#meffBinLow = 0.
pt1BinHighTR = 800.


pt2NBinsTR = 40
pt2BinLowTR = 0.
#meffBinLow = 0.
pt2BinHighTR = 800.

if doValidationSlope:
    # check impact of kfactor fit on several distributions
    #TR
    validationSlopeTRChannels=[]
    validationSlopeTRChannels.append( bkgOnly.addValidationChannel("meffInc",["TRElVR"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validationSlopeTRChannels.append( bkgOnly.addValidationChannel("meffInc",["TRMuVR"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validationSlopeTRChannels.append( bkgOnly.addValidationChannel("met",["TRElVR2"],metNBinsTR,metBinLowTR,metBinHighTR) )
    validationSlopeTRChannels.append( bkgOnly.addValidationChannel("met",["TRMuVR2"],metNBinsTR,metBinLowTR,metBinHighTR) )
    validationSlopeTRChannels.append( bkgOnly.addValidationChannel("jet1Pt",["TRElVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR) )
    validationSlopeTRChannels.append( bkgOnly.addValidationChannel("jet1Pt",["TRMuVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR) )
    validationSlopeTRChannels.append( bkgOnly.addValidationChannel("jet2Pt",["TRElVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR) )
    validationSlopeTRChannels.append( bkgOnly.addValidationChannel("jet2Pt",["TRMuVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR) )
    # add systematics
    for chan in validationSlopeTRChannels:
        if chan.name.find("El")>-1:
            chan.setFileList(bgdFiles_e)
        else:
            chan.setFileList(bgdFiles_m)
        chan.hasBQCD = True
        chan.useOverflowBin = True
        for syst in btagChanSyst:
            chan.addSystematic(syst)
                    
    # WR
    validationSlopeWRChannels=[]
    validationSlopeWRChannels.append( bkgOnly.addValidationChannel("Wpt",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR) )
    validationSlopeWRChannels.append( bkgOnly.addValidationChannel("Wpt",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR) )
    validationSlopeWRChannels.append( bkgOnly.addValidationChannel("met",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR) )
    validationSlopeWRChannels.append( bkgOnly.addValidationChannel("met",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR) )
    # add systematics
    for chan in validationSlopeWRChannels:
        if chan.name.find("El")>-1:
            chan.setFileList(bgdFiles_e)
        else:
            chan.setFileList(bgdFiles_m)
        chan.hasBQCD = False
        chan.useOverflowBin = True
        for syst in btagChanSyst:
            chan.addSystematic(syst)

    #ZR
    validationSlopeZRChannels = []
    validationSlopeZRChannels.append( bkgOnly.addValidationChannel("Zpt",["ZRee"],metNBinsTR,metBinLowTR,metBinHighTR) )
    validationSlopeZRChannels.append( bkgOnly.addValidationChannel("Zpt",["ZRmm"],metNBinsTR,metBinLowTR,metBinHighTR) )
    # add systematics
    for chan in validationSlopeZRChannels:
        if chan.name.find("ee")>-1:
            chan.setFileList(bgdFiles_ee)
        else:
            chan.setFileList(bgdFiles_mm)
        chan.removeWeight("bTagWeight3Jet")
        chan.hasBQCD = False
        chan.useOverflowBin = True

##Hadronization in SRs as userHistoSys for exclusion fits
#Hard 1 lepton SR binning
meffNBins1lS3 = 6
meffBinLow1lS3 = 400.
meffBinHigh1lS3 = 1600.

meffNBins1lS4 = 4
meffBinLow1lS4 = 800.
meffBinHigh1lS4 = 1600.

#Dilepton SR binning
meffNBinsS2 = 5
meffBinLowS2 = 700.
meffBinHighS2 = 1700.

meffNBinsS4 = 5
meffBinLowS4 = 600.
meffBinHighS4 = 1600.

meffNBinsHL = 6
meffBinLowHL = 400.
#meffBinLow = 0.
meffBinHighHL = 1600.

"""
if doValidationSRLoose:
    #DILEPTONS
    meff2ee = bkgOnly.addValidationChannel("meffInc",["S2ee"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    meff2ee.setFileList(bgdFiles_ee)
    meff4ee = bkgOnly.addValidationChannel("meffInc",["S4ee"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    meff4ee.setFileList(bgdFiles_ee)
    meff2em = bkgOnly.addValidationChannel("meffInc",["S2em"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    meff2em.setFileList(bgdFiles_em)
    meff4em = bkgOnly.addValidationChannel("meffInc",["S4em"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    meff4em.setFileList(bgdFiles_em)
    meff2mm = bkgOnly.addValidationChannel("meffInc",["S2mm"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    meff2mm.setFileList(bgdFiles_mm)
    meff4mm = bkgOnly.addValidationChannel("meffInc",["S4mm"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    meff4mm.setFileList(bgdFiles_mm)
    # HARD LEPTON SRS
    meffS3_El=bkgOnly.addValidationChannel("meffInc",["S3El"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS3_El.setFileList(bgdFiles_e)
    meffS3_Mu=bkgOnly.addValidationChannel("meffInc",["S3Mu"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS3_Mu.setFileList(bgdFiles_m)
    meffS4_El=bkgOnly.addValidationChannel("meffInc",["S4El"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS4_El.setFileList(bgdFiles_e)
    meffS4_Mu=bkgOnly.addValidationChannel("meffInc",["S4Mu"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS4_Mu.setFileList(bgdFiles_m)
    # SOFT LEPTON SRS
    mmSSEl = bkgOnly.addValidationChannel("met/meff2Jet",["SSEl"],6,0.1,0.7)
    mmSSEl.setFileList(bgdFiles_se)
    mmSSMu = bkgOnly.addValidationChannel("met/meff2Jet",["SSMu"],6,0.1,0.7)
    mmSSMu.setFileList(bgdFiles_sm)

    validationSRChannels = [meff2ee, meff4ee, meff2em, meff4em, meff2mm, meff4mm, meffS3_El, meffS3_Mu, meffS4_El, meffS4_Mu, mmSSEl, mmSSMu]
    for chan in validationSRChannels:
        chan.useOverflowBin = True
        chan.removeWeight("bTagWeight3Jet")
"""

"""
if doValidationSRTight:
    #DILEPTONS
    meff2ee = bkgOnly.addValidationChannel("meffInc",["S2eeT"],1,meffBinLowS2,meffBinHighS2)
    meff2ee.setFileList(bgdFiles_ee)
    meff4ee = bkgOnly.addValidationChannel("meffInc",["S4eeT"],1,meffBinLowS4,meffBinHighS4)
    meff4ee.setFileList(bgdFiles_ee)
    meff2em = bkgOnly.addValidationChannel("meffInc",["S2emT"],1,meffBinLowS2,meffBinHighS2)
    meff2em.setFileList(bgdFiles_em)
    meff4em = bkgOnly.addValidationChannel("meffInc",["S4emT"],1,meffBinLowS4,meffBinHighS4)
    meff4em.setFileList(bgdFiles_em)
    meff2mm = bkgOnly.addValidationChannel("meffInc",["S2mmT"],1,meffBinLowS2,meffBinHighS2)
    meff2mm.setFileList(bgdFiles_mm)
    meff4mm = bkgOnly.addValidationChannel("meffInc",["S4mmT"],1,meffBinLowS4,meffBinHighS4)
    meff4mm.setFileList(bgdFiles_mm)
    # HARD LEPTON SRS
    meffS3T_El=bkgOnly.addValidationChannel("meffInc",["SR3jTEl"],1,1200,meffBinHighHL)
    meffS3T_El.setFileList(bgdFiles_e)
    meffS3T_Mu=bkgOnly.addValidationChannel("meffInc",["SR3jTMu"],1,1200,meffBinHighHL)
    meffS3T_Mu.setFileList(bgdFiles_m)
    meffS4T_El=bkgOnly.addValidationChannel("meffInc",["SR4jTEl"],1,800,meffBinHighHL)
    meffS4T_El.setFileList(bgdFiles_e)
    meffS4T_Mu=bkgOnly.addValidationChannel("meffInc",["SR4jTMu"],1,800,meffBinHighHL)
    meffS4T_Mu.setFileList(bgdFiles_m)
    # MULTIJETS SRS
    #meffS7T_El=bkgOnly.addValidationChannel("meffInc",["SR7jTEl"],1,750,meffBinHighHL)
    #meffS7T_El.setFileList(bgdFiles_e)
    #meffS7T_Mu=bkgOnly.addValidationChannel("meffInc",["SR7jTMu"],1,750,meffBinHighHL)
    #meffS7T_Mu.setFileList(bgdFiles_m)
    # SOFT LEPTON SRS
    mmSSElT = bkgOnly.addValidationChannel("met/meff2Jet",["SSElT"],1,0.3,0.7)
    mmSSElT.setFileList(bgdFiles_se)
    mmSSMuT = bkgOnly.addValidationChannel("met/meff2Jet",["SSMuT"],1,0.3,0.7)
    mmSSMuT.setFileList(bgdFiles_sm)

    validationSRChannels = [meff2ee, meff4ee, meff2em, meff4em, meff2mm, meff4mm, meffS3T_El, meffS3T_Mu, meffS4T_El, meffS4T_Mu, mmSSElT, mmSSMuT]
    for chan in validationSRChannels:
        chan.useOverflowBin = True
        chan.removeWeight("bTagWeight3Jet")

"""

if doValidationDilep:
    validation2LepChannels = []
    validation2LepChannels.append( bkgOnly.addValidationChannel("meffInc",["VR4ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("meffInc",["VR4em"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("meffInc",["VR4mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("nJet",["VR4ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("nJet",["VR4em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("nJet",["VR4mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("meffInc",["VR2ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("meffInc",["VR2em"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("meffInc",["VR2mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("nJet",["VR2ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("nJet",["VR2em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("nJet",["VR2mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("meffInc",["VR3ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("meffInc",["VR3em"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("meffInc",["VR3mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("nJet",["VR3ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("nJet",["VR3em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepChannels.append( bkgOnly.addValidationChannel("nJet",["VR3mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    # add systematics
    for chan in validation2LepChannels:
        chan.useOverflowBin = True
        chan.removeWeight("bTagWeight3Jet")
        if chan.name.endswith("ee"):
            chan.setFileList(bgdFiles_ee)
        elif chan.name.endswith("em"):
            chan.setFileList(bgdFiles_em)
        elif chan.name.endswith("mm"):
            chan.setFileList(bgdFiles_mm)
        else:
            raise RuntimeError("Unexpected channel name: %s"%(chan.name))

    
if doValidationDilepZ:
    validation2LepZChannels=[]
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR4ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR4em"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR4mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR4NoBselem"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR4ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR4em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR4mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR4NoBselem"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR2ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR2em"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR2mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR2NoBselem"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR2ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR2em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR2mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR2NoBselem"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR3ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR3em"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR3mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("meffInc",["VZR3NoBselem"],meffNBinsTR,meffBinLowTR,meffBinHighTR) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR3ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR3em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR3mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    validation2LepZChannels.append( bkgOnly.addValidationChannel("nJet",["VZR3NoBselem"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh) )
    # add systematics
    for chan in validation2LepZChannels:
        chan.hasBQCD = False
        chan.useOverflowBin = True
        if chan.name.endswith("ee"):
            chan.setFileList(bgdFiles_ee)
        elif chan.name.endswith("em"):
            chan.setFileList(bgdFiles_em)
        elif chan.name.endswith("mm"):
            chan.setFileList(bgdFiles_mm)
        else:
            raise RuntimeError("Unexpected channel name: %s"%(chan.name))
    

if doValidationSoftLep:
    validationSoftLepChannels = []
    validationSoftLepBtagChannels = []
    validationSoftLepBvetoChannels = []
    validationSoftLepChannels.append( bkgOnly.addValidationChannel("nJet",["SVEl"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh) )
    validationSoftLepChannels.append( bkgOnly.addValidationChannel("nJet",["SVMu"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh) )
    # add systematics
    for chan in validationSoftLepChannels:
        chan.useOverflowBin = True
        chan.removeWeight("bTagWeight3Jet")

    if not useSoftLepCR:
        validationSoftLepBvetoChannels.append( bkgOnly.addValidationChannel("nJet",["SVWEl"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh) )
        validationSoftLepBvetoChannels.append( bkgOnly.addValidationChannel("nJet",["SVWMu"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh) )
        validationSoftLepBtagChannels.append( bkgOnly.addValidationChannel("nJet",["SVTEl"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh) )
        validationSoftLepBtagChannels.append( bkgOnly.addValidationChannel("nJet",["SVTMu"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh) )
        # add systematics
        for chan in validationSoftLepBtagChannels:
            chan.hasBQCD = True
            chan.useOverflowBin = True
            for syst in btagChanSyst:
                chan.addSystematic(syst)
                pass

        # add systematics
        for chan in validationSoftLepBvetoChannels:
            chan.hasBQCD = False
            chan.useOverflowBin = True
            for syst in btagChanSyst:
                chan.addSystematic(syst)
                pass
            pass
        pass
    
    for chan in validationSoftLepChannels+validationSoftLepBtagChannels+validationSoftLepBvetoChannels:
        if chan.name.find("El")>-1:
            chan.setFileList(bgdFiles_se)
        else:
            chan.setFileList(bgdFiles_sm)

